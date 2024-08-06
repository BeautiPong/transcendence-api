from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from .models import ScoreHistory
from .serializers import UserRankingSerializer, OverallRankingSerializer, ScoreHistorySerializer


class OverallRankingsView(APIView):
    def get(self, request):
        users = CustomUser.objects.all().order_by('-score')
        overall_rankings = []

        for idx, user in enumerate(users):
            rank = idx + 1
            overall_rankings.append({
                'nickname': user.nickname,
                'rank': rank
            })

        overall_serializer = OverallRankingSerializer(overall_rankings, many=True)
        return Response(overall_serializer.data, status=status.HTTP_200_OK)

class UserInfoView(APIView):
    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        users = CustomUser.objects.all().order_by('-score')
        user_stats = None

        for idx, u in enumerate(users):
            rank = idx + 1
            if u.id == user.id:
                user_stats = {
                    'nickname': u.nickname,
                    'match_cnt': u.match_cnt,
                    'win_cnt': u.win_cnt,
                    'score': u.score,
                    'rank': rank,
                }

        user_serializer = UserRankingSerializer(user_stats)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

class UserScoreHistoryView(APIView):
    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        score_history = ScoreHistory.objects.filter(user=user).order_by('create_time')
        serializer = ScoreHistorySerializer(score_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
