import aioredis
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.utils import json

redis_client = aioredis.from_url("redis://localhost")

class MatchingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', None)

        if user.is_authenticated:
            await self.accept()
            if not self.room_name:
                self.matchmaking_queue_key = 'matchmaking_queue'

                await redis_client.lpush(self.matchmaking_queue_key, user.nickname)
                await self.match_users()
            else:
                await self.channel_layer.group_send(
                    f'game_{self.room_name}',
                    {
                        'type': 'game_start',
                        'message': 'Game started'
                    }
                )
        else:
            await self.close()

    async def disconnect(self, close_code):
        # 대기열에서 사용자 제거
        await redis_client.lrem(self.matchmaking_queue_key, 0, self.user.nickname)
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def match_users(self):
        users = await redis_client.lrange(self.matchmaking_queue_key, 0, 1)
        if len(users) >= 2:
            user1_nickname = users[0].decode('utf-8')  # Redis에서는 byte를 반환하므로 decode 필요
            user2_nickname = users[1].decode('utf-8')

            self.room_name = f'game_{user1_nickname}_{user2_nickname}'
            await self.create_game_room(user1_nickname, user2_nickname)

            await redis_client.lrem(self.matchmaking_queue_key, 0, user1_nickname.encode('utf-8'))
            await redis_client.lrem(self.matchmaking_queue_key, 0, user2_nickname.encode('utf-8'))

    async def create_game_room(self, user1_nickname, user2_nickname):
        await self.channel_layer.group_add(self.room_name, self.channel_name)  # 사용자 1 추가
        # 다음과 같이 user2가 속한 다른 소비자에서도 group_add를 호출해야 합니다.
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'game_start',
                'message': f'Game started with {user1_nickname} and {user2_nickname}'
            }
        )

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
