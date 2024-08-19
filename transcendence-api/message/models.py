from django.db import models
from chattingRoom.models import ChattingRoom
from users.models import CustomUser

class Message(models.Model):
    READ_STATUS_CHOICES = [
        ('read', 'Read'),
        ('no_read', 'No Read'),
    ]
    

    room = models.ForeignKey(ChattingRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_status = models.CharField(
        max_length=10,
        choices=READ_STATUS_CHOICES,
        default='no_read'
    )#reciever가 읽으면 상태 바뀌도록. -> 읽었는지 어떻게 알지? -> 채팅방에 들어와있는지 안들어와있는지 확인 후 상태 변경.