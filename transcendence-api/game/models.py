from django.db import models
from users.models import CustomUser

# Create your models here.

class Game(models.Model) :
    user1_score = models.BigIntegerField()
    user2_score = models.BigIntegerField()
    create_time = models.DateTimeField()

    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE)