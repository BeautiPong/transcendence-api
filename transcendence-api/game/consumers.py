from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


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


import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import aioredis

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
import aioredis

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import aioredis

import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json


import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json


import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import aioredis
import json

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.player_name = self.user.nickname
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        self.redis_client = await aioredis.from_url("redis://redis")

        # 게임 상태 변수 초기화
        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': -0.02}
        self.paddle_positions = {'player1': 0, 'player2': 0}
        self.scores = {'player1': 0, 'player2': 0}
        self.game_active = True  # 게임이 활성 상태인지 추적

        # 플레이어를 방에 추가
        await self.add_user_to_room(self.room_name, self.player_name)
        players_in_room = await self.check_room_capacity(self.room_name)

        # 플레이어 설정 및 클라이언트에게 역할 전달
        if players_in_room == 1:
            self.current_player = 'player1'
            print(f"{self.player_name} is player1 in room {self.room_name}")
            await self.send(text_data=json.dumps({
                'type': 'assign_role',
                'role': 'player1'
            }))
        elif players_in_room == 2:
            self.current_player = 'player2'
            print(f"{self.player_name} is player2 in room {self.room_name}")
            await self.send(text_data=json.dumps({
                'type': 'assign_role',
                'role': 'player2'
            }))
            await self.start_game()

    async def disconnect(self, close_code):
        print(f"User {self.player_name} disconnected with code {close_code}")
        await self.remove_user_from_room(self.room_name, self.player_name)
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        if not self.game_active:
            return  # 게임이 종료된 경우 더 이상 입력을 처리하지 않음

        data = json.loads(text_data)
        if data['type'] == 'move':
            direction = data['direction']
            player = data['player']
            print(f"Received move command: {direction} for {player}")

            # 패들 움직임 범위 제한 및 위치 업데이트
            if player == 'player1':
                self.paddle_positions['player1'] = max(-0.75, min(0.75, self.paddle_positions['player1'] + (-0.05 if direction == 'left' else 0.05)))
            elif player == 'player2':
                self.paddle_positions['player2'] = max(-0.75, min(0.75, self.paddle_positions['player2'] + (-0.05 if direction == 'left' else 0.05)))

            await self.send_game_state()

    async def start_game(self):
        print(f"Starting game loop in room {self.room_name}")
        asyncio.create_task(self.game_loop())

    async def game_loop(self):
        try:
            while self.game_active:
                await self.update_ball_position()
                await self.send_game_state()
                await asyncio.sleep(0.01)  # 게임 속도 조절
        except Exception as e:
            print(f"Error in game_loop: {e}")
            await self.close()

    async def update_ball_position(self):
        try:
            if not self.game_active:
                return  # 게임이 종료된 경우 공 위치 업데이트 중지

            self.ball_position['x'] += self.ball_velocity['x']
            self.ball_position['z'] += self.ball_velocity['z']

            # x축에서 벽에 부딪힐 경우 반사
            if abs(self.ball_position['x']) >= 0.75:
                self.ball_velocity['x'] = -self.ball_velocity['x']

            # z축에서 패들에 부딪힐 경우 반사 또는 득점 처리
            if self.ball_position['z'] >= 1.5:
                if abs(self.ball_position['x'] - self.paddle_positions['player1']) <= 0.25:
                    # 공이 패들의 중앙에서 얼마나 떨어져 있는지 계산
                    offset = self.ball_position['x'] - self.paddle_positions['player1']
                    # x 축 속도에 오프셋을 추가하여 궤도를 변경
                    self.ball_velocity['x'] += offset * 0.1  # 여기서 0.1은 공이 튕기는 각도를 조절하는 값
                    self.ball_velocity['z'] = -self.ball_velocity['z']
                else:
                    self.scores['player2'] += 1
                    await self.reset_ball()

            elif self.ball_position['z'] <= -1.5:
                if abs(self.ball_position['x'] - self.paddle_positions['player2']) <= 0.25:
                    offset = self.ball_position['x'] - self.paddle_positions['player2']
                    self.ball_velocity['x'] += offset * 0.1
                    self.ball_velocity['z'] = -self.ball_velocity['z']
                else:
                    self.scores['player1'] += 1
                    await self.reset_ball()

            # 게임 종료 조건: 점수가 10점에 도달한 경우
            if self.scores['player1'] >= 10:
                await self.end_game(winner='player1')
            elif self.scores['player2'] >= 10:
                await self.end_game(winner='player2')

        except Exception as e:
            print(f"Error in update_ball_position: {e}")
            await self.close()

    async def reset_ball(self):
        if not self.game_active:
            return  # 게임이 종료된 경우 공 위치 초기화 중지

        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': -0.02}
        await self.send_game_state()

    async def send_game_state(self):
        try:
            if not self.game_active:
                return  # 게임이 종료된 경우 게임 상태 전송 중지

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'send_update',
                    'ball_position': self.ball_position,
                    'paddle_positions': self.paddle_positions,
                    'scores': self.scores
                }
            )
        except Exception as e:
            print(f"Error in send_game_state: {e}")
            await self.close()

    async def send_update(self, event):
        ball_position = event['ball_position']
        paddle_positions = event['paddle_positions']
        scores = event['scores']
        self.ball_position = event['ball_position']
        self.paddle_positions = paddle_positions
        self.scores = scores

        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'ball_position': ball_position,
            'paddle_positions': paddle_positions,
            'scores': scores,
        }))

    async def end_game(self, winner):
        self.game_active = False  # 게임을 비활성화하여 루프 중지
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'game_over',
                'winner': winner
            }
        )

    async def game_over(self, event):
        winner = event['winner']
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': winner
        }))

    async def check_room_capacity(self, room_name):
        return await self.redis_client.scard(f"group_{room_name}")

    async def add_user_to_room(self, room_name, nickname):
        await self.redis_client.sadd(f"group_{room_name}", nickname)

    async def remove_user_from_room(self, room_name, nickname):
        try:
            await self.redis_client.srem(f"group_{room_name}", nickname)
        except Exception as e:
            print(f"Error in remove_user_from_room: {e}")
