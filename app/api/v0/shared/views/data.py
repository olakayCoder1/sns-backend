from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *

# Create your views here.

class GetRoleAPI(APIView):
    
    def get(self, request):
    
        try:
            m_data = Role.objects.all()
            serializer = RoleSerializer(m_data, many=True)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetIMAPAPI(APIView):
    
    def get(self, request):
    
        try:
            m_data = IMAP.objects.all()
            serializer = IMAPSerializer(m_data, many=True)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetStatusAPI(APIView):
    
    def get(self, request):
    
        try:
            m_data = Status.objects.all()
            serializer = StatusSerializer(m_data, many=True)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)



class GetPropertyAPI(APIView):
    
    def get(self, request):
    
        try:
            m_data = Property.objects.all()
            serializer = PropertySerializer(m_data, many=True)

            return Response(serializer.data, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetDomainAPI(APIView):
    
    def get(self, request):
    
        try:
            m_data = MailDomain.objects.all()

            return Response([
                {
                    "id": data.id,
                    "name": data.username
                } for data in m_data
            ], status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)

