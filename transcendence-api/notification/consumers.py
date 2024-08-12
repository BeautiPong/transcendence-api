from venv import logger

from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if user.is_authenticated:
            # 로그에 유저 정보 출력
            self.nickname = user.nickname
            self.group_name = f"user_{self.nickname}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()



    async def disconnect(self, close_code):
        pass
        # await self.channel_layer.group_discard(self.group_name, self.channel_name)

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
