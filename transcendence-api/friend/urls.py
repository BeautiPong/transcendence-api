from django.urls import path
from .views import *

urlpatterns = [
    path('info/', FriendList.as_view(),name='friend_list'),
    path('add/', AddFriend.as_view(),name='add_friend'),
    path('test/', AddFriendsV2.as_view(),name='test'),
]