from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from .models import Game
from .serializers import GameSerializer

class RecentGamesView(APIView):
    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        recent_games = Game.objects.filter(user1=user).order_by('-create_time')[:5]
        serializer = GameSerializer(recent_games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
