
from django.db.models import *
from db_schema.models import *
from utils.permissions import get_role


def validate_create_customer(request):
    data = dict(request.data)
    last_name = data.get("last_name", "")
    first_name = data.get("first_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    email_2 = data.get("email_2", "")
    phone_2 = data.get("phone_2", "")
    ads = data.get("ads", "")
    deposit_date = data.get("deposit_date", None)
    contract_start_date = data.get("contract_start_date", None)
    contract_days = data.get("contract_days", 0)
    status = data.get("status", 0)
    property = data.get("property", 0)
    system_provided = data.get("system_provided", False)


    try:
        errors = {}
        
        if last_name == "":
            errors["last_name"] = "姓を入力してください。"

        if first_name == "":
            errors["first_name"] = "名を入力してください。"

        if email == "":
            errors["email"] = "メールを入力してください。"

        if email != "" and Customer.objects.filter(email=email).exists():
            errors["email"] = "このメールは既に登録されています。"

        if phone == "":
            errors["phone"] = "電話番号を入力してください。"
           

        clean_data = {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone": phone,
            "email_2": email_2,
            "phone_2": phone_2,
            "ads": ads,
            "deposit_date": deposit_date,
            "contract_start_date": contract_start_date,
            "contract_days": contract_days,
            "status": status,
            "property": property,
            "system_provided": system_provided
        }

        status = 422 if len(errors) > 0 else 200
        
        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    
def validate_update_customer(request, customer_id):
    data = dict(request.data)
    last_name = data.get("last_name", "")
    first_name = data.get("first_name", "")
    email = data.get("email", "")
    phone = data.get("phone", "")
    email_2 = data.get("email_2", "")
    phone_2 = data.get("phone_2", "")
    ads = data.get("ads", "")
    deposit_date = data.get("deposit_date", None)
    contract_start_date = data.get("contract_start_date", None)
    contract_days = data.get("contract_days", 0)
    status = data.get("status", 0)
    property = data.get("property", 0)
    system_provided = data.get("system_provided", False)

    customer = Customer.objects.filter(id=customer_id)

    role = get_role(request.user)
    if role == "member":
        customer = customer.filter(manager=request.user)
    elif role == "admin":
        pass
    else:
        raise Exception("Forbidden")

    customer = customer.first()
    
    if customer is None:
        raise Exception("データが見つかりません。")
    
    try:
        errors = {}
        
        if last_name == "":
            errors["last_name"] = "姓を入力してください。"

        if first_name == "":
            errors["first_name"] = "名を入力してください。"

        if email == "":
            errors["email"] = "メールを入力してください。"

        if email != "" and Customer.objects.filter(Q(email=email), ~Q(id=customer_id)).exists():
            errors["email"] = "このメールは既に登録されています。"

        if phone == "":
            errors["phone"] = "電話番号を入力してください。"

        clean_data = {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone": phone,
            "email_2": email_2,
            "phone_2": phone_2,
            "ads": ads,
            "deposit_date": deposit_date,
            "contract_start_date": contract_start_date,
            "contract_days": contract_days,
            "status": status,
            "property": property,
            "system_provided": system_provided
        }

        status = 422 if len(errors) > 0 else 200

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    

    
def validate_delete_customer(request, customer_id):
    data = dict(request.data)

    customer = Customer.objects.filter(id=customer_id)

    role = get_role(request.user)
    if role == "member":
        customer = customer.filter(manager=request.user)
    elif role == "admin":
        pass
    else:
        raise Exception("Forbidden")

    customer = customer.first()
    
    if customer is None:
        raise Exception("データが見つかりません。")
    
    try:
        errors = {}

        clean_data = {

        }

        status = 422 if len(errors) > 0 else 200

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    

    