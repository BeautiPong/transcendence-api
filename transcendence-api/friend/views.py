from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.views import APIView
from friend.models import Friend
from rest_framework.response import Response
from users.utils import *

# 내 친구 리스트 반환
class FriendList(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        friend_with_user1 = Friend.objects.filter(user1 = user, status=Friend.Status.ACCEPT)
        friend_list = [friend.user2 for friend in friend_with_user1]

        friend_info_list = [ ]
        for friend in friend_list :
            friend_info_list.append(get_user_info(friend.nickname))
        friend_info_list_sorted = sorted(friend_info_list, key=lambda user_info: user_info["nickname"])

        friend_info_serializer = UserInfoSerializer(friend_info_list_sorted, many=True)
        return Response(friend_info_serializer.data, status=status.HTTP_200_OK)

