

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from utils.permissions import *
from django.db.models import *
from django.db import transaction

from mail.mailbox import send_email_task
from django_mailbox.models import MessageAttachment

from db_schema.models import *
from db_schema.serializers import *
from validations.mail import *

class CreateMailAPI(APIView):
    permission_classes = [IsCustomer]


    def post(self, request):
        try:
            errors, status, clean_data = validate_create_mail(request)

            if status != 200:
                return Response({"errors": errors}, status=status)

            recipients = Customer.objects.filter(id__in=clean_data['recipients'])
            send_email_task(request.user.id, [r.id for r in recipients], clean_data)
            
            return Response({
                "msg": "メールを送信しました。"
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        

class CreateGroupMailAPI(APIView):
    permission_classes = [IsCustomer]


    def post(self, request):
        try:
            errors, status, clean_data = validate_create_group_mail(request)

            if status != 200:
                return Response({"errors": errors}, status=status)

            if clean_data['group_type'] == "status":
                recipients = Customer.objects.filter(status=Status.objects.get(id=clean_data['group']))
                
            if clean_data['group_type'] == "property":
                recipients = Customer.objects.filter(property=Property.objects.get(id=clean_data['group']))
                
                
            send_email_task(request.user.id, [r.id for r in recipients], clean_data)

            return Response({
                "msg": "メールを送信しました。"
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        

class CreateAttachmentFileView(APIView):
    # permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
    
        try:
            if request.data['file'] is None:
                return Response({"msg": "File is required"}, status=400)
            
            with transaction.atomic():
                # get Content-Type from the file
                file = request.data['file']

                headers = f"""Content-Type: {file.content_type}; name="{file.name}"
                Content-Disposition: attachment; filename="{file.name}"
                Content-Transfer-Encoding: base64"""

                m_attach = MessageAttachment.objects.create(
                    document=request.data['file'],
                    headers=headers
                )
        
            return Response(MessageAttachmentSerializer(m_attach).data, status=200)
        
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
