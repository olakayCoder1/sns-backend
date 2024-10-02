
# Generate token and generate reset url
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password, make_password
from db_schema.models import *
import re


def validate_profile(request):
    data = dict(request.data)
    last_name = data.get("last_name", "")
    first_name = data.get("first_name", "")
    last_name_furi = data.get("last_name_furi", "")
    first_name_furi = data.get("first_name_furi", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    
    try:
        errors = {}

        if last_name == "":
            errors["last_name"] = "氏名を入力してください。"

        if first_name == "":
            errors["first_name"] = "氏名を入力してください。"

        if email == "":
            errors["email"] = "メールアドレスを入力してください。"

        if email != "" and User.objects.filter(email=email).count() == 0:
            errors["email"] = "入力されたメールアドレスは登録されていません。"
        

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "last_name": last_name,
            "first_name": first_name,
            "last_name_furi": last_name_furi,
            "first_name_furi": first_name_furi,
            "email": email,
            "phone": phone
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    
