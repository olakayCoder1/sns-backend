
# Generate token and generate reset url
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password, make_password
from db_schema.models import *
import re


def validate_file(request):
    
    try:
        file = request.data['file']
        errors = {}
        
        if file == None:
            errors["file"] = "証拠資料を選択してください。"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "file": file
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    