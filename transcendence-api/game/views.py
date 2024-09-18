from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.shortcuts import render, redirect
from channels.layers import get_channel_layer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from scoreHistory.models import ScoreHistory
from users.models import CustomUser
from users.serializers import UserScoreSerializer
from .models import Game
from .serializers import GameSerializer
from game.serializers import GameScoreHistorySerializer
from friend.views import check_friend_status
from friend.models import Friend



class RecentGamesView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        recent_games = Game.objects.filter(user1=user).order_by('-create_time')[:4]
        serializer = GameSerializer(recent_games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InviteGameView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, nickname):
        user = request.user
        try:
            friend = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        # 나 자신에게 게임 초대를 시도할 경우 예외 처리
        if user == friend:
            raise ValidationError(detail="You cannot invite yourself.", code=status.HTTP_400_BAD_REQUEST)

        # 친구가 아닌 사람에게 게임 초대를 시도할 경우 예외 처리
        if not check_friend_status(user, friend, Friend.Status.ACCEPT):
            raise ValidationError(detail="You can invite only friend.", code=status.HTTP_400_BAD_REQUEST)

        # 오프라인 상태인 친구에게 게임 초대를 시도할 경우 예외 처리
        if not friend.is_online:
            raise ValidationError(detail="You can invite only online friend.", code=status.HTTP_400_BAD_REQUEST)

        if friend.is_in_game:
            raise ValidationError(detail="You cannot invite a friend who is currently in a game.", code=status.HTTP_400_BAD_REQUEST)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{friend.nickname}",
            {
                'type': 'invite_game',
                'sender': user.nickname,
                'message': f"{user.nickname} invite you."
            }
        )

        return Response({"message": "Friend invite sent."}, status=status.HTTP_201_CREATED)

class AcceptGameView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, friend_nickname):
        user = request.user

        try:
            friend = CustomUser.objects.get(nickname=friend_nickname)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Friend does not exist.", code=status.HTTP_404_NOT_FOUND)

        # 오프라인 상태인 친구의 게임 초대를 수락할 경우 예외 처리
        if not friend.is_online:
            raise ValidationError(detail="Cannot accept: friend is offline.", code=status.HTTP_400_BAD_REQUEST)

        # 이미 게임 중인 친구의 게임 초대를 수락할 경우 예외 처리
        if friend.is_in_game:
            raise ValidationError(detail="Cannot accept: friend is in a game.", code=status.HTTP_400_BAD_REQUEST)

        waiting_room = f'waiting_{friend_nickname}'
        room_name = f'{user.nickname}_{friend_nickname}'
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{friend_nickname}",
            {
                'type': 'join_room',
                'waiting_room': waiting_room,
                'room_name': room_name,
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{user.nickname}",
            {
                'type': 'join_room',
                'waiting_room': waiting_room,
                'room_name': room_name,
            }
        )

        return Response({"message": "Join Game"}, status=status.HTTP_201_CREATED)

class MatchingView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        waiting_room = None
        room_name = None
        myNickname = request.data.get('myNickname')
        friendNickname = request.data.get('friendNickname')
        if(myNickname and friendNickname):
            sorted_names = sorted([myNickname, friendNickname])
            waiting_room = f'{myNickname}_waitingRoom'
            room_name = f'{sorted_names[0]}_{sorted_names[1]}_gameRoom'

        user = request.user

        if room_name:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                waiting_room,
                {
                    'type': 'start_game_with_friend',
                    'waiting_room': waiting_room,
                    'room_name': room_name,
                    'message': 'start game with friend'
                }
            )

        if user.is_authenticated:
            token = str(request.auth)
            data = {
                'jwt_token': token,
                'waiting_room': waiting_room,
                'room_name': room_name
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


class GamePageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, room_name):
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # 게임 페이지에 필요한 정보를 JSON으로 전달
        data = {
            'room_name': room_name,
            'jwt_token': str(request.auth)
        }

        return JsonResponse(data, status=status.HTTP_200_OK)

class OfflineGameView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self,request):
        user1 = request.data.get('user1')
        user2 = request.data.get('user2')
        user3 = request.data.get('user3')
        user4 = request.data.get('user4')

        if user3 is None or user4 is None:
            match_type = '1v1'
        else:
            match_type = 'tournament'

        data = {
            'user1': user1,
            'user2': user2,
            'user3': user3,
            'user4': user4,
            'match_type': match_type,
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

