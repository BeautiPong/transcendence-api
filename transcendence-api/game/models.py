from django.db import models
from users.models import CustomUser

class Game(models.Model) :
    user1_score = models.BigIntegerField()
    user2_score = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='game_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='game_user2')
