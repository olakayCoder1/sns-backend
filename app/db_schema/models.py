from datetime import timedelta
from django.db import models
from django_mailbox.models import Message, Mailbox, MessageAttachment
from django.utils import timezone
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from jwt_auth.models import *
# Create your models here.

class Property(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    PROPERTY_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    )

    property_type = models.CharField(max_length=50, blank=True, null=True, choices=PROPERTY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.property_type if self.property_type is not None else ''}"
    
    class Meta:
        verbose_name = "属性"
        verbose_name_plural = "属性管理"
    

class Status(models.Model):
    name = models.CharField(max_length=50, unique=True)

    STATUS_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
    )

    status_type = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.status_type if self.status_type is not None else ''}"
    
    class Meta:
        verbose_name = "ステータス"
        verbose_name_plural = "ステータス管理"
    

class Customer(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone_2 = models.CharField(max_length=50, blank=True, null=True)
    email_2 = models.EmailField(max_length=50, blank=True, null=True)

    ads = models.CharField(max_length=255, blank=True, null=True)
    deposit_date = models.DateField(blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_days = models.IntegerField(blank=True, null=True)

    property = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    system_provided = models.BooleanField(default=True)

    last_contacted = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.last_name + " " + self.first_name
    
    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客管理"
    

class CustomerMemo(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
    
    class Meta:
        verbose_name = "顧客メモ"
        verbose_name_plural = "顧客メモ管理"
    

class MailTemplate(models.Model):
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name = "メールテンプレート"
        verbose_name_plural = "メールテンプレート管理"


class MailDomain(models.Model):
    mailbox = models.ForeignKey(Mailbox, on_delete=models.CASCADE, blank=True, null=True)
    host = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    imap_host = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "メールドメイン"
        verbose_name_plural = "メールドメイン管理"


class Mail(models.Model):
    domain = models.EmailField(max_length=50, blank=True, null=True)
    customers = models.ManyToManyField(Customer, blank=True)
    managers = models.ManyToManyField(User, blank=True)

    # mail type is inbound or outbound
    outgoing = models.BooleanField(default=False)
    read = models.DateTimeField(blank=True, null=True)
    processed = models.DateTimeField(blank=True, null=True)
    
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    attachments = models.ManyToManyField(MessageAttachment, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name = "メール"
        verbose_name_plural = "メール管理"







class SocialConfig(models.Model):
    AVAILABLE_PROVIDER = (
        ("YOUTUBE","YOUTUBE"),
        ("TIKTOK","TIKTOK"),
        ("INSTAGRAM","INSTAGRAM"),
        ("TWITTER","TWITTER"),
    )
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL , null=True ,blank=True)
    name = models.CharField(max_length=100, default="",null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    provider = models.CharField(choices=AVAILABLE_PROVIDER,max_length=10,default="YOUTUBE")
    youtube_token = models.TextField(null=True,blank=True)
    youtube_client_id = models.TextField(null=True,blank=True)
    youtube_client_secret = models.TextField(null=True,blank=True)
    youtube_project_id = models.TextField(null=True,blank=True)
    youtube_refresh_token = models.TextField(null=True,blank=True)
    youtube_credentials = models.JSONField(null=True,blank=True)
    youtube_credentials_data = models.JSONField(null=True,blank=True)
    scopes = models.TextField(null=True,blank=True)


    # twitter
    twitter_access_token = models.TextField(null=True,blank=True)
    twitter_access_token_secret = models.TextField(null=True,blank=True)


    # facebook credentials
    facebook_client_secret = models.TextField(null=True,blank=True)
    facebook_app_id = models.TextField(null=True,blank=True)
    instagram_business_id = models.TextField(null=True,blank=True)
    facebook_access_token = models.TextField(null=True,blank=True)

    # INSTAGRAM_BUSINESS_ACCOUNT_ID

    is_active = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f"{self.user.username} - YouTube Token"
    

    


    @staticmethod
    def update_social_token(user, youtube_token, youtube_refresh_token, youtube_credentials, scopes,youtube_credentials_data):
        social_token, created = SocialConfig.objects.get_or_create(user=user)
        social_token.youtube_token = youtube_token
        social_token.youtube_refresh_token = youtube_refresh_token
        social_token.youtube_credentials = youtube_credentials
        social_token.scopes = scopes
        social_token.youtube_credentials_data = youtube_credentials_data
        social_token.save()
        
        return social_token




class ScheduleVideo(models.Model):
    file = models.FileField(upload_to='schedule_videos/',storage=VideoMediaCloudinaryStorage())
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL , null=True ,blank=True)
    title = models.CharField(max_length=255)
    processing_id = models.CharField(max_length=64,null=True,blank=True)
    completed = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    youtube_title = models.TextField(blank=True, null=True)
    youtube_description = models.TextField(blank=True, null=True)
    tiktok_description = models.TextField(blank=True, null=True)
    instagram_description = models.TextField(blank=True, null=True)
    twitter_description = models.TextField(blank=True, null=True)
    socials = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


    def is_expired(self):
        now = timezone.now().date()
        thirty_days_ago = now - timedelta(days=30)
        return self.created_at.date() < thirty_days_ago