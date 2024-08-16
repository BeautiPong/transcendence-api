from django.shortcuts import render

from friend.models import Friend
from message.models import Message


# Create your views here.
def get_my_not_check_message(user):
    messages = Message.objects.filter(
        room__in=user.chattingroom_user1.all() | user.chattingroom_user2.all(),
        created_at__gte=user.last_logout,
    ).exclude(sender=user).all()
    return messages