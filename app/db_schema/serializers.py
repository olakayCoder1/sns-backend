from rest_framework import serializers
from django_mailbox.models import Message, Mailbox, MessageAttachment
from django.db.models import *
import re
from .models import *
from jwt_auth.serializers import *


class PropertySerializer(serializers.ModelSerializer):
    customer_cnt = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['id', 'name', 'property_type', 'customer_cnt']

    def get_customer_cnt(self, obj):
        return Customer.objects.filter(property=obj).count()

class StatusSerializer(serializers.ModelSerializer):
    customer_cnt = serializers.SerializerMethodField()

    class Meta:
        model = Status
        fields = ['id', 'name', 'status_type', 'customer_cnt']

    def get_customer_cnt(self, obj):
        return Customer.objects.filter(status=obj).count()

class CustomerSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    status = StatusSerializer(read_only=True)
    manager = UserNameSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = "__all__"

class CustomerNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'name']


class CustomerNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ["id", "name", "email"]

class CustomerFlatSerializer(serializers.ModelSerializer):
    manager = UserNameSerializer(read_only=True)

    class Meta:
        model = Customer
        exclude = ["created_at", "updated_at"]


class CustomerMemoSerializer(serializers.ModelSerializer):
    manager = UserNameSerializer(read_only=True)

    class Meta:
        model = CustomerMemo
        fields = ["id", "content", "manager", "customer", "created_at"]


class MailTemplateSerializer(serializers.ModelSerializer):
    publisher = UserNameSerializer(read_only=True)
    class Meta:
        model = MailTemplate
        fields = ["id", "subject", "body", "publisher"]

class MessageAttachmentSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    class Meta:
        model = MessageAttachment
        fields = "__all__"

    def get_info(self, obj):
        m_attach = MessageAttachment.objects.get(id = obj.id)

        text = m_attach.headers
        
        content_type_match = re.search(r'Content-Type:\s*([^;]+)', text)
        if content_type_match:
            content_type = content_type_match.group(1)
        else:
            content_type = "unknown"

        name_match = re.search(r'name="([^"]+)"', text)
        if name_match:
            name = name_match.group(1)
        else:
            name = "unknown"

        return {
            "content_type": content_type,
            "name": name
        }


class MailDomainSerializer(serializers.ModelSerializer):

    class Meta:
        model = MailDomain
        fields = "__all__"


class MailSerializer(serializers.ModelSerializer):
    customers = CustomerNameSerializer(many=True)
    managers = UserNameSerializer(many=True)
    attachments = MessageAttachmentSerializer(many=True)

    class Meta:
        model = Mail
        fields = "__all__"


class MailInboxSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_cnt = serializers.SerializerMethodField()
    new_message_cnt = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = "__all__"

    def get_last_message(self, obj):
        domain = self.context.get("domain", "")
        m_messages = Mail.objects.filter(customers__id=obj.id, domain=domain).order_by('-processed')
        if m_messages.exists():
            
            m_message = m_messages.first()
            return MailSerializer(m_message).data

        return None
    
    def get_message_cnt(self, obj):
        domain = self.context.get("domain", "")
        m_messages = Mail.objects.filter(customers__id=obj.id, domain=domain)
        return m_messages.count()

    def get_new_message_cnt(self, obj):
        domain = self.context.get("domain", "")
        m_messages = Mail.objects.filter(customers__id=obj.id, outgoing=False, read=None, domain=domain)
        return m_messages.count()
