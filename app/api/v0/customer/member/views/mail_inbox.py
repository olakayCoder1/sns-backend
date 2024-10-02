

from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import *
from django.db.models import *
from django.db import transaction

from ..serializers import *
from db_schema.models import *
from db_schema.serializers import *
from datetime import datetime
from validations.mail import *


class GetInboxMailsAPI(APIView):
    permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]

    def get(self, request):
        try:
            domain = request.GET.get('domain', "")
            page = int(request.GET.get('page', 1))
            pageSize = int(request.GET.get('pageSize', 20))

            # get incoming mails according to customers
            m_customer_ids = Mail.objects.filter(domain=domain, outgoing=False).values_list('customers', flat=True)

            m_customers = Customer.objects.filter(id__in=m_customer_ids)
            
            role = get_role(request.user)
            if role == "member":
                m_customers = m_customers.filter(manager=request.user)
            
            m_customers = m_customers.order_by('-last_contacted')
            
            serializer = MailInboxSerializer(m_customers[(page-1)*pageSize : page*pageSize], context={"domain": domain} , many=True)

            message_total = Mail.objects.filter(domain=domain)

            if role == "member":
                message_total = message_total.filter(customers__manager=request.user)

            message_unread = message_total.filter(outgoing=False, read=None)

            return Response({
                "data": serializer.data,
                "total": m_customers.count(),
                "message_unread": message_unread.count(),
                "message_total": message_total.count()
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetMailsByCustomer(APIView):
    permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]

    def get(self, request, domain, customer_id):
        try:
            m_customer = Customer.objects.filter(id=customer_id)

            role = get_role(request.user)
            if role == "member":
                m_customer = m_customer.filter(manager=request.user)
                
            m_customer = m_customer.first()
            if m_customer is None:
                raise Exception("Customer not found")
            
            m_mails = Mail.objects.filter(customers=m_customer, domain=domain).order_by('processed')
            serializer = MailSerializer(m_mails, many=True)

            for mail in m_mails:
                for attach in mail.attachments.all():
                    print(attach.document.url)

            return Response({
                "data": serializer.data,
                "total": m_mails.count(),
                "customer": CustomerSerializer(m_customer).data
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


     
class MakeMailAsRead(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, mail_id):
        try:
            m_mail = Mail.objects.filter(id=mail_id, managers=request.user).first()
            if m_mail is None:
                raise Exception("Mail not found")

            with transaction.atomic():
                if m_mail.read is None:
                    m_mail.read = datetime.now()
                    m_mail.save()
                    
            return Response({}, status=200)
        
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        
