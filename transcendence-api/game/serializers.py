from rest_framework import serializers
from .models import Game


class GameScoreHistorySerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Game
        fields = ['user1_score', 'user2_score', 'create_time', 'user1', 'user2']
