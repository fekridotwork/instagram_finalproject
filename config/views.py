from rest_framework.response import Response
from rest_framework.views import APIView

from .schemas import health_check_schema


@health_check_schema
class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({'status': 'ok'})