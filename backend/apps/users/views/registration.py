import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from ..serializers import *
from ..models import CustomUserModel
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

class Stage1SignupView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=KidSignupSerializer)
    def post(self, request):
        serializer = KidSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # 1. Generate a random 6-digit code
            otp = str(random.randint(100000, 999999))
            
            # 2. Save code to the user model
            user.verification_code = otp
            user.save()
            
            # 3. Send email to the KID
            send_mail(
                subject="Verify your Email",
                message=f"Your verification code is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return Response({
                "message": "Step 1 complete. OTP sent to kid's email.",
                "email": user.email
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VerifyKidEmailView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=OtpVerificationSerializer)
    def post(self, request):
        # 1. Use the serializer to validate the input structure
        serializer = OtpVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = CustomUserModel.objects.get(email=email)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # 2. Logic Check
            if user.verification_code == code:
                user.is_email_verified = True
                user.verification_code = None 
                user.save()

                # Generate Tokens for Flutter
                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "Email verified!",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Return automatic errors if email format is wrong or code is missing
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=ProfileCompletionSerializer)
    def post(self, request):
        serializer = ProfileCompletionSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.pop('email')
            
            try:
                user = CustomUserModel.objects.get(email=email)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Ensure they verified their own email first!
            if not user.is_email_verified:
                return Response({"error": "Verify your own email first"}, status=status.HTTP_403_FORBIDDEN)

            # Update the user instance with the rest of the data
            serializer = ProfileCompletionSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                
                # 1. Generate code for the PARENT
                parent_otp = str(random.randint(100000, 999999))
                user.verification_code = parent_otp
                user.save()
                
                # 2. Send email to the PARENT
                send_mail(
                    subject="Action Required: Parental Consent",
                    message=f"Your child is signing up. Provide them this code to approve: {parent_otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.parent_email],
                    fail_silently=False,
                )
                
                return Response({"message": "Profile updated. Code sent to parent."}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyParentApprovalView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=OtpVerificationSerializer)
    def post(self, request):
        serializer = OtpVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            try:
                user = CustomUserModel.objects.get(email=email)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if user.verification_code == code:
            user.is_parent_approved = True
            user.verification_code = None
            user.save()
            return Response({"message": "Account activated!"})
        
        return Response({"error": "Invalid parent code"}, status=status.HTTP_400_BAD_REQUEST)
# Resend OTP View
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(request_body=ResendOtpSerializer)
    def post(self, request):
        serializer = ResendOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUserModel.objects.get(email=email)
            except CustomUserModel.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.is_email_verified and user.is_parent_approved:
                return Response({"message": "Account already fully verified"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate new OTP
            otp = str(random.randint(100000, 999999))
            user.verification_code = otp
            user.save()

            if not user.is_email_verified:
                # Resend to Kid
                send_mail(
                    subject="Verify your Email",
                    message=f"Your new verification code is: {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response({"message": "New OTP sent to kid's email."}, status=status.HTTP_200_OK)
            else:
                # Resend to Parent
                if not user.parent_email:
                    return Response({"error": "Parent email not set. Complete profile first."}, status=status.HTTP_400_BAD_REQUEST)
                
                send_mail(
                    subject="Action Required: Parental Consent (Resent)",
                    message=f"Your child is signing up. Provide them this code to approve: {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.parent_email],
                    fail_silently=False,
                )
                return Response({"message": "New OTP sent to parent's email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)