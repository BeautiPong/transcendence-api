from rest_framework import serializers


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
