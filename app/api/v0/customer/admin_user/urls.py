
from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views.user import *
from .views.domain import *

router = DefaultRouter()

urlpatterns = [
    re_path(r'^', include(router.urls)),
    
    re_path(r'^users$', GetUsersAPI.as_view(), name='get_users'),
    re_path(r'^users/create$', CreateUserAPI.as_view(), name='create_user'),
    re_path(r'^users/(?P<user_id>[0-9]+)$', UpdateUserAPI.as_view(), name='update_user'),

    re_path(r'^domains/$', GetDomainsAPI.as_view(), name='get_domains'),
    re_path(r'^domains/create$', CreateDomainAPI.as_view(), name='create_domain'),
    re_path(r'^domains/(?P<domain_id>[0-9]+)$', UpdateDomainAPI.as_view(), name='update_domain'),
]
