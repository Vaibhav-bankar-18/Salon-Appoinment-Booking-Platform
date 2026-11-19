from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import MeView, RegisterView
from bookings.views import BookingViewSet, ServiceViewSet, SlotViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("slots", SlotViewSet, basename="slot")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", MeView.as_view()),
    path("api/", include(router.urls)),
]
