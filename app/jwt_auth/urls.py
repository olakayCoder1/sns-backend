
from django.conf.urls import include
from django.urls import re_path
from rest_framework_simplejwt import views
from rest_framework.routers import DefaultRouter

from .views.ProfileView import *
from .views.PasswordView import *
from .views.NotificationView import *
from .views.AccountView import *

router = DefaultRouter()

urlpatterns = [
    re_path(r'auth/login$', views.TokenObtainPairView.as_view()),
    re_path(r'auth/refresh$', views.TokenRefreshView.as_view()),
    re_path(r'auth/password/forgot$', PasswordForgotView.as_view()),
    re_path(r'auth/password/reset$', PasswordResetView.as_view()),
    re_path(r'account/password$', PasswordChangeView.as_view()),
    re_path(r'account/activate$', AccountActivateAPI.as_view()),
    re_path(r"me$", GetMyAccountInfoView.as_view()),
    re_path(r"profile$", ProfileView.as_view()),
    re_path(r"notifications$", GetNotificationsView.as_view()),
]
