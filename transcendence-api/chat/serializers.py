
from rest_framework import serializers
from message.models import Message
from chattingRoom.models import ChattingRoom

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ChatRoomSerializer(serializers.ModelSerializer):
    latest_message = serializers.SerializerMethodField()  # 최신 메시지 필드를 동적으로 가져옵니다.
    opponent_nickname = serializers.SerializerMethodField()
    user1_nickname = serializers.SerializerMethodField()
    user2_nickname = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True, source="messages.all")  # 해당 채팅방의 메시지 목록을 가져옵니다.

    class Meta:
        model = ChattingRoom 
        fields = ('id', 'user1', 'user2', 'latest_message', 'opponent_nickname', 'user1_nickname', 'user2_nickname', 'messages')

    # 최신 메시지 가져옴
    def get_latest_message(self, obj):
        latest_message = obj.messages.order_by('-timestamp').first()
        if latest_message:
            return {
                'id': latest_message.id,
                'content': latest_message.content,
                'timestamp': latest_message.timestamp,
                'sender': latest_message.sender.nickname
            }
        return None

    # 상대방의 닉네임을 반환
    def get_opponent_nickname(self, obj):
        current_user = self.context['request'].user
        if obj.user1 == current_user:
            return obj.user2.nickname
        return obj.user1.nickname

    def get_user1_nickname(self, obj):
        return obj.user1.nickname

    def get_user2_nickname(self, obj):
        return obj.user2.nickname