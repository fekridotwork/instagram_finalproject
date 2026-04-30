from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileSerializer

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)