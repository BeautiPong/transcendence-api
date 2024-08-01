from django.db import models

# Create your models here.
class Friend(models.Model):
    class Status(models.TextChoices):
        ACCEPT = 'AC', 'Accept'
        REFUSE = 'RF', 'Refuse'
        BLOCK = 'BL', 'Block'
        WAIT = 'WT', 'Wait'
    user1 = models.ForeignKey(User, on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE)
    user1_victory_num = models.IntegerField()
    user2_victory_num = models.IntegerField()
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.WAIT)
    