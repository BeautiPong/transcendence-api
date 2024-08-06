from rest_framework import serializers
from scoreHistory.models import ScoreHistory

class ScoreHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreHistory
        fields = ['score', 'create_time']

class OverallRankingSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=30)
    rank = serializers.IntegerField()
