from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json


class MatchingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', None)
        self.waiting_room = self.scope['url_route']['kwargs'].get('waiting_room', None)

        if user.is_authenticated:
            self.redis_client = await aioredis.from_url("redis://redis")
            await self.set_user_game_status(user, True)

            await self.accept()

            if not self.room_name:
                await self.channel_layer.group_add(f'user_game_{user.nickname}', self.channel_name)
                self.matchmaking_queue_key = 'matchmaking_queue'

                await self.redis_client.lpush(self.matchmaking_queue_key, user.nickname)
                await self.match_users()

            else:
                players_in_room = await self.check_room_capacity(self.room_name)
                if players_in_room >= 2:
                    await self.close()
                    return

                await self.channel_layer.group_add(self.room_name, self.channel_name)
                await self.check_and_start_game()

        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.set_user_game_status(user, False)
        if self.waiting_room:
            await self.channel_layer.group_discard(self.waiting_room, self.channel_name)
            await self.redis_client.srem(self.waiting_room, user.nickname.encode())
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)


    @database_sync_to_async
    def set_user_game_status(self, user, status):
        user.is_in_game = status
        user.save()

    async def check_room_capacity(self, room_name):
        group_users = await self.redis_client.smembers(f"group_{room_name}")
        return len(group_users)

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
            f"user_game_{user1_nickname}",
            {
                'type': 'join_game',
                'room_name': self.room_name,
            }
        )
        await self.channel_layer.group_send(
            f"user_game_{user2_nickname}",
            {
                'type': 'join_game',
                'room_name': self.room_name,
            }
        )

    async def join_room_or_reject(self):
        players_in_room = await self.check_room_capacity(self.room_name)
        if players_in_room >= 2:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.redis_client.sadd(f"group_{self.room_name}", self.scope['user'].nickname)
        await self.check_and_start_game()

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    async def join_game(self, event):
        room_name = event["room_name"]

        await self.channel_layer.group_add(room_name, self.channel_name)
        await self.check_and_start_game()

        await self.send(text_data=json.dumps({
            'type': 'join_game',
            'room_name': room_name,
        }))

    async def check_and_start_game(self):
        players_in_room = await self.check_room_capacity(self.room_name)
        if players_in_room == 2:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_start',
                    "message": "Game started"
                }
            )
