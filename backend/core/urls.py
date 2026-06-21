from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


#--------------------------------------
# DRF-YASG API Documentation
#--------------------------------------
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Chef_Starz API",
        default_version='v1',
        description="API documentation for Chef_Starz",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
#--------------------------------------



#--------------------------------------
# Sentry Error Trigger
#--------------------------------------
def trigger_error(request):
    division_by_zero = 1 / 0
#--------------------------------------



#--------------------------------------
# Redirect backend root to docs
#--------------------------------------
def redirect_to_docs(request):
    """Redirect root URL to API documentation"""
    return redirect('schema-swagger-ui')
#--------------------------------------



urlpatterns = [
    path('admin/', admin.site.urls),

    # Sentry Error Trigger
    path('sentry-debug/', trigger_error),

    # Local app routes (v1 prefix)
    
    path('v1/users/', include('apps.users.urls')),
    
    path('v1/admins/', include('apps.admins.urls')),
    
    path('v1/posts/', include('apps.posts.urls')),
    
    path('v1/recipes/', include('apps.recipes.urls')),
    
    path('v1/notifications/', include('apps.notifications.urls')),

    path('v1/app_settings/', include('apps.app_settings.urls')),
    
    path('v1/reports/', include('apps.admins.report_urls')),
    
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Redirect root to docs
    path('', redirect_to_docs, name='root-redirect'),
]