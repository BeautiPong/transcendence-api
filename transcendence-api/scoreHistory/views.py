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
        users_with_matches = CustomUser.objects.filter(match_cnt__gt=0).order_by('-score')
        users_without_matches = CustomUser.objects.filter(match_cnt=0).order_by('-score')
        
        overall_rankings = []
        
        # 경기 수가 있는 사용자들
        for idx, user in enumerate(users_with_matches):
            rank = idx + 1
            overall_rankings.append({
                'nickname': user.nickname,
                'image' : user.image, 
                'score' : user.score,
                'rank': rank
            })
        
        # 경기 수가 없는 사용자들 (리스트의 끝에 추가)
        for user in users_without_matches:
            overall_rankings.append({
                'nickname': user.nickname,
                'image' :  user.image, 
                'score' : user.score,
                'rank': None
            })
        
        overall_serializer = OverallRankingSerializer(overall_rankings, many=True, context={'request': request})
        return Response(overall_serializer.data, status=status.HTTP_200_OK)


class UserScoreHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, nickname):
        try:
            user = CustomUser.objects.get(nickname=nickname)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        score_history = ScoreHistory.objects.filter(user=user).order_by('create_time')[:5]

        if not score_history:
            # 기본 점수 추가
            score_history = [
                {
                    'user': user.id,
                    'score': 1000,
                    'create_time': user.date_joined
                }
            ]
            serializer = ScoreHistorySerializer(data=score_history, many=True)
            serializer.is_valid(raise_exception=True)
        else:
            serializer = ScoreHistorySerializer(score_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
