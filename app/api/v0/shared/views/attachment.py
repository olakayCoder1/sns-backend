from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse, FileResponse
from django.db.models import *
from django.db import transaction

from db_schema.models import *
from db_schema.serializers import *
from utils.permissions import *
from validations.shared.upload import validate_file

# Create your views here.

class CreateAttachmentFileView(APIView):
    # permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
    
        try:
            errors, status, clean_data = validate_file(request)
            if status != 200:
                return Response(errors, status=status)
            
            m_attachment = AttachmentFile(file=clean_data['file'], is_used=False)
            m_attachment.save()

            return Response({
                "success": True
            }, status=200)
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)


class GetAttachmentFileView(APIView):
    # permission_classes = [IsCustomerAndMember|IsCustomerAndAdmin]
    
    def get(self, request, id):
        try:
            m_attachment = AttachmentFile.objects.get(id=id)
            
            response = FileResponse(m_attachment.file)
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(m_attachment.file.name)
            return response
        except Exception as e:
            print(str(e))
            return Response({"msg": str(e)}, status=500)
