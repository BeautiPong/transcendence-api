from django.conf.urls.static import static
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

    path('api/chat/', include("chat.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)