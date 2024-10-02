
from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views.data import *
from .views.attachment import *

router = DefaultRouter()


urlpatterns = [
    re_path(r'^data/role$', GetRoleAPI.as_view()),
    re_path(r'^data/imap$', GetIMAPAPI.as_view()),
    re_path(r'^data/status$', GetStatusAPI.as_view()),
    re_path(r'^data/property$', GetPropertyAPI.as_view()),
    re_path(r'^data/domain$', GetDomainAPI.as_view()),
    re_path(r'^attachments/upload$', CreateAttachmentFileView.as_view()),
    re_path(r'^attachments/(?P<id>[0-9]+)/download$', GetAttachmentFileView.as_view()),
]
