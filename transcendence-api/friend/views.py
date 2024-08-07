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


# 내 친구 관계 추가
class AddFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request) :
        user = request.user

        friend_nickname = request.data.get('nickname')
        user2 = CustomUser.objects.filter(nickname=friend_nickname).first()

        # friend 객체 생성
        friend = Friend(
            user1=user,
            user2=user2,
            user1_victory_num=0,
            user2_victory_num=0,
            status=Friend.Status.ACCEPT  # 일단 확인하려고 ACCEPT로 설정했습니다.
        )
        friend.save()

        # friend 객체 생성
        friend = Friend(
            user1=user2,
            user2=user,
            user1_victory_num=0,
            user2_victory_num=0,
            status=Friend.Status.ACCEPT
        )
        friend.save()

        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)