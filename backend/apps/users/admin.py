from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import CustomUserModel, UserBlockModel

from django.db.models import Count
from django.db.models.functions import TruncDay
import json

@admin.register(CustomUserModel)
class UserAdmin(ModelAdmin):
    list_display = ["email", "age_group", "is_active", "is_parent_approved", "date_joined"]
    list_filter = ["age_group", "is_active", "is_staff"]
    search_fields = ["email", "username"]
    
    def changelist_view(self, request, extra_context=None):
        """Override to add chart data to the user list page"""
        extra_context = extra_context or {}
        
        # Calculate user statistics
        total_users = CustomUserModel.objects.count()
        active_users = CustomUserModel.objects.filter(is_active=True).count()
        inactive_users = CustomUserModel.objects.filter(is_active=False).count()
        parent_approved = CustomUserModel.objects.filter(is_parent_approved=True).count()
        
        extra_context.update({
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "parent_approved": parent_approved,
        })
        
        # Chart data
        try:
            data = (
                CustomUserModel.objects
                .annotate(date=TruncDay("date_joined"))
                .values("date")
                .annotate(count=Count("id"))
                .order_by("date")
            )
            
            labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
            values = [d["count"] for d in data] if data else []
        except Exception:
            labels = []
            values = []
        
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "New Users",
                "data": values,
                "borderColor": "#7c3aed", 
                "backgroundColor": "rgba(124, 58, 237, 0.1)",
                "tension": 0.4,
                "fill": True
            }],
        }
        
        extra_context["user_growth_chart"] = json.dumps(chart_data)
        
        print(f"DEBUG: Chart data - Labels: {labels}, Values: {values}")
        
        return super().changelist_view(request, extra_context=extra_context)



# Unfold Dashboard Stats
def user_stats_callback(request, context):
    print("DEBUG: user_stats_callback executed")
    
    # 1. Basic Stats
    from apps.posts.models import PostModel
    context.update({
        "total_users": CustomUserModel.objects.count(),
        "active_users": CustomUserModel.objects.filter(is_active=True).count(),
        "total_posts": PostModel.objects.count(),
    })

    # 2. Logic: Get users joined per day
    try:
        data = (
            CustomUserModel.objects
            .annotate(date=TruncDay("date_joined"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Structure the data for Chart.js
        labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
        values = [d["count"] for d in data] if data else []
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "New Users",
                "data": values,
                "borderColor": "#7c3aed", 
                "backgroundColor": "rgba(124, 58, 237, 0.1)",
                "tension": 0.4,
                "fill": True
            }],
        }
        context["dashboard_chart"] = json.dumps(chart_data)
    except Exception as e:
        print(f"Dashboard chart error: {e}")
        context["dashboard_chart"] = json.dumps({"labels": [], "datasets": []})

    return context

@admin.register(UserBlockModel)
class UserBlockAdmin(ModelAdmin):
    list_display = ["blocker", "blocked", "created_at"]
    search_fields = ["blocker__email", "blocked__email"]