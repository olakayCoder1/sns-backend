import logging
import traceback
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
from utils.permissions import IsAuthenticated
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from validations.auth.profile import *

# Create your views here.
class GetMyAccountInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"me": serializer.data})
    
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):

        
        
        try:
            serializer = UserFlatSerializer(request.user.user_info)

            return Response(serializer.data, 200)

        except Exception as e:
            print(str(e))
            return Response({"msg": "Can't find User Info"}, status=404)
    
    def post(self, request):
        print(request.data)
        
        try:
            errors, status, clean_data = validate_profile(request)
            if status != 200:
                return Response({"errors": errors}, status=status)    
            
            with transaction.atomic():
                m_user = User.objects.get(id=request.user.id)
                m_user.email = clean_data['email']
                m_user.save()

                m_user.user_info.last_name = clean_data['last_name']
                m_user.user_info.first_name = clean_data['first_name']
                m_user.user_info.last_name_furi = clean_data['last_name_furi']
                m_user.user_info.first_name_furi = clean_data['first_name_furi']
                m_user.user_info.name = clean_data['last_name'] + " " + clean_data['first_name']
                m_user.user_info.name_furi = clean_data['last_name_furi'] + " " + clean_data.get('first_name_furi') if clean_data.get('first_name_furi') else ''
                m_user.user_info.phone = clean_data['phone']
                m_user.user_info.save()

                return Response({
                    "msg": "プロフィール情報が正常に更新されました。"
                })
        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            return Response({"msg": str(e)}, status=400)