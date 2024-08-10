from django.urls import path

from notification import consumers

websocket_urlpatterns = [
    path('ws/login/<str:nickname>/', consumers.NotificationConsumer.as_asgi()),
]
