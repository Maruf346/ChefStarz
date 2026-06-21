from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.profile import *
from .views.registration import *
from .views.auth import PasswordResetConfirmHTMLView, ManualPasswordResetConfirmView, DeleteAccountView
from .views.social_auth import GoogleLoginView, AppleLoginView
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.views import PasswordResetConfirmView

from .views.blocking import BlockUserView, UnblockUserView, BlockedUserListView

router = DefaultRouter()
router.register(r'profiles', CustomUserViewSet)

urlpatterns = [
    # Add your routes here
    path('', include(router.urls)),

    # Blocking Routes
    path('block/', BlockUserView.as_view(), name='block-user'),
    path('unblock/', UnblockUserView.as_view(), name='unblock-user'),
    path('blocked-list/', BlockedUserListView.as_view(), name='blocked-list'),

    # Signup Routes
    path('signup/kid/', Stage1SignupView.as_view(), name='kid-signup-stage1'),
    path('signup/verify-kid/', VerifyKidEmailView.as_view()),
    path('signup/complete-profile/', CompleteProfileView.as_view()),
    path('signup/verify-parent/', VerifyParentApprovalView.as_view()),
    path('signup/resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    # This adds: password/reset/, password/change/, login/, logout/, and user/
    path('auth/', include('dj_rest_auth.urls')),

    # Required for dj-rest-auth to generate the reset link in the email
    path(
        'auth/password/reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmHTMLView.as_view(),
        name='password_reset_confirm'
    ),

    # Custom Manual Reset for the HTML page
    path('auth/password/reset/confirm/manual/', ManualPasswordResetConfirmView.as_view(), name='manual-password-reset-confirm'),

    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'), 

    # Social Login Routes
    path('user/google/id-token/', GoogleLoginView.as_view(), name='google_login_new'),
    path('dj-rest-auth/apple/', AppleLoginView.as_view(), name='apple_login_new'),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('auth/apple/', AppleLoginView.as_view(), name='apple_login'),   

    # Delete Account Route
    path('auth/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
