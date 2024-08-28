class PingPongGame:
    def __init__(self, table_width, table_length, paddle_width):
        self.table_width = table_width  # 탁구대의 너비 (x축 방향)
        self.table_length = table_length  # 탁구대의 길이 (y축 방향)
        self.paddle_width = paddle_width  # 패들의 너비
        
        # 패들의 y축 위치를 탁구대의 양 끝으로 고정
        self.player1_paddle_y = 0  # player1의 y축 위치 (탁구대의 시작 부분)
        self.player2_paddle_y = table_length  # player2의 y축 위치 (탁구대의 끝 부분)
        
        # 공의 초기 위치와 방향
        self.ball_pos = [table_width // 2, table_length // 2]  # 공의 x, y 좌표 (z축은 고정)
        self.ball_dir = [1, 1]  # x축과 y축으로 공이 이동하는 방향 (공은 z축에서 튕김)
        
        # 패들의 초기 위치 (x축만 사용)
        self.player1_paddle_x = table_width // 2  # player1 패들의 초기 x 위치
        self.player2_paddle_x = table_width // 2  # player2 패들의 초기 x 위치
        
        # 점수 초기화
        self.player1_score = 0
        self.player2_score = 0

    def move_paddle(self, player, direction):
        print("in move_paddle")
        """
        패들은 키보드 입력에 따라 상대적으로 이동합니다.
        :param player: 'player1' 또는 'player2' 패들을 지정합니다.
        :param direction: 'left' 또는 'right'로 패들의 이동 방향을 지정합니다.
        """
        if player == 'player1':
            if direction == 'left' and self.player1_paddle_x > 0:
                self.player1_paddle_x -= 1
            elif direction == 'right' and self.player1_paddle_x < self.table_width - self.paddle_width:
                self.player1_paddle_x += 1
        elif player == 'player2':
            if direction == 'left' and self.player2_paddle_x > 0:
                self.player2_paddle_x -= 1
            elif direction == 'right' and self.player2_paddle_x < self.table_width - self.paddle_width:
                self.player2_paddle_x += 1

    def move_ball(self):
        # 공은 x축과 y축으로만 이동, z축에서 항상 중간 지점에서 튕김
        self.ball_pos[0] += self.ball_dir[0]
        self.ball_pos[1] += self.ball_dir[1]
        
        # x축 경계에 부딪히면 방향 반전 (너비 방향)
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= self.table_width - 1:
            self.ball_dir[0] *= -1
        
        # player1 패들 충돌 검사 (y축 시작 부분)
        if self.ball_pos[1] <= self.player1_paddle_y:
            if self.ball_pos[0] >= self.player1_paddle_x and self.ball_pos[0] <= self.player1_paddle_x + self.paddle_width:
                # 패들에 맞았으면 반사
                self.ball_dir[1] *= -1
            else:
                # 패들에 맞지 않으면 player2가 득점
                self.player2_score += 1
                # self.reset_ball()
                self.ball_dir[1] *= -1
                

        # player2 패들 충돌 검사 (y축 끝 부분)
        if self.ball_pos[1] >= self.player2_paddle_y:
            if self.ball_pos[0] >= self.player2_paddle_x and self.ball_pos[0] <= self.player2_paddle_x + self.paddle_width:
                # 패들에 맞았으면 반사
                self.ball_dir[1] *= -1
            else:
                # 패들에 맞지 않으면 player1이 득점
                self.player1_score += 1
                # self.reset_ball()
                self.ball_dir[1] *= -1

    def reset_ball(self):
        # 공을 중앙으로 리셋
        self.ball_pos = [self.table_width // 2, self.table_length // 2]
        self.ball_dir = [1, 1]  # 기본 방향으로 리셋

    def get_game_state(self):
        # 게임 상태 반환 (패들 위치, 공 위치, 점수)
        return {
            'ball_pos': self.ball_pos,
            'player1_paddle_x': self.player1_paddle_x,
            'player2_paddle_x': self.player2_paddle_x,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score
        }

# 사용 예시
# game = PingPongGame(table_width=50, table_length=100, paddle_width=10)

# # 키보드 입력에 따라 패들 이동
# game.move_paddle('player1', 'left')  # player1 패들을 왼쪽으로 이동
# game.move_paddle('player2', 'right')  # player2 패들을 오른쪽으로 이동

# # 공을 이동시키고 게임 상태를 확인
# game.move_ball()
# state = game.get_game_state()

# print(state)  # {'ball_pos': [26, 51], 'player1_paddle_x': 19, 'player2_paddle_x': 41, 'player1_score': 0, 'player2_score': 0}
