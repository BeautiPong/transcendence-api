from django.urls import path
from .views import *

urlpatterns = [
    path('info/', FriendList.as_view(),name='friend_list'),
    path('add/<str:friend_nickname>/', AddFriend.as_view(),name='add_friend'),  #친구추가
    path('accept/<str:friend_nickname>/', AcceptFriend.as_view(), name='accept_friend'),  #친구추가
    # path('test/', AddFriendsV2.as_view(),name='test'),
]