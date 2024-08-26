from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import aioredis
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import aioredis
import json

from channels.db import database_sync_to_async
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
            await self.channel_layer.group_add(f'user_game_{user.nickname}', self.channel_name)

            await self.accept()

            if not self.room_name:
                self.matchmaking_queue_key = 'matchmaking_queue'
                await self.redis_client.lpush(self.matchmaking_queue_key, user.nickname)
                await self.match_users()
            else:
                await self.add_user_to_room(self.room_name, user.nickname)
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
            await self.remove_user_from_room(self.room_name, user.nickname)
        await self.channel_layer.group_discard(f'user_game_{user.nickname}', self.channel_name)

    @database_sync_to_async
    def set_user_game_status(self, user, status):
        user.is_in_game = status
        user.save()

    async def check_room_capacity(self, room_name):
        # 방에 있는 사용자 수를 확인하기 위해 Redis의 set 크기를 확인
        return await self.redis_client.scard(f"group_{room_name}")

    async def add_user_to_room(self, room_name, nickname):
        # 사용자를 방에 추가 (Redis set 사용)
        await self.redis_client.sadd(f"group_{room_name}", nickname)

    async def remove_user_from_room(self, room_name, nickname):
        # 사용자를 방에서 제거 (Redis set 사용)
        await self.redis_client.srem(f"group_{room_name}", nickname)

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
        await self.channel_layer.group_add(self.room_name, f'user_game_{user1_nickname}')
        await self.channel_layer.group_add(self.room_name, f'user_game_{user2_nickname}')

        await self.add_user_to_room(self.room_name, user1_nickname)
        await self.add_user_to_room(self.room_name, user2_nickname)

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

    async def join_game(self, event):
        room_name = event["room_name"]

        await self.channel_layer.group_add(room_name, self.channel_name)
        await self.add_user_to_room(room_name, self.scope['user'].nickname)

        await self.send(text_data=json.dumps({
            'type': 'join_game',
            'room_name': room_name,
        }))
        await self.check_and_start_game()

    async def check_and_start_game(self):
        players_in_room = await self.check_room_capacity(self.room_name)
        if players_in_room == 2:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_start',
                    'room_name': self.room_name,
                    "message": "Game started"
                }
            )
            if self.waiting_room:
                await self.channel_layer.group_discard(self.waiting_room, self.channel_name)

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_start',
            'room_name': event['room_name'],
            'message': event['message']
        }))


from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0.01, 'z': -0.02}
        self.paddle_positions = {'player1': 0, 'player2': 0}
        self.current_player = 'player1'
        self.room_name = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'game_start',
                "message": "Game started"
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'move':
            direction = data['direction']
            player = data['player']

            if player == 'player1':
                self.paddle_positions['player1'] += -0.05 if direction == 'left' else 0.05
            elif player == 'player2':
                self.paddle_positions['player2'] += -0.05 if direction == 'left' else 0.05

    async def game_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': event['message']
        }))
        await self.game_loop()

    async def game_loop(self):
        while True:
            await self.update_ball_position()
            await self.send_game_state()
            await asyncio.sleep(0.01)

    async def update_ball_position(self):
        self.ball_position['x'] += self.ball_velocity['x']
        self.ball_position['y'] += self.ball_velocity['y']
        self.ball_position['z'] += self.ball_velocity['z']

        if self.ball_position['z'] <= -1.0 or self.ball_position['z'] >= 1.0:
            if self.current_player == 'player1' and self.ball_position['z'] <= -1.0:
                await self.handle_collision('player1')
            elif self.current_player == 'player2' and self.ball_position['z'] >= 1.0:
                await self.handle_collision('player2')

        if abs(self.ball_position['x']) >= 0.5:
            self.ball_velocity['x'] = -self.ball_velocity['x']

        self.ball_velocity['y'] -= 0.0001

    async def handle_collision(self, player):
        if player == 'player1' and abs(self.ball_position['x'] - self.paddle_positions['player1']) < 0.2:
            self.ball_velocity['z'] = -self.ball_velocity['z']
            self.current_player = 'player2'
        elif player == 'player2' and abs(self.ball_position['x'] - self.paddle_positions['player2']) < 0.2:
            self.ball_velocity['z'] = -self.ball_velocity['z']
            self.current_player = 'player1'
        else:
            await self.end_game(winner='player2' if player == 'player1' else 'player1')

    async def send_game_state(self):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'ball_position': self.ball_position,
            'paddle_positions': self.paddle_positions
        }))

    async def end_game(self, winner):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': winner
        }))
        await self.close()