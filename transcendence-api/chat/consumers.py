from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChattingRoom, Message, CustomUser

class ChatConsumer(AsyncJsonWebsocketConsumer) :

    # 연결
    async def connet(self) :
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        
        # room_id를 통해서 group_name을 가져온다 -> 채팅방을 찾아온다
        group_name = self.get_group_name(self.room_id)

        # group에 현재 내 channel을 추가한다 -> 채팅방에 나를 추가한다
        await self.channel_layer.group_add(group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive_message(self, content):
        # 수신된 JSON에서 필요한 정보를 추출합니다.
        message = content['message']
        sender_nickname = content['sender_nickname']
        user1_nickname = content['user1_nickname']
        user2_nickname = content['user2_nickname']

        room = await self.get_or_create_room(user1_nickname, user2_nickname)

        # room_id 속성을 업데이트합니다.
        self.room_id = str(room.id)

        # 그룹 이름을 가져옵니다.
        group_name = self.get_group_name(self.room_id)

        # 수신된 메시지를 데이터베이스에 저장합니다.
        # user1이 sender
        await self.save_message(room, sender_nickname, message)

        # 메시지를 전체 그룹에 전송합니다.
        await self.channel_layer.group_send(group_name, {
            'type': 'chat_message',
            'message': message,
            'sender_nickname': sender_nickname
        })


    # 화면에 메시지랑 sender_nickname 보내는 함수인가(?)
    async def chat_message(self, event):
        message = event['message']
        sender_nickname = event['sender_nickname']
        
        await self.send_json({'message': message, 'sender_nickname': sender_nickname})

    @staticmethod
    def get_group_name(room_id):
        # 방 ID를 사용하여 고유한 그룹 이름을 구성합니다.
        return f"chat_room_{room_id}"
        
    @database_sync_to_async
    def get_or_create_room(self, user1_nickname, user2_nickname):
        user1 = CustomUser.objects.get(nickname = user1_nickname)
        user2 = CustomUser.objects.get(nickname = user2_nickname)

        # user id가 작은 애가 무조건 user1임
        room, created = ChattingRoom.objects.get_or_create(user1 = user1, user2 = user2)
        return room

    @database_sync_to_async
    def save_message(self, room, sender_nickname, message_text):
        
        sender = CustomUser.objects.get(nickname = sender_nickname)

        # 메시지를 생성하고 데이터베이스 저장
        Message.objects.create(room=room, sender=sender, text=message_text)

    @database_sync_to_async
    def check_room_exists(self, room_id):
        # 주어진 ID로 채팅방이 존재하는지 확인합니다.
        return ChattingRoom.objects.filter(id=room_id).exists()