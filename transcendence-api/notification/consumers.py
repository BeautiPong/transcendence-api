import aioredis
from django.utils import timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json

import friend.views
import message.views
from friend.views import get_my_friends_request


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if user.is_authenticated:
            await self.set_user_active_status(user, True)
            self.nickname = user.nickname
            self.group_name = f"user_{self.nickname}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # 비동기 컨텍스트에서 Django ORM 호출
            await self.send_notifications(user)
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.set_user_active_status(user, False)
        if self.waiting_room:
            await self.channel_layer.group_discard(self.waiting_room, self.channel_name)
            await self.redis_client.srem(self.waiting_room, user.nickname.encode())

    @database_sync_to_async
    def get_notifications(self, user):
        friend_requests = friend.views.get_my_friends_request(user)
        notifications = []
        for friend_request in friend_requests:
            sender = friend_request.user1.nickname
            notifications.append({
                'type': 'request_friend',
                'sender': sender,
                'message': f"{sender} 님이 친구 요청을 보냈습니다!"
            })

        not_checked_messages = message.views.get_my_not_check_message(user)
        for not_checked_message in not_checked_messages:
            sender = not_checked_message.sender
            notifications.append({
                'type': 'pend_messages',
                'sender': sender,
                'message': f"{not_checked_message.content}"
            })

        return notifications

    async def send_notifications(self, user):
        notifications = await self.get_notifications(user)
        for notification in notifications:
            await self.send(text_data=json.dumps(notification))

    @database_sync_to_async
    def set_user_active_status(self, user, status):
        user.is_online = status
        user.last_logout = timezone.now()
        user.save()

    async def request_friend(self, event):
        sender = event["sender"]
        message = event["message"]

        await self.send(text_data=json.dumps({
            'sender': sender,
            'type': 'request_fr',
            'message': message
        }))

    async def invite_game(self, event):
        sender = event["sender"]
        message = event["message"]

        await self.send(text_data=json.dumps({
            'sender': sender,
            'type': 'invite_game',
            'message': message
        }))

    async def join_room(self, event):
        self.waiting_room = event["waiting_room"]
        room_name = event["room_name"]

        self.redis_client = await aioredis.from_url("redis://redis")
        current_members = await self.redis_client.smembers(self.waiting_room)
        if  self.nickname.encode() not in current_members:
            if len(current_members) >= 2:
                await self.send(text_data=json.dumps({
                    'type': 'room_full',
                    'message': 'The room is full. You cannot join.'
                }))
            else:
                await self.channel_layer.group_add(self.waiting_room, self.channel_name)
                await self.redis_client.sadd(self.waiting_room, self.nickname)

                await self.send(text_data=json.dumps({
                    'type': 'join_room',
                    'waiting_room': self.waiting_room,
                    'room_name': room_name,
                }))

    # 프론트에서 이거 보고 매칭 웹소켓 연결해야 됨
    async def start_game_with_friend(self, event):
        room_name = event["room_name"]
        message = event["message"]

        await self.send(text_data=json.dumps({
            'type': 'start_game_with_friend',
            'room_name': room_name,
            'message': message
        }))
