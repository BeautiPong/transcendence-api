from django.db import models

# Create your models here.
class ScoreHistory(models.Model) :
    score = models.BigIntegerField()
    create_time = models.DateTimeField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)