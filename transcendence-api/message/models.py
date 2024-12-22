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
    )