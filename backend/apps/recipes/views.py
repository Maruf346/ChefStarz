from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import RecipeModel, RecipeLikeModel, RecipePinModel, RecipeSaveModel
from .serializers import RecipeModelSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from core.custompermissions import IsOwnerOrReadOnly

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# Create your views here.

class RecipeModelViewSet(ModelViewSet):
    queryset = RecipeModel.objects.all().prefetch_related('step_by_step_recipes', 'likes', 'comments', 'shares', 'user', 'pins', 'saved_by')
    serializer_class = RecipeModelSerializer
    ordering = ['-created_at']

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        # Specific for creation/update to avoid Swagger nesting issues with MultiPart
        if getattr(self, 'action', None) in ['create', 'update', 'partial_update']:
            from .serializers import RecipeCreateUpdateSerializer
            return RecipeCreateUpdateSerializer
        return RecipeModelSerializer

    def get_permissions(self):
        action = getattr(self, 'action', None)
        if action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif action in ['like', 'pin', 'save_recipe', 'create', 'add_comment']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter out blocked users' content
        if self.request.user.is_authenticated:
            # Users blocked by the current user
            blocked_user_ids = self.request.user.blocked_users_relationship.values_list('blocked_id', flat=True)
            # Users who blocked the current user
            blocked_by_ids = self.request.user.blocked_by_relationship.values_list('blocker_id', flat=True)
            
            queryset = queryset.exclude(user_id__in=blocked_user_ids).exclude(user_id__in=blocked_by_ids)

        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty')
        prep_time = self.request.query_params.get('preparation_time')
        user_id = self.request.query_params.get('user_id')

        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if prep_time:
            queryset = queryset.filter(preparation_time=prep_time)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        recipe = self.get_object_or_404(RecipeModel, pk=pk)
        like, created = RecipeLikeModel.objects.get_or_create(recipe=recipe, user=request.user)
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        recipe = self.get_object_or_404(RecipeModel, pk=pk)
        pin, created = RecipePinModel.objects.get_or_create(recipe=recipe, user=request.user)
        if not created:
            pin.delete()
            return Response({'status': 'unpinned'}, status=status.HTTP_200_OK)
        return Response({'status': 'pinned'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_recipe(self, request, pk=None):
        recipe = self.get_object_or_404(RecipeModel, pk=pk)
        save, created = RecipeSaveModel.objects.get_or_create(recipe=recipe, user=request.user)
        if not created:
            save.delete()
            return Response({'status': 'unsaved'}, status=status.HTTP_200_OK)
        return Response({'status': 'saved'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        recipe = self.get_object_or_404(RecipeModel, pk=pk)
        comment_text = request.data.get('comment')
        
        if not comment_text or not str(comment_text).strip():
            return Response({'error': 'Comment text is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        from .models import RecipeCommentModel
        comment = RecipeCommentModel.objects.create(recipe=recipe, user=request.user, comment=comment_text.strip())
        
        from .serializers import RecipeCommentModelSerializer
        serializer = RecipeCommentModelSerializer(comment)
        return Response({'status': 'comment added', 'comment': serializer.data}, status=status.HTTP_201_CREATED)

    def get_object_or_404(self, model, **kwargs):
        return get_object_or_404(model, **kwargs)