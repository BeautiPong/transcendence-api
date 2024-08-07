from django.contrib import admin
from django.urls import path, include
from users.views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/admin/', admin.site.urls),


    path('api/otp/', include("otp.urls")),
    path('api/user/', include('users.urls')),
    path('api/score/', include('scoreHistory.urls')),

    path('api/friend/', include("friend.urls")),
    path('api/game/', include('game.urls')),
]
