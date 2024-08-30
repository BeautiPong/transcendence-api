from django.urls import path
from game.consumers import GameConsumer, OfflineConsumer
from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer
from game.consumers import MatchingConsumer

websocket_urlpatterns = [
    path('ws/match/', MatchingConsumer.as_asgi()),  # 기본 매칭 관련 WebSocket 연결
    path('ws/match/<str:waiting_room>/<str:room_name>/', MatchingConsumer.as_asgi()),  # 특정 대기실과 방 이름을 포함한 매칭 연결
    path('ws/game/online/<str:room_name>/', GameConsumer.as_asgi()),  # 게임 관련 WebSocket 연결
    path('ws/game/offline/<str:userA_nickname>/<str:userB_nickname>/', OfflineConsumer.as_asgi()),  # 오프라인 게임 관련 WebSocket 연결
    path('ws/user/', NotificationConsumer.as_asgi()),  # 사용자별 알림 연결
    path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),  # 채팅 방 관련 WebSocket 연결
    
]
