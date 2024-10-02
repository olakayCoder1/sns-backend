from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
from utils.permissions import IsAuthenticated
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *

# Create your views here.
class GetNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        if request.user.permission == "customer":
            return Response({
                "total": 0,
            })
        else:
            return Response({
                "total": 0,
            })
    
    