from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, VerificationCode
from .serializers import UserSerializer, VerificationCodeSerializer
import random
import string
import time

class SendVerificationCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        VerificationCode.objects.filter(phone_number=phone_number).delete()

        code = ''.join(random.choices(string.digits, k=4))
        print(code)
        VerificationCode.objects.create(phone_number=phone_number, code=code)

        time.sleep(random.uniform(1, 2))

        return Response({"message": "Verification code sent"})

class VerifyCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        if not phone_number or not code:
            return Response({"error": "Phone number and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification_code = VerificationCode.objects.get(phone_number=phone_number, code=code, is_valid=True)
        except VerificationCode.DoesNotExist:
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        verification_code.is_valid = False
        verification_code.save()

        user, created = User.objects.get_or_create(phone_number=phone_number)
        if created:
            user.save()

        return Response({"message": "User authenticated", "user_id": user.id})

class UserProfileView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        referred_users = User.objects.filter(referred_by=user)
        referred_users_data = UserSerializer(referred_users, many=True).data

        profile_data = {
            "phone_number": user.phone_number,
            "invite_code": user.invite_code,
            "referred_by": user.referred_by.phone_number if user.referred_by else None,
            "referred_users": referred_users_data
        }

        return Response(profile_data)

    def post(self, request, user_id):
        invite_code = request.data.get('invite_code')
        if not invite_code:
            return Response({"error": "Invite code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.referred_by:
            return Response({"error": "Invite code already used"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            referred_user = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response({"error": "Invalid invite code"}, status=status.HTTP_400_BAD_REQUEST)

        user.referred_by = referred_user
        user.save()

        return Response({"message": "Invite code applied successfully"})
