from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/login/<str:nickname>/', consumers.LoginConsumer.as_asgi()),
]
