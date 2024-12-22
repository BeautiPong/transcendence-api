from rest_framework import serializers
from friend.models import Friend


class FriendSerializer(serializers.Serializer):
    
    nickname = serializers.CharField(max_length=6)
