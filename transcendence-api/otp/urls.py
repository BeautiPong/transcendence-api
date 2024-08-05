
from django.urls import path
from .views import RequestOTPView, VerifyOTPView

urlpatterns = [
    path('generate/', RequestOTPView.as_view(), name='generate_otp'),
    path('verify/', VerifyOTPView.as_view(), name='verify_otp'),
]
