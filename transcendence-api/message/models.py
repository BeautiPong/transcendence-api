from django.db import models
from chattingRoom.models import ChattingRoom
from users.models import CustomUser

class Message(models.Model):
    room_id = models.ForeignKey(ChattingRoom, on_delete=models.CASCADE)
    sender_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)