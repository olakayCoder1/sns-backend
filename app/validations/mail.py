
from django.db.models import *
from db_schema.models import *
import re


def validate_create_mail(request):
    data = dict(request.data)
    recipients = data.get("recipients", [])
    subject = data.get("subject", "")
    body = data.get("body", "")
    attachments = data.get("attachments", [])
    domain = data.get("domain", "")
    

    try:
        errors = {}

        if len(recipients) == 0:
            errors["recipients"] = "受信者を入力してください"

        if subject == "":
            errors["subject"] = "件名を入力してください"

        if body == "":
            errors["body"] = "本文を入力してください"

        if domain == "":
            errors["domain"] = "ドメインを入力してください"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "recipients": recipients,
            "subject": subject,
            "body": body,
            "attachments": attachments,
            "domain": domain
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    

def validate_create_group_mail(request):
    data = dict(request.data)
    group = int(data.get("group", 0))
    group_type = data.get("group_type", "status")
    subject = data.get("subject", "")
    body = data.get("body", "")
    attachments = data.get("attachments", [])
    domain = data.get("domain", "")
    

    try:
        errors = {}
        
        if group_type == "status" and not Status.objects.filter(id=group).exists():
            errors['group'] = "グループを選択します。"
        
        if group_type == "property" and not Property.objects.filter(id=group).exists():
            errors['group'] = "グループを選択します。"

        if subject == "":
            errors["subject"] = "件名を入力してください"

        if body == "":
            errors["body"] = "本文を入力してください"

        if domain == "":
            errors["domain"] = "ドメインを入力してください"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "group": group,
            "group_type": group_type,
            "subject": subject,
            "body": body,
            "attachments": attachments,
            "domain": domain
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    