# chat/urls.py
from django.urls import path

from .views import ChatFriend
# from . import views


urlpatterns = [
    # path("", views.index, name="index"),
    # path("<str:room_name>/", views.room, name="room"),

    path("<str:friend_nickname>/", ChatFriend.as_view(), name="chat_friend"),
]