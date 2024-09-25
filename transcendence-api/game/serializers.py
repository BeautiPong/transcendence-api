from rest_framework import serializers
from .models import Game
from users.serializers import UserInfoSerializer

class GameScoreHistorySerializer(serializers.ModelSerializer):

    user1 = UserInfoSerializer(read_only=True)
    user2 = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = ['user1', 'user2', 'user1_score', 'user2_score']

    def create(self, validated_data):
        game1 = Game(**validated_data)
        game1.save()
        game2 = Game(
            user1=validated_data['user2'],
            user2=validated_data['user1'],
            user1_score=validated_data['user2_score'],
            user2_score=validated_data['user1_score']
        )
        game2.save()
        return game1


class GameSerializer(serializers.ModelSerializer):

    user1_nickname = serializers.SerializerMethodField()
    user1_image = serializers.SerializerMethodField()
    user2_nickname = serializers.SerializerMethodField()
    user2_image = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['user1_score', 'user2_score', 'create_time', 
                  'user1_nickname', 'user1_image', 
                  'user2_nickname', 'user2_image']

    def get_user1_nickname(self, obj):
        return obj.user1.nickname

    def get_user1_image(self, obj):
        if obj.user1.image:
            return obj.user1.image.url  # 이미지 URL 반환
        return None

    def get_user2_nickname(self, obj):
        return obj.user2.nickname

    def get_user2_image(self, obj):
        if obj.user2.image:
            return obj.user2.image.url  # 이미지 URL 반환
        return None