from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.memo import *

# Create your views here.
class GetUserAnalysisAPI(APIView):
    permission_classes = [IsCustomer]
    
    def get(self, request, user_id):
        try:
            m_user = User.objects.filter(id=user_id).first()
            m_data = Customer.objects.filter(manager=m_user)

            m_status = Status.objects.all()

            res = {
                "name": m_user.user_info.name,
                "total": m_data.count(),
                "analysis": []
            }

            for status in m_status:
                res["analysis"].append({
                    "id": status.id,
                    "name": status.name,
                    "count": m_data.filter(status=status).count()
                })

            return Response(res, status=200)

        except Exception as e:
            print(str(e))
            return Response(str(e), status=500)