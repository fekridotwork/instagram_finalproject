from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import generate_otp_code, store_otp, verify_otp, get_or_create_user_by_identifier

from .serializers import RequestOTPSerializer, VerifyOTPSerializer


class RequestOTPAPIView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        purpose = serializer.validated_data['purpose']

        code = generate_otp_code()
        store_otp(identifier, purpose, code)

        return Response({"message": "OTP sent successfully",
                        "code": code,
        })

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
        return Response(
            {"message": "OTP verified successfully",
            "is_new_user": created,
             })
