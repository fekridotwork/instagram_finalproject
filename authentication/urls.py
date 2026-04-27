from django.urls import path
from .views import RequestOTPAPIView, VerifyOTPAPIView

urlpatterns = [
    path("request-otp/", RequestOTPAPIView.as_view(), name="request_otp"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
]