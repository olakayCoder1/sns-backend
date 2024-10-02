from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.mail_template import *

# Create your views here.
class GetMailTemplatesAPI(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request):
        keyword = request.GET.get('keyword', '')
        page = int(request.GET.get('page', 1))
        pageSize = int(request.GET.get('pageSize', 10))

        try:
            m_data = MailTemplate.objects.filter(Q(subject__contains=keyword) | Q(body__contains=keyword)).order_by('id')
            serializer = MailTemplateSerializer(m_data[pageSize * (page - 1):pageSize * page], many=True)

            return Response({
                "data": serializer.data,
                "total": m_data.count()
            })
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        

class CreateMailTemplateAPI(APIView):
    permission_classes = [IsCustomer]
    
    def post(self, request):
        
        try:
            errors, status, clean_data = validate_mail_template(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                mail_template = MailTemplate.objects.create(
                    publisher = request.user,
                    subject=clean_data["subject"],
                    body=clean_data["body"]
                )
                
                return Response({
                    "msg": "作成しました。",
                    "data": MailTemplateSerializer(mail_template).data
                }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        

class UpdateMailTemplateAPI(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, mail_template_id):
        try:
            mail_template = MailTemplate.objects.filter(id=mail_template_id).first()
            
            if mail_template is None:
                raise Exception("メールテンプレートが見つかりません")
            
            serializer = MailTemplateSerializer(mail_template)
            return Response(serializer.data)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
    
    def patch(self, request, mail_template_id):
        
        try:
            errors, status, clean_data = validate_mail_template(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                mail_template = MailTemplate.objects.filter(id=mail_template_id).first()
                
                if mail_template is None:
                    raise Exception("メールテンプレートが見つかりません")

                mail_template.subject = clean_data["subject"]
                mail_template.body = clean_data["body"]
                mail_template.save()
                
                # in japanese
                return Response({
                    "msg": "更新しました。",
                    "data": MailTemplateSerializer(mail_template).data
                }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
        
    def delete(self, request, mail_template_id):
        try:
            mail_template = MailTemplate.objects.filter(id=mail_template_id).first()
            
            if mail_template is None:
                raise Exception("メールテンプレートが見つかりません")
            
            mail_template.delete()
            return Response("OK", status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)