from django.contrib import admin
from django.urls import path
from users.views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('join/', join, name='signup'),
    path('login/', login, name='login'),
    path('otp/', include("otp.urls")),
]
