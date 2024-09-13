from django.urls import path
from .views import *

urlpatterns = [
    path('info/', FriendList.as_view(),name='friend_list'),
    path('add/<str:friend_nickname>/', AddFriend.as_view(),name='add_friend'),  #친구추가
    path('accept/<str:friend_nickname>/', AcceptFriend.as_view(), name='accept_friend'),  #친구추가
    path('block/<str:friend_nickname>/', BlockFriend.as_view(), name='block_friend'),  #친구차단
    path('reblock/<str:friend_nickname>/', ReBlockFriend.as_view(), name='reblock_friend'),  #친구차단해제
    path('delete/<str:friend_nickname>/', DeleteFriend.as_view(), name='delete_friend'),  #친구삭제
    path('search/<str:friend_nickname>/', SearchFriend.as_view(), name='search_friend'), #친구 검색_조회
    path('block-list/', GetBlockFriendList.as_view(), name='get_block_friend'), #차단된 친구 조회
    # path('test/', AddFriendsV2.as_view(),name='test'),
    path('pend/', PendFriendRequest.as_view(), name='pend_friend'), #아직 읽지 않은 친구 요청 확인
]