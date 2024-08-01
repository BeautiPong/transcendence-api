from django.db import models
from users.models import CustomUser

class ChattingRoom(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
