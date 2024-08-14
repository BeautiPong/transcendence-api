from django.db import models
from users.models import CustomUser

# Create your models here.
class Friend(models.Model):
    class Status(models.TextChoices):
        ACCEPT = 'AC', 'Accept'
        REFUSE = 'RF', 'Refuse'
        BLOCK = 'BL', 'Block'
        PEND = 'PN', 'Pend'
        SEND = 'SD', 'Send'
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friend_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friend_user2')
    user1_victory_num = models.IntegerField()
    user2_victory_num = models.IntegerField()
    status = models.CharField(max_length=2,
                              choices=Status.choices)
    create_time = models.DateTimeField(auto_now_add=True)
