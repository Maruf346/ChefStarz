from django.urls import path
from .views import AppDetailsView, ReportCreateView

urlpatterns = [
    # Add your routes here
    path('app-details/', AppDetailsView.as_view(), name='app-details'),
    path('reports/', ReportCreateView.as_view(), name='report-create'),
]
