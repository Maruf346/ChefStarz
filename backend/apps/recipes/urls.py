from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeModelViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeModelViewSet)

urlpatterns = [
    # Add your routes here
    path('', include(router.urls)),
]
