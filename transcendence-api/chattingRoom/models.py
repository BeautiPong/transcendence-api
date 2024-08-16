from django.db import models
from users.models import CustomUser

class ChattingRoom(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chattingroom_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chattingroom_user2')
    name =  models.TextField(null=True, blank=True)