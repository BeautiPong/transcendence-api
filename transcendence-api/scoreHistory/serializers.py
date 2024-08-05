from rest_framework import serializers
from scoreHistory.models import ScoreHistory

class ScoreHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreHistory
        fields = ['score', 'create_time']

class UserRankingSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    match_cnts = serializers.IntegerField()
    win_cnts = serializers.IntegerField()
    score = serializers.IntegerField()
    rank = serializers.IntegerField()

class OverallRankingSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    rank = serializers.IntegerField()
