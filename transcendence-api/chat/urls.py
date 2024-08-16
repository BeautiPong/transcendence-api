# chat/urls.py
from django.urls import path

from .views import CreateChatRoom
from . import views
from friend.views import FriendList


urlpatterns = [
    path("friend_list/", FriendList.as_view(), name="friend_list_info"),
    path('create/', CreateChatRoom.as_view(), name='create_chat_room'),
    path("", views.index, name="index"),
    path("room/<str:room_name>/", views.room, name="room"),
]