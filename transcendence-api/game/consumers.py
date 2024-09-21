import asyncio
import random
import aioredis
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.db import transaction

from friend.models import Friend
from scoreHistory.models import ScoreHistory
from users.models import CustomUser
from .models import Game


class MatchingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', None)
        self.waiting_room = self.scope['url_route']['kwargs'].get('waiting_room', None)

        if self.user.is_authenticated:
            if self.user.is_in_game:
                self.close()
                return
            self.redis_client = await aioredis.from_url("redis://redis")
            await self.channel_layer.group_add(f'user_game_{self.user.nickname}', self.channel_name)
            await self.accept()

            if not self.room_name:
                self.matchmaking_queue_key = 'matchmaking_queue'
                await self.redis_client.lpush(self.matchmaking_queue_key, self.user.nickname)
                await self.match_users()
            else:
                await self.add_user_to_room(self.room_name, self.user.nickname)
                players_in_room = await self.check_room_capacity(self.room_name)
                if players_in_room > 2:
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

        # Redis 클라이언트가 설정된 경우에만 Redis 관련 작업을 수행
        if hasattr(self, 'redis_client') and self.redis_client:
            if self.waiting_room:
                await self.channel_layer.group_discard(self.waiting_room, self.channel_name)
                await self.redis_client.srem(self.waiting_room, user.nickname.encode())
            if self.room_name:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
                await self.remove_user_from_room(self.room_name, user.nickname)
            else:
                await self.redis_client.lrem(self.matchmaking_queue_key, 0, user.nickname)

        await self.channel_layer.group_discard(f'user_game_{user.nickname}', self.channel_name)

    @database_sync_to_async
    def set_user_game_status(self, user, is_in_game):
        try:
            with transaction.atomic():
                # 유저 상태를 select_for_update로 잠금
                user = CustomUser.objects.select_for_update().get(id=user.id)
                user.is_in_game = is_in_game
                user.save()
        except Exception as e:
            print(f"Error updating user game status: {e}")



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

            self.room_name = f'{user1_nickname}_{user2_nickname}'
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
        self.room_name = event["room_name"]
        room_name = event["room_name"]

        await self.channel_layer.group_add(room_name, self.channel_name)
        await self.add_user_to_room(room_name, self.scope['user'].nickname)

        await self.send(text_data=json.dumps({
            'type': 'join_game',
            'room_name': room_name,
        }))
        await self.check_and_start_game()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'disconnect_matching':
            # 매칭 WebSocket 연결을 종료
            await self.close()


    async def check_and_start_game(self):
        players_in_room = await self.check_room_capacity(self.room_name)
        if players_in_room == 2:
            # 게임이 시작될 때 매칭 WebSocket 연결을 종료

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_start',
                    'room_name': 'game_' + self.room_name,
                    "message": "Game started"
                }
            )

            await self.send(text_data=json.dumps({
                'type': 'disconnect_matching',  # 연결 종료 신호
            }))
            if self.waiting_room:
                await self.channel_layer.group_discard(self.waiting_room, self.channel_name)


    async def game_start(self, event):
        # print("self.room_name", self.room_name)
        # print("event['room_name']", event['room_name'])
        if(self.room_name and 'room_name' in event):
            await self.send(text_data=json.dumps({
                'type': 'game_start',
                'room_name': event['room_name'],
                'message': event['message']
            }))


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.player_name = self.user.nickname

        if self.user.is_authenticated:
            if self.user.is_in_game:
                self.close()
                return
        # room_name을 '_'로 분리하여 두 플레이어의 닉네임을 가져옵니다.
        _, name1, name2 = self.room_name.split('_')

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
        await self.set_user_game_status(self.user, True)
        if players_in_room == 1:
            if self.player_name == name1:
                self.players = {'player1': name1, 'player2': name2}
            else:
                self.players = {'player1': name2, 'player2': name1}

            # print(f"{self.player_name} is player1 in room {self.room_name}")
            await self.send(text_data=json.dumps({
                'type': 'assign_role',
                'role': 'player1'
            }))
        elif players_in_room == 2:
            if self.player_name == name1:
                self.players = {'player1': name2, 'player2': name1}
            else:
                self.players = {'player1': name1, 'player2': name2}

            # print(f"{self.player_name} is player2 in room {self.room_name}")
            await self.send(text_data=json.dumps({
                'type': 'assign_role',
                'role': 'player2'
            }))
            await self.start_game()

    async def disconnect(self, close_code):
        # 플레이어를 방에서 제거
        if self.game_active:
            if self.player_name == self.players['player1']:
                self.scores['player1'] = 0
                self.scores['player2'] = 5
                await self.end_game(winner=self.players['player2'])
            else:
                self.scores['player1'] = 5
                self.scores['player2'] = 0
                await self.end_game(winner=self.players['player1'])

        await self.remove_user_from_room(self.room_name, self.player_name)
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        # 게임 상태 초기화 (게임 종료 후 상태 삭제)
        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': -0.02}
        self.paddle_positions = {'player1': 0, 'player2': 0}
        self.scores = {'player1': 0, 'player2': 0}

        # 플레이어의 게임 상태를 false로 설정
        self.game_active = False
        await self.set_user_game_status(self.user, False)


    @database_sync_to_async
    def set_user_game_status(self, user, is_in_game):
        try:
            with transaction.atomic():
                # 유저 상태를 select_for_update로 잠금
                user = CustomUser.objects.select_for_update().get(id=user.id)
                user.is_in_game = is_in_game
                user.save()
        except Exception as e:
            print(f"Error updating user game status: {e}")


    async def receive(self, text_data):
        if not self.game_active:
            return  # 게임이 종료된 경우 더 이상 입력을 처리하지 않음

        data = json.loads(text_data)
        if data['type'] == 'move':
            direction = data['direction']
            player = data['player']
            # print(data)

            # 패들 움직임 범위 제한 및 위치 업데이트
            if player == 'player1':
                self.paddle_positions['player1'] = max(-0.75, min(0.75, self.paddle_positions['player1'] + (-0.05 if direction == 'right' else 0.05)))
            elif player == 'player2':
                self.paddle_positions['player2'] = max(-0.75, min(0.75, self.paddle_positions['player2'] + (-0.05 if direction == 'right' else 0.05)))

            await self.send_game_state()

    async def start_game(self):

        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': -0.02}
        self.paddle_positions = {'player1': 0, 'player2': 0}
        self.scores = {'player1': 0, 'player2': 0}  # 점수 초기화
        self.game_active = True  # 게임 활성화 상태로 설정

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
            if self.ball_position['z'] <= -1.5:
                if abs(self.ball_position['x'] - self.paddle_positions['player1']) <= 0.25:
                    offset = self.ball_position['x'] - self.paddle_positions['player1']
                    self.ball_velocity['x'] += offset * 0.1
                    self.ball_velocity['z'] = -self.ball_velocity['z']
                else:
                    self.scores['player2'] += 1
                    if self.scores['player2'] >= 5:
                        await self.end_game(winner=self.players['player2'])
                    else:
                        await self.reset_ball()

            elif self.ball_position['z'] >= 1.5:
                if abs(self.ball_position['x'] - self.paddle_positions['player2']) <= 0.25:
                    offset = self.ball_position['x'] - self.paddle_positions['player2']
                    self.ball_velocity['x'] += offset * 0.1
                    self.ball_velocity['z'] = -self.ball_velocity['z']
                else:
                    self.scores['player1'] += 1
                    if self.scores['player1'] >= 5:
                        await self.end_game(winner=self.players['player1'])
                    else:
                        await self.reset_ball()

        except Exception as e:
            print(f"Error in update_ball_position: {e}")
            await self.close()

    async def reset_ball(self):
        if not self.game_active:
            return  # 게임이 종료된 경우 공 위치 초기화 중지

        z_velocity = random.choice([-0.02, 0.02])

        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': z_velocity}
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
        # player1과 player2의 닉네임, 점수, 그리고 게임 점수를 함께 보냅니다.
        self.game_active = False

        user1 = await database_sync_to_async(CustomUser.objects.get)(nickname=self.players['player1'])
        user2 = await database_sync_to_async(CustomUser.objects.get)(nickname=self.players['player2'])

        if winner == 'player1':
            player1_score = user1.score + 20
            player2_score = user2.score - 20
        else:
            player1_score = user1.score - 20
            player2_score = user2.score + 20

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'game_over',
                'winner': winner,
                'scores': self.scores,
                'player1': self.players['player1'],
                'player1_score': player1_score,
                'player2': self.players['player2'],
                'player2_score': player2_score,
            }
        )

        # 게임 상태 초기화
        self.ball_position = {'x': 0, 'y': 0, 'z': 0}
        self.ball_velocity = {'x': 0.01, 'y': 0, 'z': random.choice([-0.02, 0.02])}
        self.paddle_positions = {'player1': 0, 'player2': 0}
        self.scores = {'player1': 0, 'player2': 0}

        # 플레이어를 방에서 제거
        await self.remove_user_from_room(self.room_name, self.players['player1'])
        await self.remove_user_from_room(self.room_name, self.players['player2'])

        # 연결을 끊기 전에 일정 시간 대기 (예: 2초)
        await asyncio.sleep(2)

        await self.save_game_results(winner)

        # WebSocket 연결 종료
        await self.close()


    @database_sync_to_async
    def save_game_results(self, winner):
        try:
            with transaction.atomic():  # 트랜잭션 시작
                user1 = CustomUser.objects.select_for_update().get(nickname=self.players['player1'])
                user2 = CustomUser.objects.select_for_update().get(nickname=self.players['player2'])

                # 게임 결과 저장
                game1 = Game(
                    user1=user1,
                    user2=user2,
                    user1_score=self.scores['player1'],
                    user2_score=self.scores['player2']
                )
                game1.save()

                game2 = Game(
                    user1=user2,
                    user2=user1,
                    user1_score=self.scores['player2'],
                    user2_score=self.scores['player1']
                )
                game2.save()

                # 승리한 플레이어 및 점수 계산
                if winner == user1.nickname:
                    user1.win_cnt += 1
                    user1.score += 20
                    user2.score -= 20
                else:
                    user2.win_cnt += 1
                    user2.score += 20
                    user1.score -= 20

                # 매칭 수 업데이트
                user1.match_cnt += 1
                user2.match_cnt += 1

                # 사용자 데이터베이스 업데이트
                user1.save()
                user2.save()

                # ScoreHistory 생성 및 저장
                score_history1 = ScoreHistory(user=user1, score=user1.score)
                score_history1.save()

                score_history2 = ScoreHistory(user=user2, score=user2.score)
                score_history2.save()

        except CustomUser.DoesNotExist:
            print("User not found.")
        except Exception as e:
            print(f"Error saving game results: {e}")

    async def game_over(self, event):
        self.game_active = False
        winner = event['winner']
        scores = event['scores']
        player1 = event['player1']
        player1_score = event['player1_score']
        player2 = event['player2']
        player2_score = event['player2_score']

        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': winner,
            'scores': scores,
            'player1': player1,
            'player1_score': player1_score,
            'player2': player2,
            'player2_score': player2_score
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






from .game import PingPongGame
class OfflineConsumer(AsyncWebsocketConsumer):

    def count_player(self):
        self.user1 = self.scope['url_route']['kwargs'].get('user1', None)
        self.user2 = self.scope['url_route']['kwargs'].get('user2', None)
        self.user3 = self.scope['url_route']['kwargs'].get('user3', None)
        self.user4 = self.scope['url_route']['kwargs'].get('user4', None)
        if(self.user1): self.player_count += 1
        if(self.user2): self.player_count += 1
        if(self.user3): self.player_count += 1
        if(self.user4): self.player_count += 1
        print("player count = ", self.player_count)

    async def connect(self):
        self.user = self.scope['user']
        self.player_count = 0
        self.winner = ''
        self.wait = True
        self.count_player()
        print("local connect")
        print("user =", self.user)
        print("URL Route Kwargs:", self.scope['url_route']['kwargs'])
        self.keep_running = True
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'game_start'
        }))
        print(self.winner)
        asyncio.create_task(self.game_execute())


    async def game_execute(self):
        task1 = asyncio.create_task(self.game_loop(self.user1, self.user2))
        await task1
        if(self.player_count == 4):
            winner1 = self.winner
            print(self.winner)
            #대기1
            while(self.wait):
                await asyncio.sleep(0.3)
            self.wait = True
            task2 = asyncio.create_task(self.game_loop(self.user3, self.user4))
            await task2
            winner2 = self.winner
            print(self.winner)
            print("winner1 = ", winner1, "winner2 = ", winner2)
            #대기2
            while(self.wait):
                await asyncio.sleep(0.3)
            self.wait = True
            task3 = asyncio.create_task(self.game_loop(winner1, winner2))
            await task3


    async def disconnect(self, close_code):
        self.keep_running = False
        print("Gameconsumer WebSocket disconnected")
        # await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # print("Received data:", data)  # 서버에서 받은 데이터를 출력해 확인
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        data = json.loads(text_data)

        if 'key' in data:
            # 패들을 움직이는 플레이어와 방향을 가져옴

            key = data['key']  # 예: 'left' 또는 'right'

            # 이 정보를 바탕으로 게임 로직에서 패들 이동 처리
            self.game.move_paddle(key)

            # 게임 상태를 업데이트하고 클라이언트에 다시 보내는 예시
            self.game.move_ball()  # 공도 이동
            game_state = self.game.get_game_state()

            # 모든 클라이언트에게 게임 상태를 전송 (broadcast)
            await self.send(text_data=json.dumps(game_state))

        elif 'type' in data:
            if data['type'] == 'game_end_ack':
                self.wait = False

    async def game_loop(self,user1, user2):
        self.game = PingPongGame(100,50,10, user1, user2)
        print("game created")
        print("user1 =", user1, "user2 =", user2)
        while (self.keep_running):
            await asyncio.sleep(0.1)
            self.game.move_ball()
            state = self.game.get_game_state()

            await self.send(text_data=json.dumps({
                'type': 'game_loop',
                'state': state,
            }))
            if(self.game.player1_score == 5):
                self.winner = user1
                break
            elif (self.game.player2_score == 5):
                self.winner = user2
                break

        await self.send(text_data=json.dumps({
            'type': 'game_end',
            'winner': self.winner
        }))
        self.game.player1_score = 0
        self.game.player2_score = 0



