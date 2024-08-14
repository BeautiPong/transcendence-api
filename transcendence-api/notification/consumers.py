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
            notification = await database_sync_to_async(self.get_notifications)(user)
            if notification:
                for friend_request in notification:
                    sender = friend_request.user1.nickname
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'request_friend',
                            'sender': sender,
                            'message': f"{sender} 님이 친구 요청을 보냈습니다!"
                        }
                    )
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.set_user_active_status(user, False)

    @database_sync_to_async
    def get_notifications(self, user):
        return list(friend.views.get_my_friends_request(user))


        # not_checked_messages = message.views.get_my_not_check_message(user)
        # for not_checked_message in not_checked_messages:
        #     sender = not_checked_message.sender
        #     self.send(text_data=json.dumps({
        #         'sender': sender,
        #         'type': 'pend_messages',
        #         'message': f"{not_checked_message.content}"
        #     }))

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

    async def join_game(self, event):
        room_name = event["room_name"]

        await self.channel_layer.group_add(room_name, self.channel_name)

        await self.send(text_data=json.dumps({
            'type': 'join_game',
            'room_name': room_name,
        }))

