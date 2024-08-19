import aioredis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
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


class SaveGameView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = request.data
        try:
            user1 = CustomUser.objects.get(nickname=data['user1_nickname'])
            user2 = CustomUser.objects.get(nickname=data['user2_nickname'])
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        game_data = {
            'user1': user1.id,
            'user2': user2.id,
            'user1_score': data['user1_score'],
            'user2_score': data['user2_score']
        }
        serializer = GameScoreHistorySerializer(data=game_data)
        if serializer.is_valid():
            serializer.save()
            if data['user1_score'] > data['user2_score']:
                user1_data = {
                    "match_cnt": user1.match_cnt + 1,
                    "win_cnt": user1.win_cnt + 1,
                    "score": user1.score + 20
                }
                user2_data = {
                    "match_cnt": user2.match_cnt + 1,
                    "win_cnt": user2.win_cnt,
                    "score": user1.score - 20
                }
            else:
                user1_data = {
                    "match_cnt": user1.match_cnt + 1,
                    "win_cnt": user1.win_cnt,
                    "score": user1.score - 20
                }
                user2_data = {
                    "match_cnt": user2.match_cnt + 1,
                    "win_cnt": user2.win_cnt + 1,
                    "score": user1.score + 20
                }

            user1_serializer = UserScoreSerializer(user1, data=user1_data)
            user2_serializer = UserScoreSerializer(user2, data=user2_data)
            if user1_serializer.is_valid() and user2_serializer.is_valid():
                user1_serializer.save()
                user2_serializer.save()

                ScoreHistory.objects.create(user=user1, score=user1.score)
                ScoreHistory.objects.create(user=user2, score=user2.score)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecentGamesView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        recent_games = Game.objects.filter(user1=user).order_by('-create_time')[:5]
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
    # permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        token = request.GET.get('token')
        waiting_room = request.GET.get('waiting_room')
        room_name = request.GET.get('room_name')
        user = request.user

        if room_name:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                waiting_room,
                {
                    # 프론트에서 이거 보고 매칭 웹소켓 연결 시작해야 됨(룸 네임 주면서,,)
                    'type': 'start_game_with_friend',
                    'waiting_room': waiting_room,
                    'room_name': room_name,
                    'message': 'start game with friend'
                }
            )
            # return Response({"message": "Start Game with friend"}, status=status.HTTP_200_OK)

        if token:
            return render(request, 'game/match.html', {'jwt_token': token, 'waiting_room': waiting_room, 'room_name': room_name})
        else:
            return redirect('/login_page/')