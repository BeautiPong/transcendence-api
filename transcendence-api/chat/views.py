from django.shortcuts import render
from rest_framework_simplejwt.authentication    import JWTAuthentication
from rest_framework.permissions                 import IsAuthenticated
from rest_framework.views                       import APIView

# def index(request):
#     return render(request, "chat/index.html")

# def room(request, room_name):
#     return render(request, "chat/room.html", {"room_name": room_name})


# 채팅하고 싶은 상대방의 닉네임을 파라미터로 넘겨주기
class ChatFriend(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname):
        user = request.user

        sorted_names = sorted(user.nickname, friend_nickname)
        room_name = f"chat_{sorted_names[0]}_{sorted_names[1]}"

        return render(request, "chat/room.html", {"room_name": room_name})