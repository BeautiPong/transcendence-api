from django.db.models import Q
from django.shortcuts import render

from friend.models import Friend
from message.models import Message
from users.models import CustomUser


def get_users_with_unread_messages(user):
    unread_messages = Message.objects.filter(
        Q(room__in=user.chattingroom_user1.all()) |
        Q(room__in=user.chattingroom_user2.all()),
        read_status='no_read'  # 읽지 않은 상태 필터링
    ).exclude(sender=user)

    senders = unread_messages.values('sender').distinct()

    sender_users = CustomUser.objects.filter(id__in=[sender['sender'] for sender in senders])

    return sender_users