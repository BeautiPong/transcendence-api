import random
import string
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import CustomUser
from .models import OTP
from .serializers import RequestOTPSerializer, VerifyOTPSerializer

class RequestOTPView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            OTP.objects.create(user=user, otp=otp)

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                'beautipong@gmail.com',
                [email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']

            user = CustomUser.objects.filter(email=email).first()
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            otp_instance = OTP.objects.filter(user=user).last()
            if not otp_instance:
                return Response({"error": "No OTP found for this user"}, status=status.HTTP_404_NOT_FOUND)

            if otp_instance.otp != otp_code:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_instance.is_valid():
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "OTP verified successfully!!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
