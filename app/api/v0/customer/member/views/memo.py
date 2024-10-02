from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.memo import *

# Create your views here.

class GetCustomerMemoAPI(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request, customer_id):
        try:
            m_data = CustomerMemo.objects.filter(customer__id=customer_id)
            
            role = get_role(request.user)
            if role == "member":
                m_data = m_data.filter(customer__manager=request.user)
            elif role == "admin":
                pass
            else:
                raise Exception("Forbidden")
            
            m_data = m_data.order_by("-created_at")

            serializer = CustomerMemoSerializer(m_data, many=True)

            return Response({
                "data": serializer.data,
                "total": m_data.count()
            })
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class CreateCustomerMemoAPI(APIView):
    permission_classes = [IsCustomer]
    
    def post(self, request, customer_id):
        try:
            errors, status, clean_data = validate_memo(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                m_customer = Customer.objects.filter(id=customer_id)

                role = get_role(request.user)
                if role == "member":
                    m_customer = m_customer.filter(manager=request.user).first()
                elif role == "admin":
                    m_customer = m_customer.first()
                else:
                    raise Exception("Forbidden")

                memo = CustomerMemo.objects.create(
                    customer=m_customer,
                    manager=request.user,
                    content=clean_data["content"]
                )

                return Response({
                    "msg": "メモが正常に作成されました。",
                    "data": CustomerMemoSerializer(memo).data
                }, status=200)
            
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

class UpdateCustomerMemoAPI(APIView):
    permission_classes = [IsCustomer]
    
    def patch(self, request, customer_id, memo_id):
        try:
            errors, status, clean_data = validate_memo(request)
            
            if status != 200:
                return Response({"errors": errors}, status=status)
            
            with transaction.atomic():
                m_customer = Customer.objects.filter(id=customer_id)

                role = get_role(request.user)
                if role == "member":
                    m_customer = m_customer.filter(manager=request.user).first()
                elif role == "admin":
                    m_customer = m_customer.first()
                else:
                    raise Exception("Forbidden")

                memo = CustomerMemo.objects.filter(id=memo_id, customer=m_customer).first()
                if memo is None:
                    raise Exception("メモが見つかりません。")
                
                memo.content = clean_data["content"]
                memo.save()

                return Response({
                    "msg": "メモが正常に更新されました。",
                    "data": CustomerMemoSerializer(memo).data
                }, status=200)
            
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)
        

    def delete(self, request, customer_id, memo_id):
        try:
            with transaction.atomic():
                m_customer = Customer.objects.filter(id=customer_id)

                role = get_role(request.user)
                if role == "member":
                    m_customer = m_customer.filter(manager=request.user).first()
                elif role == "admin":
                    m_customer = m_customer.first()
                else:
                    raise Exception("Forbidden")

                memo = CustomerMemo.objects.filter(id=memo_id, customer=m_customer).first()
                if memo is None:
                    raise Exception("メモが見つかりません。")
                
                memo.delete()

                return Response("メモが削除されました。", status=200)
            
        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)