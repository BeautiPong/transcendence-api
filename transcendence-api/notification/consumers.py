from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.nickname = self.scope["url_route"]["kwargs"]["nickname"]		#쿼리파라미터
        # user = self.scope.get("user")										#미들웨어커스텀
        self.group_name = f"user_{self.nickname}"


        #데이터베이스 확인
        #유저 상태 온라인으로 변경
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()



    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def request_friend(self, event):
        sender = event["sender"]
        message = event["message"]

        await self.send(text_data=json.dumps({
            'sender': sender,
            'type': 'request_fr',
            'message': message
        }))

