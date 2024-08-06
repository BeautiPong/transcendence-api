from .views import get_code, get_token
from django.urls import path

urlpatterns = [
    path('login/', get_code, name='get_code'),
    path('get-token/', get_token, name='get_token'),
]