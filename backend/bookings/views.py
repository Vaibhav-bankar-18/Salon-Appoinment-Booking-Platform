from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsCustomer, IsCustomerOrAdmin, IsStaffOrAdmin

from .models import Booking, Service, Slot
from .serializers import BookingSerializer, ServiceSerializer, SlotSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.action in ("list", "retrieve") else [IsAdmin()]

    def get_queryset(self):
        qs = Service.objects.all().order_by("name")
        return qs if self.request.user.role == "admin" else qs.filter(active=True)


class SlotViewSet(viewsets.ModelViewSet):
    """Customers see only future, unbooked slots. Staff see their own. Admin sees all."""
    serializer_class = SlotSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated()] if self.action in ("list", "retrieve") else [IsStaffOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        qs = Slot.objects.select_related("staff", "service").annotate(
            is_booked=Exists(Booking.objects.filter(slot=OuterRef("pk"), status=Booking.Status.BOOKED))
        )
        if user.role == "customer":
            qs = qs.filter(start__gt=timezone.now(), is_booked=False, service__active=True)
        elif user.role == "staff":
            qs = qs.filter(staff=user)
        day = parse_date(self.request.query_params.get("date", ""))
        if day:
            qs = qs.filter(start__date=day)
        service = self.request.query_params.get("service")
        if service and service.isdigit():
            qs = qs.filter(service_id=service)
        return qs

    def perform_destroy(self, instance):
        if instance.bookings.filter(status=Booking.Status.BOOKED).exists():
            raise ValidationError({"detail": "This slot has a booking. Cancel the booking first."})
        instance.delete()


class BookingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsCustomer()]
        if self.action == "cancel":
            return [IsCustomerOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related("slot__service", "slot__staff", "customer")
        if user.role == "customer":
            qs = qs.filter(customer=user)
        elif user.role == "staff":
            qs = qs.filter(slot__staff=user)
        return qs

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                slot = Slot.objects.select_for_update().get(pk=request.data.get("slot"))
                if slot.start <= timezone.now():
                    return Response({"detail": "This slot has already started."}, status=400)
                if slot.bookings.filter(status=Booking.Status.BOOKED).exists():
                    return Response({"detail": "This slot was just taken. Pick another one."}, status=409)
                booking = Booking.objects.create(customer=request.user, slot=slot)
        except (Slot.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Slot not found."}, status=404)
        except IntegrityError:
            return Response({"detail": "This slot was just taken. Pick another one."}, status=409)
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.BOOKED:
            return Response({"detail": "This booking is already cancelled."}, status=400)
        cutoff = timedelta(hours=settings.CANCEL_CUTOFF_HOURS)
        if request.user.role != "admin" and booking.slot.start - timezone.now() < cutoff:
            return Response(
                {"detail": f"Cancellations close {settings.CANCEL_CUTOFF_HOURS} hours before the appointment."},
                status=400)
        booking.status = Booking.Status.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=["status", "cancelled_at"])
        return Response(self.get_serializer(booking).data)
