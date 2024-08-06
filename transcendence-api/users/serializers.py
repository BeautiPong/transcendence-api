from rest_framework import serializers
from users.models import CustomUser


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['nickname', 'image', 'match_cnt', 'win_cnt', 'score', 'is_active']

class UserRankingSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
