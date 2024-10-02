
# Generate token and generate reset url
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password, make_password
from db_schema.models import *
import re


def validate_password_change(request):
    data = dict(request.data)
    password = data.get("password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")
    
    try:
        errors = {}

        if password == "":
            errors["password"] = "この項目は必須です。"

        if password != "" and check_password(password, request.user.password) == False:
            errors["password"] = "パスワードが一致しません。"

        if new_password == "":
            errors["new_password"] = "この項目は必須です。"

        if confirm_password == "":
            errors["confirm_password"] = "この項目は必須です。"

        if password != "" and new_password != "" and new_password != confirm_password:
            errors["confirm_password"] = "新しいパスワードが一致しません。"

        # check contains 8 characters, 1 uppercase, 1 lowercase, 1 number
        if not re.search("[0-9]", new_password):
            errors["new_password"] = "パスワードは数字を含めてください。"

        if not re.search("[a-zA-Z]", new_password):
            errors["new_password"] = "パスワードは英字を含めてください。"

        if not re.search("[!@#$%^&*()_+-=]", new_password):
            errors["new_password"] = "パスワードは記号を含めてください。"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "password": password,
            "new_password": new_password,
            "confirm_password": confirm_password
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    

def validate_forgot_password(request):
    data = dict(request.data)
    email = data.get("email", "")
    
    try:
        errors = {}

        if email == "":
            errors["email"] = "この項目は必須です。"

        if email != "" and User.objects.filter(email=email).count() == 0:
            errors["email"] = "入力されたメールアドレスは登録されていません。"
        
        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "email": email
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    

def validate_reset_password(request):
    data = dict(request.data)
    token = data.get("token", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")
    
    try:
        errors = {}

        if token == "":
            errors["token"] = "この項目は必須です。"

        if new_password == "":
            errors["new_password"] = "この項目は必須です。"

        if confirm_password == "":
            errors["confirm_password"] = "この項目は必須です。"

        if new_password != "" and new_password != confirm_password:
            errors["confirm_password"] = "新しいパスワードが一致しません。"

        # check contains 8 characters, 1 uppercase, 1 lowercase, 1 number
        if new_password != "" and (len(new_password) < 8 or new_password.isalpha() or new_password.isnumeric()):
            errors["new_password"] = "パスワードは8文字以上の英数字を含めてください。"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "token": token,
            "new_password": new_password,
            "confirm_password": confirm_password
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}