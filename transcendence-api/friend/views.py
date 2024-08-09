from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.views import APIView
from friend.models import Friend
from rest_framework.response import Response
from users.utils import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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


# 친구 추가
# 프론트에서 친구의 nickname을 주고
# 백에서 받아서 친구 관계 저장 -> DB
# 소켓으로 상대방 nickname group에 메시지 보내기
class AddFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname) :
        user = request.user

        user2 = CustomUser.objects.filter(nickname=friend_nickname).first()

        # 친구 요청 보낸 사람 = user1
        friend = Friend(
            user1=user,
            user2=user2,
            user1_victory_num=0,
            user2_victory_num=0,
            status=Friend.Status.SEND
        )
        friend.save()

        # 친구 요청 받은 사람 = user1
        friend = Friend(
            user1=user2,
            user2=user,
            user1_victory_num=0,
            user2_victory_num=0,
            status=Friend.Status.NONE
        )
        friend.save()

        # 친구가 온라인에 있으면 소켓으로 보내기
        if user2.is_active :
            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f'friend_request_{friend_nickname}',
                {
                    'type': 'friend_request_message',
                    'message': f'Friend request from {user.nickname}'
                }
            )

        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)
    

# 친구 수락
class AddFriend(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname) :
        user = request.user
        user2 = CustomUser.objects.filter(nickname=friend_nickname).first()

        friend1 = Friend.objects.filter(user1=user, user2=user2).first()
        friend2 = Friend.objects.filter(user1=user2, user2=user).first()

        friend1.status = Friend.Status.ACCEPT
        friend2.status = Friend.Status.ACCEPT

        friend1.save()
        friend2.save()
    
        return Response({"message": "친구관계 성립~"}, status=status.HTTP_200_OK)
    