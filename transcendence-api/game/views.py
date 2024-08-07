from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import CustomUser
from users.serializers import UserScoreSerializer
from .models import Game
from .serializers import GameSerializer
from game.serializers import GameScoreHistorySerializer


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
