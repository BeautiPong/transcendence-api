from django.shortcuts import render
from rest_framework_simplejwt.authentication    import JWTAuthentication
from rest_framework.permissions                 import IsAuthenticated
from rest_framework.views                       import APIView
from friend.models import Friend
from .serializers import FriendSerializer
from rest_framework.response import Response
from chattingRoom.models import ChattingRoom
from users.models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken
from message.models import Message

# 기존 메시지를 가져오기
class PreMessage(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, room_name):

        user = request.user

        # 기존의 대화 내용 찾아오기
        chatting_room = ChattingRoom.objects.filter(name=room_name).first()

        # 채팅방의 메시지 가져오기
        if chatting_room:
            messages = Message.objects.filter(room=chatting_room).order_by('created_at')
            # 메시지를 JSON 형식으로 변환
            message_list = [
                {
                    "sender": message.sender.nickname,
                    "content": message.content,
                    "created_at": message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for message in messages
            ]
        else:
            message_list = []

        return Response({"messages": message_list,
                         "user": user.nickname},
                        status=200)
        

# 채팅방 그룹 이름 설정
class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        friend_nickname = request.data.get('friend_nickname')

        # 채팅방 이름 생성 (예: 사용자와 친구의 닉네임을 조합)
        sorted_names = sorted([user.nickname, friend_nickname])
        room_name = f'chat_{sorted_names[0]}_{sorted_names[1]}'

        # 응답 데이터 준비
        return Response({'room_name': room_name,
                         "sender": user.nickname}, status=201)