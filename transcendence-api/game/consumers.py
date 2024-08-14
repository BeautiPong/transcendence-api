from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

class MatchingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', None)

        if user.is_authenticated:

            self.redis_client = await aioredis.from_url("redis://redis")

            await self.accept()
            if not self.room_name:
                await self.channel_layer.group_add(f'user_{user.nickname}', self.channel_name)
                self.matchmaking_queue_key = 'matchmaking_queue'

                await self.redis_client.lpush(self.matchmaking_queue_key, user.nickname)
                await self.match_users()

            else:
                await self.channel_layer.group_add(self.room_name, self.channel_name)
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type': 'game_start',
                        'message': 'Game started with friends'
                    }
                )
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass
        # await self.redis_client.lrem(self.matchmaking_queue_key, 0, self.scope['user'].nickname)
        # if self.room_name:
        #     await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def match_users(self):
        users = await self.redis_client.lrange(self.matchmaking_queue_key, 0, 1)

        if len(users) >= 2:
            user1_nickname = users[0].decode('utf-8')
            user2_nickname = users[1].decode('utf-8')

            self.room_name = f'game_{user1_nickname}_{user2_nickname}'
            await self.create_game_room(user1_nickname, user2_nickname)

            await self.redis_client.lrem(self.matchmaking_queue_key, 0, user1_nickname)
            await self.redis_client.lrem(self.matchmaking_queue_key, 0, user2_nickname)

    async def create_game_room(self, user1_nickname, user2_nickname):
        await self.channel_layer.group_send(
            f"user_{user1_nickname}",
            {
                'type': 'join_game',
                'room_name': self.room_name,
            }
        )
        await self.channel_layer.group_send(
            f"user_{user2_nickname}",
            {
                'type': 'join_game',
                'room_name': self.room_name,
            }
        )
        await self.channel_layer.group_send(
            f"{self.room_name}",
            {
                'type': 'game_start',
                "message": "Game started"
            }
        )


    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))


    async def join_game(self, event):
        room_name = event["room_name"]

        await self.channel_layer.group_add(room_name, self.channel_name)

        await self.send(text_data=json.dumps({
            'type': 'join_game',
            'room_name': room_name,
        }))
