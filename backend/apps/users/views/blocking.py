from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from ..models import CustomUserModel, UserBlockModel
from ..serializers import UserBlockSerializer, BlockedUserListSerializer

class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserBlockSerializer(data=request.data)
        if serializer.is_valid():
            blocked_user_id = serializer.validated_data['blocked_user_id']
            blocked_user = get_object_or_404(CustomUserModel, id=blocked_user_id)

            if request.user == blocked_user:
                return Response({"detail": "You cannot block yourself."}, status=status.HTTP_400_BAD_REQUEST)

            block, created = UserBlockModel.objects.get_or_create(
                blocker=request.user,
                blocked=blocked_user
            )

            if not created:
                return Response({"detail": "User is already blocked."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"detail": f"User {blocked_user.email} blocked successfully."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnblockUserView(APIView):
    """
    Optional but useful for the blocked list UI to unblock users.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        blocked_user_id = request.data.get('blocked_user_id')
        if not blocked_user_id:
            return Response({"detail": "blocked_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        block = UserBlockModel.objects.filter(blocker=request.user, blocked_id=blocked_user_id).first()
        if block:
            block.delete()
            return Response({"detail": "User unblocked successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({"detail": "User not found in your blocked list."}, status=status.HTTP_404_NOT_FOUND)

class BlockedUserListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlockedUserListSerializer

    def get_queryset(self):
        return UserBlockModel.objects.filter(blocker=self.request.user)
