# chat/urls.py
from django.urls import path

from .views import FriendListInfo, CreateChatRoom
from . import views


urlpatterns = [
    path("friend_list/", FriendListInfo.as_view(), name="friend_list_info"),
    path('create/', CreateChatRoom.as_view(), name='create_chat_room'),
    path("", views.index, name="index"),
    path("room/<str:room_name>/", views.room, name="room"),
]