from django.urls import path

from game.consumers import MatchingConsumer
from notification.consumers import NotificationConsumer

websocket_urlpatterns = [
    path('ws/match/', MatchingConsumer.as_asgi()),
    path('ws/match/<str:room_name>/', MatchingConsumer.as_asgi()),
    path('ws/user/', NotificationConsumer.as_asgi()),
]
