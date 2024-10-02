

from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import *
from django.db.models import *
from django.db import transaction

from ..serializers import *
from db_schema.models import *
from db_schema.serializers import *
from validations.mail import *

class GetSentMailsAPI(APIView):
    permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]

    def get(self, request):
        try:
            domain = request.GET.get('domain', "")
            page = int(request.GET.get('page', 1))
            pageSize = int(request.GET.get('pageSize', 20))

            # get incoming mails according to customers
            role = get_role(request.user)
            m_mails = Mail.objects.filter(outgoing=True, domain=domain)
            
            m_mails = m_mails.filter(managers=request.user)
            
            m_mails = m_mails.order_by('-processed')

            serializer = MailSerializer(m_mails[(page-1)*pageSize : page*pageSize] , many=True)

            return Response({
                "data": serializer.data,
                "total": m_mails.count()
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetSentMailAPI(APIView):
    permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]

    def get(self, request, mail_id):
        try:
            role = get_role(request.user)

            m_mail = Mail.objects.filter(id=mail_id)
            if role == "member":
                m_mail = m_mail.filter(managers=request.user)

            m_mail = m_mail.first()
            if m_mail is None:
                raise Exception("Mail not found")
            
            serializer = MailSerializer(m_mail)

            return Response({
                "data": [serializer.data],
                "total": 1
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)

   