from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PostModel, LikeModel, PinModel, SaveModel
from .serializers import PostModelSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from core.custompermissions import IsOwnerOrReadOnly

from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# Create your views here.

class PostModelViewSet(ModelViewSet):
    queryset = PostModel.objects.all().prefetch_related('likes', 'comments', 'shares', 'user', 'pins', 'saved_by')
    serializer_class = PostModelSerializer
    ordering = ['-created_at']

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        # Specific for creation/update to avoid Swagger nesting issues with MultiPart
        if getattr(self, 'action', None) in ['create', 'update', 'partial_update']:
            from .serializers import PostCreateUpdateSerializer
            return PostCreateUpdateSerializer
        return PostModelSerializer

    def get_permissions(self):
        # Actions that anyone (auth'd) can do: like, pin, save, comment, share
        # Actions that only owners can do: update, partial_update, destroy
        action = getattr(self, 'action', None)
        if action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif action in ['like', 'pin', 'save_post', 'create', 'add_comment']:
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

        post_type = self.request.query_params.get('post_type')
        user_id = self.request.query_params.get('user_id')

        if post_type:
            queryset = queryset.filter(post_type=post_type)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object_or_404(PostModel, pk=pk)
        like, created = LikeModel.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        post = self.get_object_or_404(PostModel, pk=pk)
        pin, created = PinModel.objects.get_or_create(post=post, user=request.user)
        if not created:
            pin.delete()
            return Response({'status': 'unpinned'}, status=status.HTTP_200_OK)
        return Response({'status': 'pinned'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_post(self, request, pk=None):
        post = self.get_object_or_404(PostModel, pk=pk)
        save, created = SaveModel.objects.get_or_create(post=post, user=request.user)
        if not created:
            save.delete()
            return Response({'status': 'unsaved'}, status=status.HTTP_200_OK)
        return Response({'status': 'saved'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        post = self.get_object_or_404(PostModel, pk=pk)
        comment_text = request.data.get('comment')
        
        if not comment_text or not str(comment_text).strip():
            return Response({'error': 'Comment text is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        from .models import CommentModel
        comment = CommentModel.objects.create(post=post, user=request.user, comment=comment_text.strip())
        
        from .serializers import CommentModelSerializer
        serializer = CommentModelSerializer(comment)
        return Response({'status': 'comment added', 'comment': serializer.data}, status=status.HTTP_201_CREATED)

    def get_object_or_404(self, model, **kwargs):
        return get_object_or_404(model, **kwargs)