from django.db import models
from django.conf import settings

# Create your models here.
class AppDetailsModel(models.Model):
    class Meta:
        app_label = 'admins'
        db_table = 'App Details Table'

    # default fields
    terms_and_conditions = models.TextField(blank=True, null=True)
    privacy_policy = models.TextField(blank=True, null=True)
    about_us = models.TextField(blank=True, null=True)
    contact_us = models.TextField(blank=True, null=True)

    def __str__(self):
        return "App Details"

class ReportModel(models.Model):
    TARGET_TYPE_CHOICES = [
        ('recipe', 'Recipe'),
        ('comment', 'Comment'),
        ('user', 'User'),
        ('post', 'Post'),
    ]

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        app_label = 'admins'
        db_table = 'Reports Table'

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    target_id = models.CharField(max_length=255)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} on {self.target_type} {self.target_id}"
