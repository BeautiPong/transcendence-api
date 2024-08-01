from django.db import models
from users.models import CustomUser

# Create your models here.
class ScoreHistory(models.Model) :
    score = models.BigIntegerField()
    create_time = models.DateTimeField()

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)