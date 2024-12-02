from django.urls import path
from .views import SendVerificationCodeView, VerifyCodeView, UserProfileView

urlpatterns = [
    path('send-verification-code/', SendVerificationCodeView.as_view(), name='send-verification-code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
]
