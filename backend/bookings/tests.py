from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User

from .models import Booking, Service, Slot


class BookingTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user("s", password="x", role="staff")
        self.c1 = User.objects.create_user("c1", password="x")
        self.c2 = User.objects.create_user("c2", password="x")
        self.service = Service.objects.create(name="Cut", duration_minutes=30, price=100)
        self.slot = self._slot(timedelta(days=1))

    def _slot(self, delta):
        start = timezone.now() + delta
        return Slot.objects.create(staff=self.staff, service=self.service, start=start,
                                   end=start + timedelta(minutes=30))

    def book(self, user, slot=None):
        self.client.force_authenticate(user)
        return self.client.post("/api/bookings/", {"slot": (slot or self.slot).id})

    def test_booking_hides_slot_from_other_customers(self):
        self.assertEqual(self.book(self.c1).status_code, 201)
        self.client.force_authenticate(self.c2)
        self.assertEqual(self.client.get("/api/slots/").json(), [])

    def test_double_booking_is_rejected(self):
        self.book(self.c1)
        self.assertEqual(self.book(self.c2).status_code, 409)
        self.assertEqual(Booking.objects.filter(status="booked").count(), 1)

    def test_cancel_frees_slot(self):
        booking_id = self.book(self.c1).json()["id"]
        res = self.client.post(f"/api/bookings/{booking_id}/cancel/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.book(self.c2).status_code, 201)

    def test_cancel_blocked_inside_cutoff(self):
        soon = self._slot(timedelta(hours=1))
        booking_id = self.book(self.c1, soon).json()["id"]
        self.assertEqual(self.client.post(f"/api/bookings/{booking_id}/cancel/").status_code, 400)

    def test_customer_cannot_create_slots(self):
        self.client.force_authenticate(self.c1)
        res = self.client.post("/api/slots/", {"service": self.service.id,
                               "start": (timezone.now() + timedelta(days=2)).isoformat()})
        self.assertEqual(res.status_code, 403)
