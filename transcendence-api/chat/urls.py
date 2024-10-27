# chat/urls.py
from django.urls import path

from .views import CreateChatRoom, PreMessage, CheckUnReadMessage
from . import views
from friend.views import FriendList


urlpatterns = [
    path("friend_list/", FriendList.as_view(), name="friend_list_info"),
    path('create/', CreateChatRoom.as_view(), name='create_chat_room'),
    path("pre_message/<str:room_name>/", PreMessage.as_view(), name="room"),
    path("unread/<str:friend_nickname>/", CheckUnReadMessage.as_view(), name="check_unread_message"),
]