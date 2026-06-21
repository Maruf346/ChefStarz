from rest_framework import serializers
from .models import AppDetailsModel, ReportModel

# Create your serializers here. 
class AppDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppDetailsModel
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportModel
        fields = ['id', 'target_id', 'target_type', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
