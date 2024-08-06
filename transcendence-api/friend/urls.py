from django.urls import path
from .views import FriendList

urlpatterns = [
    path('info/', FriendList.as_view(),name='friend_list')
]