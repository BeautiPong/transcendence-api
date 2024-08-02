from django.db import models
from users.models import CustomUser

# Create your models here.
class ScoreHistory(models.Model) :
    score = models.BigIntegerField()
    create_time = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)