import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # group에 내 채널 추가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


    # 연결 끊기
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # 웹소켓으로부터 메시지 받기
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = text_data_json["sender"]

        # 그룹한테 메시지 보내기
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message", 
                "message": message,
                "sender" : sender,
            }
        )

    # 그룹으로부터 메시지 받기
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        # 웹소켓으로 보내기
        await self.send(text_data=json.dumps({
            # "message": message,
            # "sender" : sender,
            "message" : f'{sender} : {message}'
        }))