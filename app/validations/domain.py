
from django.db.models import *
from db_schema.models import *
import re


def validate_create_domain(request):
    data = dict(request.data)
    host = data.get("host", "")
    port = data.get("port", "")
    username = data.get("username", "")
    password = data.get("password", "")
    imap_host = data.get("imap_host", "")
    

    try:
        errors = {}
        
        if host == "":
            errors["host"] = "ホストを入力してください。"

        if port == "":
            errors["port"] = "ポートを入力してください。"

        if username == "":
            errors["username"] = "メールアドレスを入力してください。"

        if username != "" and MailDomain.objects.filter(username=username).exists():
            errors["username"] = "このメールアドレスは既に登録されています。"

        if password == "":
            errors["password"] = "パスワードを入力してください。"

        if imap_host == "":
            errors["imap_host"] = "IMAPホストを入力してください。"

        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "imap_host": imap_host
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    
def validate_update_domain(request, domain_id):
    data = dict(request.data)
    host = data.get("host", "")
    port = data.get("port", "")
    username = data.get("username", "")
    password = data.get("password", "")
    imap_host = data.get("imap_host", "")

    try:
        errors = {}

        if host == "":
            errors["host"] = "ホストを入力してください。"

        if port == "":
            errors["port"] = "ポートを入力してください。"

        if username == "":
            errors["username"] = "メールアドレスを入力してください。"

        if MailDomain.objects.filter(~Q(id=domain_id), Q(username=username)).exists():
            errors["username"] = "このドメインは存在しません。"

        if password == "":
            errors["password"] = "パスワードを入力してください。"

        if imap_host == "":
            errors["imap_host"] = "IMAPホストを入力してください。"


        status = 422 if len(errors) > 0 else 200
        clean_data = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "imap_host": imap_host
        }

        return errors, status, clean_data
        
    except Exception as e:
        print(str(e))
        
        return {}, 500, {}
    