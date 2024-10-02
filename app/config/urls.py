from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import re_path
from django.views.static import serve
from django.conf.urls.static import static

from jwt_auth.urls import urlpatterns as auth_urls
from api.v0.owner.urls import urlpatterns as v0_owner_urls
from api.v0.customer.member.urls import urlpatterns as v0_member_urls
from api.v0.customer.admin_user.urls import urlpatterns as v0_admin_urls
from api.v0.shared.urls import urlpatterns as v0_shared_urls

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/', include(auth_urls)),
    re_path(r'^api/v0/', include(v0_member_urls)),
    re_path(r'^api/v0/owner/', include(v0_owner_urls)),
    re_path(r'^api/v0/admin/', include(v0_admin_urls)),
    re_path(r'^api/', include(v0_shared_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

if settings.DEBUG:
    import debug_toolbar
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    from rest_framework import permissions
    from django.conf import settings
    
    schema_view = get_schema_view(
        openapi.Info(
            title="Episyche Technologies",
            default_version='v1',),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        re_path(r'^swagger/', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    

        




