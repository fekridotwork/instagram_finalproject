from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import (
    generate_otp_code, 
    store_otp, 
    verify_otp, 
    get_user_by_identifier,
    user_exists_by_identifier,
    create_user_by_identifier,
    get_otp_cooldown_remaining,
    set_otp_cooldown,
    OTPTooManyAttemptsError
)

from .serializers import RequestOTPSerializer, VerifyOTPSerializer, LogoutSerializer

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from rest_framework.permissions import IsAuthenticated

from django.conf import settings

from .tasks import send_otp_task


class RequestOTPAPIView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        purpose = serializer.validated_data['purpose']

        user_exists = user_exists_by_identifier(identifier)

        if purpose == "register" and user_exists:
            return Response(
                {"error": "User with this identifier already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if purpose == "login" and not user_exists:
            return Response(
                {"error": "User with this identifier does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cooldown_remaining = get_otp_cooldown_remaining(identifier, purpose)

        if cooldown_remaining > 0:
            return Response(
                {
                    "error": f"Try again in {cooldown_remaining} seconds.",
                    "retry_after": cooldown_remaining,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        code = generate_otp_code()
        store_otp(identifier, purpose, code)

        set_otp_cooldown(identifier,purpose)

        send_otp_task.delay(identifier, purpose, code)

        data = {
            "message": "OTP sent successfully",
        }
        if settings.DEBUG:
            data["code"] = code

        return Response(data, status=status.HTTP_200_OK)

class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        purpose = serializer.validated_data['purpose']
        code = serializer.validated_data['code']

        try:
            is_valid = verify_otp(identifier, purpose, code)
        except OTPTooManyAttemptsError:
            return Response(
                {"error": "Too many failed attempts. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if not is_valid:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if purpose == "register":
            if user_exists_by_identifier(identifier):
                return Response(
                    {"error": "User with this identifier already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = create_user_by_identifier(identifier)
            is_new_user = True

        elif purpose == "login":
            user = get_user_by_identifier(identifier)

            if user is None:
                return Response(
                    {"error": "User with this identifier does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            is_new_user = False
        refresh = RefreshToken.for_user(user)

        return Response(
            {"message": "OTP verified successfully",
            "is_new_user": is_new_user,
             "access": str(refresh.access_token),
             "refresh": str(refresh),
             },
        status=status.HTTP_200_OK)

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "phone_number": request.user.phone_number,
        })

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "Logged out successfully",})
