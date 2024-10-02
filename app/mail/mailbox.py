
from utils.permissions import *
from django.db.models import *
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection
from django_mailbox.models import MessageAttachment

from celery import shared_task
from datetime import datetime

from db_schema.models import *
from db_schema.serializers import *

def send_email_task(sender, recepients, clean_data):
    recepient_users = Customer.objects.filter(id__in=recepients)
    
    mail_subject = clean_data["subject"]
    
    # each line is wrapped in <p> tag
    # each new line is replaced with <br> tag
    message = clean_data["body"].replace("\n", "<br>")
    message = f"<p style='color: #333;'>{message}</p>"

    email_obj = EmailMessage(
        mail_subject, message, to=[recepient_user.email for recepient_user in recepient_users]
    )
    email_obj.content_subtype = "html"

    for attach_id in clean_data["attachments"]:
        m_attach = MessageAttachment.objects.get(id = attach_id)
        m_attach_serializer = MessageAttachmentSerializer(m_attach).data
        
        email_obj.attach(m_attach_serializer["info"]["name"], m_attach.document.file.read(), m_attach_serializer["info"]["content_type"])

    m_domain = MailDomain.objects.filter(username=clean_data["domain"]).first()
    if m_domain is None:
        raise Exception("ドメインが無効です。")
    
    email_obj.from_email = m_domain.username
    email_obj.connection = get_connection(
        host=m_domain.host,
        port=m_domain.port,
        username=m_domain.username,
        password=m_domain.password,
        use_tls=True
    )

    email_obj.send()

    m_box = m_domain.mailbox

    # save email_obj to Message
    message = m_box.record_outgoing_message(email_obj.message())

    m_customers = Customer.objects.filter(Q(email__in=message.to_addresses) | Q(email_2__in=message.to_addresses))
    m_managers = User.objects.filter(id=sender)

    if m_customers.count() == 0 or m_managers.count() == 0:
        return

    with transaction.atomic():
        m_mail = Mail.objects.create(
            domain=m_box.name,
            outgoing=True,
            read=datetime.now(),
            subject=message.subject,
            body=message.text if message.html is None else message.html,
            processed=message.processed
        )

        m_attachments = MessageAttachment.objects.filter(message=message)
        for attach  in m_attachments:
            m_mail.attachments.add(attach)

        for customer in m_customers:
            customer.last_contacted = message.processed
            customer.save()
            m_mail.customers.add(customer)

        for manager in m_managers:
            m_mail.managers.add(manager)
