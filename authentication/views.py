from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import generate_otp_code, store_otp, verify_otp, get_or_create_user_by_identifier

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

        code = generate_otp_code()
        store_otp(identifier, purpose, code)

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

        is_valid = verify_otp(identifier, purpose, code)

        if not is_valid:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST)
        user, created = get_or_create_user_by_identifier(identifier)
        refresh = RefreshToken.for_user(user)
        return Response(
            {"message": "OTP verified successfully",
            "is_new_user": created,
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
