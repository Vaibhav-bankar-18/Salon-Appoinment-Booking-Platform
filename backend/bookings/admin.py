from django.contrib import admin

from .models import Booking, Service, Slot

admin.site.register(Service)
admin.site.register(Slot)
admin.site.register(Booking)
