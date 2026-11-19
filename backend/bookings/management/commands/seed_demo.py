from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from bookings.models import Service, Slot


class Command(BaseCommand):
    help = "Create demo users, services and upcoming slots."

    def handle(self, *args, **opts):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "Admin@12345")
        staff, _ = User.objects.get_or_create(username="priya", defaults={"role": "staff", "first_name": "Priya"})
        staff.set_password("Staff@12345"); staff.role = "staff"; staff.save()
        if not User.objects.filter(username="demo").exists():
            User.objects.create_user("demo", "demo@example.com", "Demo@12345", first_name="Demo")
        services = [Service.objects.get_or_create(name=n, defaults={"duration_minutes": d, "price": p})[0]
                    for n, d, p in [("Haircut", 30, 300), ("Facial", 60, 800), ("Manicure", 45, 500)]]
        for day in range(1, 4):
            date = timezone.localdate() + timedelta(days=day)
            for hour in range(10, 17):
                service = services[hour % 3]
                start = timezone.make_aware(datetime.combine(date, time(hour)))
                Slot.objects.get_or_create(staff=staff, start=start, defaults={
                    "service": service, "end": start + timedelta(minutes=service.duration_minutes)})
        self.stdout.write(self.style.SUCCESS(
            "Seeded. Logins: admin/Admin@12345, priya/Staff@12345, demo/Demo@12345"))
