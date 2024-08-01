from django.db import models
from chattingRoom.models import ChattingRoom

class Message(models.Model):
    room_id = models.ForeignKey(ChattingRoom, on_delete=models.CASCADE)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)