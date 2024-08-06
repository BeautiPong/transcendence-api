from rest_framework import serializers
from .models import Game

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['user1_score', 'user2_score', 'create_time', 'user1', 'user2']
