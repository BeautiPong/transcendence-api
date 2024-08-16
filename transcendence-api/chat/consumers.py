import json

from channels.generic.websocket import AsyncWebsocketConsumer
from message.models import Message
from chattingRoom.models import ChattingRoom
from users.models import CustomUser
from datetime import datetime
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        user = self.scope['user']

        if user.is_authenticated:
            # await self.set_user_active_status(user, True)

            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = f"chat_{self.room_name}"

            # group에 내 채널 추가
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            # ChattingRoom의 is in chat room true로 변환.
            chattingroom = ChattingRoom.objects.filter(name=self.room_name).first()
            if(chattingroom.user1 == user):
               chattingroom.user1_is_in_chat_room = True
               sender = chattingroom.user2
            elif(chattingroom.user2 == user):
                chattingroom.user2_is_in_chat_room = True
                sender = chattingroom.user1
            
            # sender가 나에게 보낸 안읽은 message 전부 read상태로 바꾸기.
            messages = Message.objects.filter(room=chattingroom, sender=sender, read_status='no_read').all()
            for message in messages:
                message.read_status = 'read'
                message.save()

        else:
            await self.close()

    # def set_status(self, user):
    #     # ChattingRoom의 is in chat room true로 변환.
    #         chattingroom = ChattingRoom.objects.filter(name=self.room_name).first()
    #         if(chattingroom.user1 == user):
    #            chattingroom.user1_is_in_chat_room = True
    #            sender = chattingroom.user2
    #         elif(chattingroom.user2 == user):
    #             chattingroom.user2_is_in_chat_room = True
    #             sender = chattingroom.user1
            
    #         # sender가 나에게 보낸 안읽은 message 전부 read상태로 바꾸기.
    #         messages = Message.objects.filter(room=chattingroom, sender=sender, read_status='no_read').all()
    #         for message in messages:
    #             message.read_status = 'read'
    #             message.save()

    # 연결 끊기
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # ChattingRoom의 is in chat room false로 변환.
        user = self.scope['user']

        chattingroom = ChattingRoom.objects.filter(name=self.room_name).first()
        if(chattingroom.user1 == user):
            chattingroom.user1_is_in_chat_room = False
        elif(chattingroom.user2 == user):
            chattingroom.user2_is_in_chat_room = False



    # 웹소켓으로부터 메시지 받기
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = text_data_json["sender"]
        roomName = text_data_json["roomName"]

        # message 저장
        await self.save_message(roomName, sender, message)

        # 그룹한테 메시지 보내기
        await self.channel_layer.group_send( # 이거 어디서 확인가능? chat_message에서 맞나?
            self.room_group_name, {
                "type": "chat.message", 
                "message": message,
                "sender" : sender,
            }
        )
    
    @database_sync_to_async
    def save_message(self, room_name, sender, message):
        
        room = ChattingRoom.objects.filter(name=room_name).first()
        user = CustomUser.objects.filter(nickname=sender).first()

        # Save message with current time
        message = Message.objects.create(
            room=room,
            sender=user,
            content=message,
            created_at=datetime.now()
        )
        #reciever가 접속 중이면 바로 read로 바꾸기.
        sender = CustomUser.objects.filter(nickname=sender).first()
        if(self.is_user_in_room(sender)):
            message.read_status = 'read'
            message.save()


    # 그룹으로부터 메시지 받기
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        user = self.scope['user']

        if user.is_authenticated:

            if (user.nickname == sender) :
                await self.send(text_data=json.dumps({
                "message" : f'나 : {message}'
                }))
            else :
                await self.send(text_data=json.dumps({
                "message" : f'{sender} : {message}'
                }))


################################################################

    def is_user_in_room(self, user):
        # 그룹 내의 채널 리스트 가져오기
        channel_layer = get_channel_layer()
        group_name = self.room_group_name

        # group_channels는 비동기 메서드이므로 동기적으로 호출해야 함
        channel_list = async_to_sync(channel_layer.group_channels)(group_name)
        
        # 현재 사용자의 채널 이름이 그룹에 포함되어 있는지 확인
        user_channel_name = self.channel_name  # 채널 이름 생성 방식에 맞춰 조정
        return user_channel_name in channel_list
    
