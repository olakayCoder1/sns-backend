
from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views.customer import *
from .views.memo import *
from .views.analysis import *
from .views.mail_template import *
from .views.mail import *
from .views.mail_sent import *
from .views.mail_inbox import *
router = DefaultRouter()


urlpatterns = [
    # User Analysis
    re_path(r'^analysis/(?P<user_id>[0-9]+)$', GetUserAnalysisAPI.as_view(), name='get_user_analysis'),

    # Customer
    re_path(r'^customers/$', GetCustomersAPI.as_view(), name='get_customers'),


    re_path(r'^customers/create/sns$', CreateCustomersSocialConfigAPI.as_view(), name='create_customer_condfig'),
    re_path(r'^customers/sns$', ListCustomersSocialConfigAPI.as_view(), name='get_customers_config'),
    re_path(r'^customers/post/dispatch$', DispatchVideoAPI.as_view(), name='post_video_dispatch'),
    re_path(r'^customers/sns/(?P<customer_id>[0-9]+)$', GetCustomersSocialConfigAPI.as_view(), name='update_customer_sns'),
    re_path(r'^customers/sns/(?P<customer_id>[0-9]+)/refresh$', GetCustomersSocialConfigForRefreshAPI.as_view(), name='refresh_customer_sns'),


    re_path(r'^customers/create/callback$', CreateCustomersSocialConfigCallbackAPI.as_view(), name='get_customers'),
    re_path(r'^customers/create$', CreateCustomerAPI.as_view(), name='create_customer'),
    re_path(r'^customers/batch_create$', CreateBatchCustomerAPI.as_view(), name='create_multi_customer'),
    re_path(r'^customers/download$', DownloadCustomerAPI.as_view(), name='download_customer'),
    re_path(r'^customers/(?P<customer_id>[0-9]+)$', UpdateCustomerAPI.as_view(), name='update_customer'),

    # Memo
    re_path(r'^customers/(?P<customer_id>[0-9]+)/memo$', GetCustomerMemoAPI.as_view(), name='get_customer_memo'),
    re_path(r'^customers/(?P<customer_id>[0-9]+)/memo/create$', CreateCustomerMemoAPI.as_view(), name='create_customer_memo'),
    re_path(r'^customers/(?P<customer_id>[0-9]+)/memo/(?P<memo_id>[0-9]+)$', UpdateCustomerMemoAPI.as_view(), name='update_customer_memo'),

    # Mail Template
    re_path(r'^mail_templates/$', GetMailTemplatesAPI.as_view(), name='get_mail_templates'),
    re_path(r'^mail_templates/create$', CreateMailTemplateAPI.as_view(), name='create_mail_template'),
    re_path(r'^mail_templates/(?P<mail_template_id>[0-9]+)$', UpdateMailTemplateAPI.as_view(), name='update_mail_template'),

    # Mail
    re_path(r'^mails/inbox$', GetInboxMailsAPI.as_view(), name='get_mails'),
    re_path(r'^mails/inbox/domain/(?P<domain>.*)/customer/(?P<customer_id>[0-9]+)$', GetMailsByCustomer.as_view(), name='get_mails_by_customer'),
    re_path(r'^mails/inbox/(?P<mail_id>[0-9]+)/read$', MakeMailAsRead.as_view(), name='make_mail_as_read'),
    
    re_path(r'^mails/sent$', GetSentMailsAPI.as_view(), name='get_sent_mails'),
    re_path(r'^mails/sent/(?P<mail_id>[0-9]+)$', GetSentMailAPI.as_view(), name='get_sent_mail'),


    re_path(r'^mails/new_send$', CreateMailAPI.as_view(), name='create_mail'),
    re_path(r'^mails/attachment/upload$', CreateAttachmentFileView.as_view(), name='create_mail_attachment'),
    # re_path(r'^mails/(?P<mail_id>[0-9]+)$', UpdateMailAPI.as_view(), name='update_mail'),

]
