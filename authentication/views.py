from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import generate_otp_code, store_otp

from .serializers import RequestOTPSerializer

# class RequestOTPAPIView(APIView):
#     def post(self, request):
#         identifier = request.data.get('identifier')
#         purpose = request.data.get('purpose')
#
#         code = generate_otp_code()
#         store_otp(identifier, purpose, code)
#
#         return Response({"message": "OTP sent successfully"})

class RequestOTPAPIView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data['identifier']
        purpose = serializer.validated_data['purpose']

        code = generate_otp_code()
        store_otp(identifier, purpose, code)

        return Response({"message": "OTP sent successfully"})
