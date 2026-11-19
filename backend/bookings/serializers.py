from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from accounts.models import User

from .models import Booking, Service, Slot


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "duration_minutes", "price", "active"]


class SlotSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="staff"), required=False)
    staff_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source="service.name", read_only=True)
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Slot
        fields = ["id", "staff", "staff_name", "service", "service_name", "start", "end", "is_booked"]
        read_only_fields = ["end"]

    def get_staff_name(self, obj):
        return obj.staff.get_full_name() or obj.staff.username

    def get_is_booked(self, obj):
        return getattr(obj, "is_booked", False)

    def validate(self, attrs):
        user = self.context["request"].user
        if user.role == "staff":
            attrs["staff"] = user
        elif "staff" not in attrs:
            raise serializers.ValidationError({"staff": "Choose a staff member."})
        start = attrs["start"]
        if start <= timezone.now():
            raise serializers.ValidationError({"start": "Slot must start in the future."})
        end = start + timedelta(minutes=attrs["service"].duration_minutes)
        if Slot.objects.filter(staff=attrs["staff"], start__lt=end, end__gt=start).exists():
            raise serializers.ValidationError({"start": "This overlaps another slot for this staff member."})
        attrs["end"] = end
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="slot.service.name", read_only=True)
    staff_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    start = serializers.DateTimeField(source="slot.start", read_only=True)
    end = serializers.DateTimeField(source="slot.end", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "slot", "service_name", "staff_name", "customer_name",
                  "start", "end", "status", "created_at", "cancelled_at"]

    def get_staff_name(self, obj):
        return obj.slot.staff.get_full_name() or obj.slot.staff.username

    def get_customer_name(self, obj):
        return obj.customer.get_full_name() or obj.customer.username
