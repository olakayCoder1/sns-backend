from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

# Create your models here.

class Role(models.Model):
    role_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "権限"
        verbose_name_plural = "権限管理"
    
class UserInfo(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    name_furi = models.CharField(max_length=50, blank=True, null=True)
    last_name_furi = models.CharField(max_length=50, blank=True, null=True)
    first_name_furi = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    is_youtube = models.BooleanField(default=False)
    is_instagram = models.BooleanField(default=False)
    is_tiktok = models.BooleanField(default=False)
    is_twitter = models.BooleanField(default=False)

    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "担当情報"
        verbose_name_plural = "担当情報管理"


from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    user_id = models.CharField(max_length=50, null=True, blank=True)
    user_info = models.ForeignKey(UserInfo, on_delete=models.CASCADE, blank=True, null=True)

    username = None
    last_name = None
    first_name = None
    email = models.EmailField(_('email address'), unique=True)
    REQUIRED_FIELDS=[]

    USERNAME_FIELD = 'email'

    PERMISSION_CHOICES = [
        ("super", 'Site Manager'),
        ("customer", 'Customer Company'),
    ]
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES, default="customer")
    is_allowed = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "担当"
        verbose_name_plural = "担当管理"

class RegisterToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024)
    expire_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024)
    expire_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Email(models.Model):

    when = models.DateTimeField(null=False, auto_now_add=True)
    to = models.EmailField(null=False, blank=False,)
    subject = models.CharField(null=False, max_length=128,)
    body = models.TextField(null=False, max_length=1024,)
    ok = models.BooleanField(null=False, default=True,)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "メール"
        verbose_name_plural = "メール管理" 


