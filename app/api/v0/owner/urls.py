
from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views.backup import *
router = DefaultRouter()


urlpatterns = [
    re_path(r'^backup/list$', GetBackupListAPI.as_view()),
    re_path(r'^backup/download$', DownloadBackupAPI.as_view()),
    re_path(r'^backup/load$', BackupLoadAPI.as_view()),
    re_path(r'^backup/create$', BackupCreateAPI.as_view()),
]
