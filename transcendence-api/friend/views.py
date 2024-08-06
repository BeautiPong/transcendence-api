from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from friend.models import Friend

# 내 친구 리스트 반환
class FriendList(APIView) :
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        # user1이 user인 column 찾아오기
        # user2가 친구인데, status가 ACCEPT인 친구만
        friend_with_user1 = Friend.objects.get(user1 = user)
        friend_list = [friend.user2 for friend in friend_with_user1]

        response = JsonResponse(
            {
                "friend id" : friend_list.id,
                "friend_name" : friend_list.name,
            },
            status = status.HTTP_200_OK
        )
        return response

