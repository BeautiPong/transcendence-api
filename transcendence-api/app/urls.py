from django.contrib import admin
from django.urls import path, include
from users.views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('otp/', include("otp.urls")),
    path('user/', include('users.urls')),
    path('score/', include('scoreHistory.urls')),
    path('friend/', include("friend.urls")),
    path('game/', include('game.urls')),
]
