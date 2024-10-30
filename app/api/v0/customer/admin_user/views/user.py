from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import *
from django.db import transaction
from django.contrib.auth.hashers import check_password, make_password
import time
from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.user import *
from mail.account_activate import *

# Create your views here.
class GetUsersAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def get(self, request):
        
        
        keyword = request.GET.get('keyword', '')
        page = int(request.GET.get('page', 1))
        pageSize = int(request.GET.get('pageSize', 10))

        try:
            m_data = User.objects.filter(Q(user_info__name__contains=keyword) | Q(email__contains=keyword), Q(permission="customer"), Q(is_active=True)).order_by('id')
            serializer = UserSerializer(m_data[pageSize * (page - 1):pageSize * page], many=True)

            return Response({
                "data": serializer.data,
                "total": m_data.count()
            })
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class CreateUserAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def post(self, request):
        
        try:
            errors, status, clean_data = validate_create_user(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                user_info = UserInfo.objects.create(
                    name = clean_data["last_name"] + " " + clean_data["first_name"],
                    last_name=clean_data["last_name"],
                    first_name=clean_data["first_name"],
                    name_furi = clean_data["last_name_furi"] + " " + clean_data["first_name_furi"],
                    last_name_furi=clean_data["last_name_furi"],
                    first_name_furi=clean_data["first_name_furi"],
                    phone=clean_data["phone"],
                    role=Role.objects.get(id=clean_data["role"])
                )
                user = User.objects.create(
                    email=clean_data["email"],
                    password='',
                    user_info=user_info,
                    permission="customer",
                    is_active=False,
                    is_allowed=clean_data['is_allowed']
                )

                # ※登録後、担当にメールが送信されます。メール内のURLからアカウントの有効化を行ってください。
                send_mail(request, clean_data["email"])
                
                serializer = UserSerializer(user)

                return Response({
                    "data": serializer.data,
                    "msg": "登録しました。"
                }, status=200)
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class UpdateUserAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            
            serializer = UserFlatSerializer(user.user_info)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(str(e))
            return Response("Can't find", status=404)
        
    def patch(self, request, user_id):
        try:
            errors, status, clean_data = validate_update_user(request, user_id)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                user.email = clean_data["email"]
                user.is_allowed = clean_data["is_allowed"]
                user.user_info.name = clean_data["last_name"] + " " + clean_data["first_name"]
                user.user_info.last_name = clean_data["last_name"]
                user.user_info.first_name = clean_data["first_name"]
                user.user_info.name_furi = clean_data["last_name_furi"] + " " + clean_data["first_name_furi"]
                user.user_info.last_name_furi = clean_data["last_name_furi"]
                user.user_info.first_name_furi = clean_data["first_name_furi"]
                user.user_info.phone = clean_data["phone"]
                user.user_info.role = Role.objects.get(id=clean_data["role"])
                user.save()
                user.user_info.save()
                
                serializer = UserSerializer(user)

                return Response({
                    "data": serializer.data,
                    "msg": "更新しました。"
                }, status=200)

        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()

            return Response({
                "msg": "削除しました。"
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        