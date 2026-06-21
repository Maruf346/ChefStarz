from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema

from ..models import CustomUserModel
from ..serializers import (
    GoogleLoginSerializer, 
    AppleLoginSerializer, 
    SocialUserRepresentationSerializer
)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=GoogleLoginSerializer)
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user, created = CustomUserModel.objects.get_or_create(email=email)
        
        refresh = RefreshToken.for_user(user)
        user_data = SocialUserRepresentationSerializer(user).data
        
        return Response({
            "success": True,
            "created": created,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data
        }, status=status.HTTP_200_OK)


class AppleLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=AppleLoginSerializer)
    def post(self, request):
        serializer = AppleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        id_token = serializer.validated_data['id_token']
        
        if not email:
            # Fallback for mock/trusted login
            email = f"apple_{id_token[:10]}@icloud.com"
            
        user, created = CustomUserModel.objects.get_or_create(email=email)
        
        refresh = RefreshToken.for_user(user)
        user_data = SocialUserRepresentationSerializer(user).data
        
        return Response({
            "success": True,
            "created": created,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data
        }, status=status.HTTP_200_OK)
