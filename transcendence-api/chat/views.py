from django.shortcuts import render
from rest_framework_simplejwt.authentication    import JWTAuthentication
from rest_framework.permissions                 import IsAuthenticated
from rest_framework.views                       import APIView
from friend.models import Friend
from .serializers import FriendSerializer, ChatRoomSerializer
from rest_framework.response import Response
from chattingRoom.models import ChattingRoom

def index(request):

    if request.method == 'GET' :
        token = request.GET.get('token')
        return render(request, "chat/index.html", {'jwt_token': token})

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


class FriendListInfo(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        friend_list = Friend.objects.filter(user1=user)
        friend_info_list = [ ]
        for friend in friend_list :
             friend_nickname = {
                 'nickname' : friend.user2.nickname
             }
             friend_info_list.append(friend_nickname)
             
        serializer = FriendSerializer(friend_info_list, many=True)
        return Response({'friends': serializer.data})
    

class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        friend_nickname = request.data.get('friend_nickname')

        # 채팅방 이름 생성 (예: 사용자와 친구의 닉네임을 조합)
        room_name = ''.join(sorted([user.nickname, friend_nickname]))

        # 채팅방 생성
        # chat_room, created = ChattingRoom.objects.get_or_create(name=room_name)

        # 응답 데이터 준비
        # serializer = ChatRoomSerializer(chat_room)
        return Response({'room_name': room_name}, status=201)