from django.urls import path

from notification import consumers

websocket_urlpatterns = [
    path('ws/user/', consumers.NotificationConsumer.as_asgi()),
]