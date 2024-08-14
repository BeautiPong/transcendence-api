from rest_framework import serializers
from friend.models import Friend
# from users.models import CustomUser


class FriendSerializer(serializers.Serializer):
    
    nickname = serializers.CharField(max_length=6)



# class ChatRoomSerializer():
    
#     name = serializers.CharField(max_length=6)
