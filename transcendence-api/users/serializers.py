from rest_framework import serializers
from users.models import CustomUser


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['nickname', 'image', 'match_cnt', 'win_cnt', 'score', 'is_active']

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class UserRankingSerializer(serializers.Serializer):
    rank = serializers.IntegerField()