from django.shortcuts import render
from rest_framework.permissions import AllowAny
from  rest_framework.response import Response
from  rest_framework.views import APIView

class HealthCheckView(APIView):
    # 覆盖 GlobalAutoPermission
    permission_classes = [AllowAny]
    # 禁用认证
    authentication_classes = []
    def get(self, request):
        return Response({"code": 200})