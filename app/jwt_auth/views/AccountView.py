from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import *
from django.db.models import Q
from django.db import transaction

# Generate token and generate reset url
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator

from validations.auth.password import *
from mail.auth.password import *
import datetime


class AccountActivateAPI(APIView):

    def get(self, request):
        token = request.query_params.get('token', "")

        try:
            print(token)
            if RegisterToken.objects.filter(token=token).exists() == False:
                return Response("invalid token", status=404)
            
            m_item = RegisterToken.objects.get(token=token)
            m_user = User.objects.get(id=m_item.user_id)
            rslt = default_token_generator.check_token(m_user, token)
            
            if rslt:
                if m_item.expire_at.date() > datetime.datetime.now().date():
                    return Response("success", status=200)
                else:
                    return Response("token has expired", status=400)
            else:
                return Response("invalid token", status=404)
            
        except Exception as e:
            print(str(e))
            return Response("invalid token", status=404)
        
    def post(self, request):
        data = dict(request.data)
        token = data.get("token", "")

        try:
            if RegisterToken.objects.filter(token=token).exists() == False:
                return Response({"msg": "無効なトークンです。"}, status=400)
            
            m_item = RegisterToken.objects.get(token=token)
            m_user = User.objects.get(id=m_item.user.id)

            if default_token_generator.check_token(m_user, token) == False or m_item.expire_at.date() < datetime.datetime.now().date():
                return Response({"msg": "無効なトークンです。"}, status=400)

            errors, status, clean_data = validate_reset_password(request)
            if status != 200:
                return Response({"errors": errors}, status=status)

            with transaction.atomic():
                m_user.password = make_password(clean_data["new_password"])
                m_user.is_active = True
                m_user.save()
                m_item.delete()

            return Response({"msg": "アカウントが有効になりました。"}, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)