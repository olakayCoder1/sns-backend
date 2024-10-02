
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
    
    # RegisterToken.objects.filter(user_id=m_user.id).delete()
    m_reset_token = RegisterToken(user_id=m_user.id, token=token, expire_at=(datetime.datetime.now()+ datetime.timedelta(days=90)))
    m_reset_token.save()

    activate_url = f"https://wavemaster.vercel.app/accounts/activate?token={token}"


    print("Activation Link ===========")
    print(activate_url)
    print("=================")
    
    # Send the password reset email
    mail_subject = "システムに登録されました。"
    message = render_to_string("mail_template/account_activate.html", {
        "name": f"{m_user.user_info.name}",
        "url": activate_url,
    })

    message = message
    email_obj = EmailMessage(
        mail_subject, message, to=[m_user.email]
    )
    email_obj.content_subtype = "html"
    email_obj.send()

    return True