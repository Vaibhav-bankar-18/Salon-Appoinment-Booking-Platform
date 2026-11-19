from django.conf import settings
from django.db import models
from django.db.models import Q


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Slot(models.Model):
    """A bookable time window offered by one staff member for one service."""
    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="slots")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="slots")
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ["start"]
        constraints = [models.UniqueConstraint(fields=["staff", "start"], name="unique_staff_start")]

    def __str__(self):
        return f"{self.service} with {self.staff} at {self.start:%d %b %H:%M}"


class Booking(models.Model):
    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-slot__start"]
        constraints = [
            # Database-level guard against double booking: only one active booking per slot.
            models.UniqueConstraint(
                fields=["slot"], condition=Q(status="booked"), name="one_active_booking_per_slot"
            )
        ]

    def __str__(self):
        return f"{self.customer} -> {self.slot} ({self.status})"
