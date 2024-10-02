
from django.db.models import *
from db_schema.models import *
import re


def validate_mail_template(request):
    data = dict(request.data)
    subject = data.get("subject", "")
    body = data.get("body", "")
    

    try:
        errors = {}

        if subject == "":
            errors["subject"] = "件名を入力してください"

        if body == "":
            errors["body"] = "本文を入力してください"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "subject": subject,
            "body": body
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    