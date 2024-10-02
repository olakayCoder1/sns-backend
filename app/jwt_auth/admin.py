from django.contrib import admin
from .models import *

# Register your models here.

# register Role, User
admin.site.register(Role)
admin.site.register(UserInfo)
admin.site.register(User)
admin.site.register(Email) 