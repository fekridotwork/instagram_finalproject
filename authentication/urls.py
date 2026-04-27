from django.urls import path
from .views import RequestOTPAPIView

urlpatterns = [
    path("request-otp/", RequestOTPAPIView.as_view(), name="request_otp"),
]