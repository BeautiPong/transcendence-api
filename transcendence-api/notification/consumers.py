import aioredis
from django.utils import timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json

import friend.views
import message.views

from friend.views import get_my_friends_request
from friend.models import Friend
from users.models import CustomUser
import logging

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        if user.is_authenticated:
            await self.set_user_active_status(user, True)
            self.nickname = user.nickname
            self.group_name = f"user_{self.nickname}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

             # 친구들에게 나의 상태 알림 전송
            await self.notify_friends_status(user, 'online')

            # 비동기 컨텍스트에서 Django ORM 호출
            await self.send_notifications(user)
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        logger = logging.getLogger(__name__)

        if user.is_authenticated:
            try:
                user = await self.refresh_user(user)  # 사용자 객체 다시 가져오기
                await self.set_user_active_status(user, False)
                # 친구들에게 나의 상태 알림 전송
                await self.notify_friends_status(user, 'offline')
            except Exception as e:
                logger.error(f"Error in disconnect: {e}")

            # group_discard를 인증된 사용자 블록 내부로 이동
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def notify_friends_status(self, user, status):
        friends = await self.get_friends_list(user)
        for friend in friends:
            friend_group_name = f"user_{friend.nickname}"
            await self.channel_layer.group_send(
                friend_group_name,
                {
                    'type': 'status_message',
                    'sender' : f"{user.nickname}",
                    'message': f"{user.nickname} is {status}",
                    'status' : f"{status}"
                }
            )

    async def notify_message(self, event):
        sender = event['sender']
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'notify_message',
            'sender': sender,
            'message': message
        }))

    @database_sync_to_async
    def get_friends_list(self, user):
        # 비동기로 친구 리스트 가져오기 (예시로 Django ORM 사용)
        friend_with_user1 = Friend.objects.filter(user1=user, status=Friend.Status.ACCEPT)
        friend_list = [friend.user2 for friend in friend_with_user1]
        return friend_list

    @database_sync_to_async
    def is_user_blocked(self, user1, user2):
        # user1이 user2를 차단했는지 확인
        return Friend.objects.filter(
            user1=user1,
            user2=user2,
            status=Friend.Status.BLOCK
        ).exists()

    async def status_message(self, event):
        message = event['message']
        sender = event['sender']
        status = event['status']
        # 메시지를 JSON 형식으로 전송
        await self.send(text_data=json.dumps({'type' : "status_message", 'sender' : sender, 'message': message, 'status' : status}))

    @database_sync_to_async
    def refresh_user(self, user):
        return user.__class__.objects.get(pk=user.pk)

    @database_sync_to_async
    def get_user_by_nickname(self, nickname):
        return CustomUser.objects.filter(nickname=nickname).first()

    async def receive(self, text_data):
        logger = logging.getLogger(__name__)
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        data = json.loads(text_data)

        if 'type' in data:
            if data['type'] == 'invite_game':
                sender = data.get('sender')  # 'sender' 필드를 추출
                receiver = data.get('receiver')  # 'receiver' 필드를 추출
                message = data.get('message')  # 'message' 필드를 추출


                #일단 초대 알람 보내기
                await self.channel_layer.group_send(
                    f"user_{receiver}", {
                    "type": "invite_game",
                    "sender" : sender,
                    "receiver" : receiver,
                    "message": message,
                    }
                )

            elif data['type'] == 'access_invitation':
                sender = data.get('sender')  # 'sender' 필드를 추출
                receiver = data.get('receiver')  # 'receiver' 필드를 추출
                message = data.get('message')  # 'message' 필드를 추출

                await self.channel_layer.group_send(
                    f"user_{receiver}", {
                    "type": "access_invitation",
                    "sender" : sender,
                    "receiver" : receiver,
                    "message": message,
                    }
                )

            elif data['type'] == 'navigateToGamePage':
                guest = data.get('guest')
                room_name = data.get('room_name')
                await self.channel_layer.group_send(
                    f"user_{guest}", {
                    "type": "navigateToGamePage",
                    "room_name": room_name,
                    "guest" : guest,
                    }
                )
            elif data['type'] == 'leaveWaitingRoom':
                leaver = data.get('leaver')
                remainder = data.get('remainder')
                await self.channel_layer.group_send(
                    f"user_{remainder}", {
                    "type": "leaveWaitingRoom",
                    "leaver": leaver,
                    "remainder": remainder
                    }
                )

            elif data['type'] == 'get_notifications':
                user = self.scope['user']

                await self.send_notifications(user)

            elif data['type'] == 'notify_status_message':
                user = self.scope['user']
                status = data.get('status')

                await self.notify_friends_status(user, status)

            elif data['type'] == 'notify_message_sent':
                sender = data.get('sender')
                receiver = data.get('receiver')
                message = data.get('message')

                # receiver와 sender 객체 가져오기
                receiver_object = await self.get_user_by_nickname(receiver)
                sender_object = await self.get_user_by_nickname(sender)

                # 상대가 나를 차단했는지 확인
                is_blocked_by_receiver = await self.is_user_blocked(receiver_object, sender_object)

                # 만약 차단한 상태라면 메시지를 보내지 않음
                if is_blocked_by_receiver:
                    return

                # 차단되지 않았다면 메시지를 전송
                await self.channel_layer.group_send(
                    f"user_{receiver}", {
                        'type': 'notify_message',
                        'sender': sender,
                        'message': message
                    }
                )




    async def invite_game(self, event):
        sender = event["sender"]
        message = event["message"]
        receiver = event['receiver']

        await self.send(text_data=json.dumps({
            'type': 'invite_game',
            'sender': sender,
            "receiver" : receiver,
            'message': message
        }))

    async def access_invitation(self, event):
        sender = event["sender"]
        message = event["message"]
        receiver = event['receiver']

        await self.send(text_data=json.dumps({
            'type': 'access_invitation',
            'sender': sender,
            "receiver" : receiver,
            'message': message
        }))

    async def navigateToGamePage(self, event):
        guest = event["guest"]
        room_name = event["room_name"]
        await self.send(text_data=json.dumps({
            'type': 'navigateToGamePage',
            'room_name': room_name,
            'guest': guest
        }))

    async def leaveWaitingRoom(self, event):
        leaver = event["leaver"]
        remainder = event["remainder"]
        await self.send(text_data=json.dumps({
            'type': 'leaveWaitingRoom',
            'leaver': leaver,
            'remainder': remainder
        }))

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

        not_checked_users = message.views.get_users_with_unread_messages(user)
        for sender in not_checked_users:
            notifications.append({
                'type': 'pend_messages',
                'sender': sender.nickname,
                'message': f"{sender.nickname} 님으로부터 읽지 않은 메시지가 있습니다."
            })

        return notifications

    async def send_notifications(self, user):
        notifications = await self.get_notifications(user)
        for notification in notifications:
            await self.send(text_data=json.dumps(notification))

    @database_sync_to_async
    def set_user_active_status(self, user, status):
        user.is_online = status
        if not status:
            user.last_logout = timezone.now()
        user.save()

    async def request_friend(self, event):
        sender = event["sender"]
        message = event["message"]
        tag = event["tag"]

        await self.send(text_data=json.dumps({
            'sender': sender,
            'type': 'request_fr',
            'message': message,
            'tag' : tag
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

