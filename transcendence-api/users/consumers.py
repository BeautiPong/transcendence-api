from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json


class LoginConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.nickname = self.scope["url_route"]["kwargs"]["nickname"]		#쿼리파라미터
        # user = self.scope.get("user")										#미들웨어커스텀
        self.group_name = f"group_{self.nickname}"

		
        #데이터베이스 확인
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()


    
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def add_friend(self, close_code):

       await self.channel_layer.group_send(
#             종민그룹, {"type": "chat.message", "message": message}
       )

    # 클라이언트에게 message 보내주기
    async def send_alarm(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))



#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#
#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.group_name, {"type": "chat.message", "message": message}
#         )
#
#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))
#
#
#
# import json
# from channels.db import database_sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
#
# from .models import Alarm
# from .serializers import AlarmSerializer
#
#
# def get_alarm(user):
#     notifications = Alarm.objects.filter(user=user)
#     serializer = AlarmSerializer(notifications, many=True)
#     return serializer.data
#
#
# class AlarmConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         user = self.scope.get("user")
#         self.group_name = f"user{user.id}"
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         alarms = await database_sync_to_async(get_alarm)(user)
#
#         if alarms:
#             await self.channel_layer.group_send(
#                 self.group_name, {"type": "send_alarm", "message": alarms}
#             )
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)
#
