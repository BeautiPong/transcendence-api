from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import CustomUser
from scoreHistory.models import ScoreHistory
from .serializers import OverallRankingSerializer, ScoreHistorySerializer

class OverallRankingsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        users = CustomUser.objects.all().order_by('-score')
        overall_rankings = []

        for idx, user in enumerate(users):
            rank = idx + 1
            rank_value = None if user.match_cnt == 0 else rank
            
            overall_rankings.append({
                'nickname': user.nickname,
                'rank': rank_value
            })

        overall_serializer = OverallRankingSerializer(overall_rankings, many=True)
        return Response(overall_serializer.data, status=status.HTTP_200_OK)

class UserScoreHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        score_history = ScoreHistory.objects.filter(user=user).order_by('create_time')
        serializer = ScoreHistorySerializer(score_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
