from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from .models import Game
from .serializers import GameSerializer
from game.serializers import GameScoreHistorySerializer


class SaveGameView(APIView):
    def post(self, request):
        data = request.data
        try:
            user1 = CustomUser.objects.get(nickname=data['user1_nickname'])
            user2 = CustomUser.objects.get(nickname=data['user2_nickname'])
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        game_data = {
            'user1': user1,
            'user2': user2,
            'user1_score': data['user1_score'],
            'user2_score': data['user2_score']
        }

        serializer = GameScoreHistorySerializer(data=game_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
class RecentGamesView(APIView):
    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        recent_games = Game.objects.filter(user1=user).order_by('-create_time')[:5]
        serializer = GameSerializer(recent_games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
