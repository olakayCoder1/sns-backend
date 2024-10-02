
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.permissions import *
from django.db.models import *
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

from db_schema.models import *
from db_schema.serializers import *
import datetime

def send_mail(request, email):
    m_user = User.objects.get(email=email)
    
    token = default_token_generator.make_token(m_user)
    
    ResetToken.objects.filter(user_id=m_user.id).delete()
    m_reset_token = ResetToken(user_id=m_user.id, token=token, expire_at=(datetime.datetime.now()+ datetime.timedelta(days=3)))
    m_reset_token.save()

    reset_password_url = f"https://wavemaster.vercel.app/accounts/password/reset?token={token}"
    
    print(f"http://localhost:3000/accounts/password/reset?token={token}")
    expire_at =  (datetime.datetime.now()+ datetime.timedelta(days=3)).strftime("%Y/%m/%d %H:%M")
    
    # Send the password reset email
    mail_subject = "パスワードを設定・変更してください"
    message = render_to_string("mail_template/password_forgot.html", {
        "name": f"{m_user.user_info.name}",
        "url": reset_password_url,
        "expire_at": expire_at,
    })

    message = message
    email_obj = EmailMessage(
        mail_subject, message, to=[m_user.email]
    )
    email_obj.content_subtype = "html"
    email_obj.send()
