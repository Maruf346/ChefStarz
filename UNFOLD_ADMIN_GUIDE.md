# Django Unfold Admin Panel - Complete Guide

## 📚 Table of Contents
1. [What is Django Unfold?](#what-is-django-unfold)
2. [How Unfold Works](#how-unfold-works)
3. [Installation & Setup](#installation--setup)
4. [Adding Charts to Model Admin Pages](#adding-charts-to-model-admin-pages)
5. [Customizing the Admin Dashboard](#customizing-the-admin-dashboard)
6. [Universal Template for Any Model](#universal-template-for-any-model)
7. [Advanced Customization](#advanced-customization)

---

## What is Django Unfold?

**Django Unfold** is a modern, beautiful admin interface for Django that replaces the default admin panel with a sleek, Tailwind CSS-based design. It provides:

- 🎨 Modern, dark-mode UI
- 📊 Built-in chart components
- 🚀 Better UX than default Django admin
- 🔧 Highly customizable
- 📱 Responsive design

---

## How Unfold Works

### Architecture Overview

```
Django Admin (default)
    ↓
Unfold (replaces templates & styling)
    ↓
Your Custom Templates (override specific blocks)
    ↓
Chart.js (for visualizations)
```

### Key Concepts

1. **Template Inheritance**: Unfold provides base templates that you extend
2. **Block Overriding**: You override specific blocks to inject custom content
3. **ModelAdmin Classes**: You use `unfold.admin.ModelAdmin` instead of Django's default
4. **Context Data**: You pass data to templates via `extra_context`

---

## Installation & Setup

### Step 1: Install Unfold

```bash
uv add django-unfold
```

### Step 2: Update `settings.py`

```python
# backend/core/settings.py

INSTALLED_APPS = [
    "unfold",  # MUST be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    # ... rest of your apps
]

# Add templates directory
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Add this
        'APP_DIRS': True,
        # ...
    },
]

# Optional: Configure Unfold
UNFOLD = {
    "ADMIN_SITE_TITLE": "Your App Admin",
    "INDEX_TEMPLATE": "admin/index.html",  # Custom dashboard
    "DASHBOARD_CALLBACK": "apps.users.admin.dashboard_callback",  # Optional
}
```

### Step 3: Update Your ModelAdmin Classes

```python
# apps/users/admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin  # Import from unfold
from .models import CustomUserModel

@admin.register(CustomUserModel)
class UserAdmin(ModelAdmin):  # Inherit from unfold.admin.ModelAdmin
    list_display = ["email", "is_active", "date_joined"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "username"]
```

---

## Adding Charts to Model Admin Pages

### Method 1: Using Chart.js (Recommended)

This is what we implemented for the User model.

#### Step 1: Override `changelist_view` in ModelAdmin

```python
# apps/users/admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin
from django.db.models import Count
from django.db.models.functions import TruncDay
import json

@admin.register(CustomUserModel)
class UserAdmin(ModelAdmin):
    list_display = ["email", "age_group", "is_active", "date_joined"]
    
    def changelist_view(self, request, extra_context=None):
        """Override to add chart data to the user list page"""
        extra_context = extra_context or {}
        
        # Query your data
        try:
            data = (
                CustomUserModel.objects
                .annotate(date=TruncDay("date_joined"))
                .values("date")
                .annotate(count=Count("id"))
                .order_by("date")
            )
            
            # Format for Chart.js
            labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
            values = [d["count"] for d in data] if data else []
        except Exception:
            labels = []
            values = []
        
        # Create chart data structure
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "New Users",
                "data": values,
                "borderColor": "#7c3aed",  # Purple
                "backgroundColor": "rgba(124, 58, 237, 0.1)",
                "tension": 0.4,
                "fill": True
            }],
        }
        
        # Pass as JSON string to template
        extra_context["user_growth_chart"] = json.dumps(chart_data)
        
        return super().changelist_view(request, extra_context=extra_context)
```

#### Step 2: Create Custom Template

Create: `templates/admin/<app_name>/<model_name>/change_list.html`

For User model: `templates/admin/users/customusermodel/change_list.html`

```html
{% extends "admin/change_list.html" %}
{% load unfold %}

{% block result_list %}
    {% if user_growth_chart %}
    <div style="background: white; padding: 20px; margin: 0 0 20px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 15px; font-size: 18px; font-weight: 600; color: #1f2937;">
            📊 User Registration Growth
        </h3>
        <div style="height: 300px; width: 100%;">
            <canvas id="userGrowthChart"></canvas>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('userGrowthChart').getContext('2d');
        const chartData = {{ user_growth_chart|safe }};
        
        new Chart(ctx, {
            type: 'bar',  // or 'line', 'pie', 'doughnut', etc.
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    </script>
    {% endif %}
    
    {{ block.super }}  <!-- This renders the original table -->
{% endblock %}
```

---

## Universal Template for Any Model

### Generic Chart Template

You can use this template for **any model** by following this pattern:

#### 1. ModelAdmin Pattern (Python)

```python
# apps/<your_app>/admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncDay, TruncMonth
import json
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(ModelAdmin):
    list_display = ["field1", "field2", "created_at"]
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # CUSTOMIZE THIS QUERY FOR YOUR MODEL
        try:
            data = (
                YourModel.objects
                .annotate(date=TruncDay("created_at"))  # Change field name
                .values("date")
                .annotate(count=Count("id"))  # Or Sum("amount"), Avg("rating"), etc.
                .order_by("date")
            )
            
            labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
            values = [d["count"] for d in data] if data else []
        except Exception as e:
            print(f"Chart error: {e}")
            labels = []
            values = []
        
        chart_data = {
            "labels": labels,
            "datasets": [{
                "label": "Your Metric Name",  # CUSTOMIZE
                "data": values,
                "borderColor": "#10b981",  # CUSTOMIZE COLOR
                "backgroundColor": "rgba(16, 185, 129, 0.1)",
                "tension": 0.4,
                "fill": True
            }],
        }
        
        extra_context["your_chart_name"] = json.dumps(chart_data)  # CUSTOMIZE
        
        return super().changelist_view(request, extra_context=extra_context)
```

#### 2. Template Pattern (HTML)

Create: `templates/admin/<app_name>/<model_name>/change_list.html`

```html
{% extends "admin/change_list.html" %}
{% load unfold %}

{% block result_list %}
    {% if your_chart_name %}  <!-- MATCH YOUR CONTEXT VARIABLE -->
    <div style="background: white; padding: 20px; margin: 0 0 20px 0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 15px; font-size: 18px; font-weight: 600; color: #1f2937;">
            📊 Your Chart Title  <!-- CUSTOMIZE -->
        </h3>
        <div style="height: 300px; width: 100%;">
            <canvas id="yourChartId"></canvas>  <!-- UNIQUE ID -->
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('yourChartId').getContext('2d');  <!-- MATCH ID -->
        const chartData = {{ your_chart_name|safe }};  <!-- MATCH CONTEXT VAR -->
        
        new Chart(ctx, {
            type: 'bar',  // CUSTOMIZE: 'line', 'bar', 'pie', 'doughnut', 'radar'
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    </script>
    {% endif %}
    
    {{ block.super }}
{% endblock %}
```

---

## Customizing the Admin Dashboard

### Dashboard with Charts (Home Page)

#### 1. Create Dashboard Callback

```python
# apps/users/admin.py

def dashboard_callback(request, context):
    """Add data to the admin dashboard homepage"""
    
    # Example: Total counts
    from apps.users.models import CustomUserModel
    from apps.posts.models import PostModel
    
    context.update({
        "total_users": CustomUserModel.objects.count(),
        "active_users": CustomUserModel.objects.filter(is_active=True).count(),
        "total_posts": PostModel.objects.count(),
    })
    
    # Example: Chart data
    from django.db.models import Count
    from django.db.models.functions import TruncDay
    import json
    
    data = (
        CustomUserModel.objects
        .annotate(date=TruncDay("date_joined"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    
    labels = [d["date"].strftime("%Y-%m-%d") for d in data] if data else []
    values = [d["count"] for d in data] if data else []
    
    context["dashboard_chart"] = json.dumps({
        "labels": labels,
        "datasets": [{
            "label": "New Users",
            "data": values,
            "borderColor": "#7c3aed",
            "backgroundColor": "rgba(124, 58, 237, 0.1)",
        }],
    })
    
    return context
```

#### 2. Create Dashboard Template

Create: `templates/admin/index.html`

```html
{% extends "unfold/layouts/base_simple.html" %}
{% load unfold %}

{% block content %}
<div style="padding: 20px;">
    <!-- Stats Cards -->
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h4 style="color: #6b7280; font-size: 14px; margin-bottom: 5px;">Total Users</h4>
            <p style="font-size: 32px; font-weight: bold; color: #1f2937;">{{ total_users }}</p>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h4 style="color: #6b7280; font-size: 14px; margin-bottom: 5px;">Active Users</h4>
            <p style="font-size: 32px; font-weight: bold; color: #10b981;">{{ active_users }}</p>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h4 style="color: #6b7280; font-size: 14px; margin-bottom: 5px;">Total Posts</h4>
            <p style="font-size: 32px; font-weight: bold; color: #3b82f6;">{{ total_posts }}</p>
        </div>
    </div>
    
    <!-- Chart -->
    {% if dashboard_chart %}
    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <h3 style="margin-bottom: 15px; font-size: 18px; font-weight: 600;">User Growth</h3>
        <div style="height: 400px;">
            <canvas id="dashboardChart"></canvas>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('dashboardChart').getContext('2d');
        const chartData = {{ dashboard_chart|safe }};
        
        new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
            }
        });
    </script>
    {% endif %}
</div>

{{ block.super }}
{% endblock %}
```

#### 3. Register in Settings

```python
# backend/core/settings.py

UNFOLD = {
    "ADMIN_SITE_TITLE": "Chef Starz Admin",
    "INDEX_TEMPLATE": "admin/index.html",
    "DASHBOARD_CALLBACK": "apps.users.admin.dashboard_callback",
}
```

---

## Advanced Customization

### Chart Types

Chart.js supports many chart types:

```javascript
// Line Chart
type: 'line'

// Bar Chart (Vertical)
type: 'bar'

// Horizontal Bar Chart
type: 'horizontalBar'

// Pie Chart
type: 'pie'

// Doughnut Chart
type: 'doughnut'

// Radar Chart
type: 'radar'

// Polar Area Chart
type: 'polarArea'
```

### Color Schemes

```javascript
// Tailwind CSS Colors
"#ef4444"  // Red
"#f59e0b"  // Amber
"#10b981"  // Green
"#3b82f6"  // Blue
"#8b5cf6"  // Violet
"#ec4899"  // Pink
"#6366f1"  // Indigo
"#14b8a6"  // Teal

// With transparency
"backgroundColor": "rgba(239, 68, 68, 0.1)"  // 10% opacity
```

### Multiple Datasets

```python
chart_data = {
    "labels": labels,
    "datasets": [
        {
            "label": "New Users",
            "data": new_users_data,
            "borderColor": "#10b981",
            "backgroundColor": "rgba(16, 185, 129, 0.1)",
        },
        {
            "label": "Active Users",
            "data": active_users_data,
            "borderColor": "#3b82f6",
            "backgroundColor": "rgba(59, 130, 246, 0.1)",
        }
    ],
}
```

### Common Queries for Charts

```python
# Count by date
data = Model.objects.annotate(
    date=TruncDay("created_at")
).values("date").annotate(
    count=Count("id")
).order_by("date")

# Sum by date
data = Order.objects.annotate(
    date=TruncDay("created_at")
).values("date").annotate(
    total=Sum("amount")
).order_by("date")

# Average by date
data = Review.objects.annotate(
    date=TruncDay("created_at")
).values("date").annotate(
    avg_rating=Avg("rating")
).order_by("date")

# Count by month
data = Model.objects.annotate(
    month=TruncMonth("created_at")
).values("month").annotate(
    count=Count("id")
).order_by("month")

# Group by category
data = Model.objects.values(
    "category"
).annotate(
    count=Count("id")
).order_by("-count")
```

---

## Quick Reference Checklist

### Adding a Chart to Any Model

- [ ] Install `django-unfold`
- [ ] Add `"unfold"` before `django.contrib.admin` in `INSTALLED_APPS`
- [ ] Change `ModelAdmin` import to `from unfold.admin import ModelAdmin`
- [ ] Override `changelist_view()` in your ModelAdmin class
- [ ] Query your data and format it for Chart.js
- [ ] Pass data via `extra_context["chart_name"] = json.dumps(chart_data)`
- [ ] Create template: `templates/admin/<app>/<model>/change_list.html`
- [ ] Extend `{% extends "admin/change_list.html" %}`
- [ ] Override `{% block result_list %}`
- [ ] Add Chart.js CDN and render chart
- [ ] Use `{{ block.super }}` to keep the table

---

## Troubleshooting

### Chart not showing?
1. Check browser console for JavaScript errors (F12)
2. Verify template path matches Django's naming: `<app_label>/<model_name_lowercase>/change_list.html`
3. Ensure `json.dumps()` is used when passing data
4. Check that Chart.js CDN is loading

### Table disappeared?
- Make sure you have `{{ block.super }}` in your template block

### Template not found?
- Verify `DIRS: [BASE_DIR / "templates"]` in `TEMPLATES` setting
- Check file path exactly matches Django's convention

---

## Summary

**Django Unfold** modernizes your admin panel with minimal code changes. To add charts:

1. **Python**: Override `changelist_view()` and pass chart data via `extra_context`
2. **Template**: Create `change_list.html` template that extends Unfold's base
3. **JavaScript**: Use Chart.js to render the visualization

This pattern works for **any model** - just customize the query, colors, and labels!

---

## Production Deployment & S3 Static Files

In production, Unfold assets (CSS, JS, Fonts) must be served via S3 or a web server like Nginx/WhiteNoise.

### 🔌 S3 Configuration (Recommended)

1. **Bucket Policy**: Ensure your S3 bucket allows public read for the `static/` prefix.
2. **Django Settings**: Disable ACLs if your bucket has "ACLs disabled" (default for new buckets).

```python
# settings.py
AWS_S3_ACCESS_CONTROL_LIST = None
AWS_S3_OBJECT_PARAMETERS = {}
AWS_QUERYSTRING_AUTH = False

STORAGES = {
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "static",
            "file_overwrite": False,
        }
    },
}
```

3. **Collectstatic**: Your entrypoint or CI/CD must run `python manage.py collectstatic --noinput`. This uploads Unfold's assets to S3.

### 🚨 Troubleshooting Production 502 Errors

If you see a **502 Bad Gateway** after adding Unfold:
- **Check Logs**: Run `docker logs <container_id>`.
- **Verify Collectstatic**: If `collectstatic` fails (e.g., S3 permission error), the container might crash before starting the server.
- **ACL Error**: If you see `AccessControlListNotSupported`, ensure `AWS_S3_ACCESS_CONTROL_LIST = None` is set in your `settings.py`.

---

**Created**: 2026-02-18  
**Project**: Chef Starz  
**Author**: Development Team
