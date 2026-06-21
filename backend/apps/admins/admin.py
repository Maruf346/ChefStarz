from django.contrib import admin
from .models import *
from rest_framework.authtoken.models import TokenProxy

# Register your models here.
admin.site.register(AppDetailsModel)
admin.site.register(ReportModel)

try:
    admin.site.unregister(TokenProxy)
except admin.sites.NotRegistered:
    pass