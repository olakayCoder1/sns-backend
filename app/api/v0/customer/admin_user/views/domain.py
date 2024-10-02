from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import *
from django.db import transaction
from django.core.mail import EmailMessage, get_connection

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.domain import *

# Create your views here.
class GetDomainsAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def get(self, request):
        keyword = request.GET.get('keyword', '')
        page = int(request.GET.get('page', 1))
        pageSize = int(request.GET.get('pageSize', 10))

        try:
            m_data = MailDomain.objects.filter(Q(host__contains=keyword)|Q(username__contains=keyword))

            serializer = MailDomainSerializer(m_data[pageSize * (page - 1):pageSize * page], many=True)

            return Response({
                "data": serializer.data,
                "total": m_data.count()
            })
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class CreateDomainAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def post(self, request):
        
        try:
            errors, status, clean_data = validate_create_domain(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            try:
                with transaction.atomic():
                    
                    m_box = Mailbox.objects.create(
                        name = clean_data["username"],
                        uri = f"imap+ssl://{clean_data['username'].replace('@', '%40')}:{clean_data['password']}@{clean_data['imap_host']}?archive=NEW",
                        from_email = clean_data["username"],
                        active = True
                    )

                    m_domain = MailDomain.objects.create(
                        host = clean_data["host"],
                        port = clean_data["port"],
                        username = clean_data["username"],
                        password = clean_data["password"],
                        imap_host = clean_data["imap_host"],
                        mailbox = m_box
                    )
                    
                    serializer = MailDomainSerializer(m_domain)

                    m_email = EmailMessage(
                        subject="メール設定の確認",
                        body="テストメールです。",
                        from_email=clean_data["username"],
                        to=[clean_data["username"]],
                        connection=get_connection(
                            host=clean_data["host"],
                            port=clean_data["port"],
                            username=clean_data["username"],
                            password=clean_data["password"],
                            use_tls=True
                        )
                    )
                    m_email.send()
                    
                    return Response({
                        "data": serializer.data,
                        "msg": "登録しました。"
                    }, status=200)
                
            except Exception as e:
                print(str(e))
                return Response({
                    "msg": "メール設定にエラーがあります。"
                }, status=400)

        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class UpdateDomainAPI(APIView):
    permission_classes = [IsCustomerAndAdmin]
    
    def get(self, request, domain_id):
        try:
            m_domain = MailDomain.objects.get(id=domain_id)
            serializer = MailDomainSerializer(m_domain)

            return Response(serializer.data, status=200)

        except Exception as e:
            print(str(e))
            return Response("Can't find", status=404)
        
    def patch(self, request, domain_id):
        try:
            errors, status, clean_data = validate_update_domain(request, domain_id)
            
            if status != 200:
                return Response({"errors": errors}, status=status)

            try:
                            
                with transaction.atomic():
                    m_domain = MailDomain.objects.get(id=domain_id)
                    m_box = m_domain.mailbox

                    m_box.uri = f"imap+ssl://{clean_data['username'].replace('@', '%40')}:{clean_data['password']}@{clean_data['imap_host']}?archive=NEW"
                    m_box.name = clean_data["username"]
                    m_box.from_email = clean_data["username"]
                    m_box.save()

                    m_domain.host = clean_data["host"]
                    m_domain.port = clean_data["port"]
                    m_domain.username = clean_data["username"]
                    m_domain.password = clean_data["password"]
                    m_domain.imap_host = clean_data["imap_host"]
                    m_domain.save()

                    serializer = MailDomainSerializer(m_domain)

                    m_email = EmailMessage(
                        subject="メール設定の確認",
                        body="テストメールです。",
                        from_email=clean_data["username"],
                        to=[clean_data["username"]],
                        connection=get_connection(
                            host=clean_data["host"],
                            port=clean_data["port"],
                            username=clean_data["username"],
                            password=clean_data["password"],
                            use_tls=True
                        )
                    )
                    m_email.send()

                    return Response({
                        "data": serializer.data,
                        "msg": "更新しました。"
                    }, status=200)
                
            except Exception as e:
                print(str(e))
                return Response({
                    "msg": "メール設定にエラーがあります。"
                }, status=400)


        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        
    def delete(self, request, domain_id):
        try:
            m_domain = MailDomain.objects.get(id=domain_id)
            m_domain.mailbox.delete()
            m_domain.delete()

            return Response({
                "msg": "削除しました。"
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        