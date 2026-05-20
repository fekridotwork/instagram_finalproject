from django.urls import path

from .views import (LogoutAPIView, MeAPIView, RequestOTPAPIView,
                    VerifyOTPAPIView)

urlpatterns = [
    path("request-otp/", RequestOTPAPIView.as_view(), name="request_otp"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    path("me/", MeAPIView.as_view(), name="auth-me"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]