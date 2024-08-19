from django.db import models
from users.models import CustomUser

class ChattingRoom(models.Model):

    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chattingroom_user1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chattingroom_user2')
    name =  models.TextField(null=True, blank=True)
    user1_is_in_chat_room = models.BooleanField(
        default=False,
    )
    user2_is_in_chat_room = models.BooleanField(
        default=False,  # 기본값은 채팅방에 없는 상태
    )
    #채팅룸에 들어오면 sender가 보낸 message 전부 read로 바꾸기.