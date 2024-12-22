class PingPongGame:
    def __init__(self, table_width, table_length, paddle_width, userA, userB):
        self.table_width = table_width  # 탁구대의 너비 (x축 방향)
        self.table_length = table_length  # 탁구대의 길이 (z축 방향)
        self.paddle_width = paddle_width  # 패들의 너비
        self.player1 = userA
        self.player2 = userB
        # 패들의 x축 위치를 탁구대의 양 끝으로 고정
        self.player1_paddle_x = -self.table_width // 2 + self.paddle_width  # player1의 x축 위치 (탁구대의 왼쪽 끝 부분)
        self.player2_paddle_x = self.table_width // 2 - self.paddle_width  # player2의 x축 위치 (탁구대의 오른쪽 끝 부분)

        # 공의 초기 위치와 방향
        self.ball_pos = [0, 0]
        self.ball_dir = [1, 1]  # x축과 z축으로 공이 이동하는 방향

        # 패들의 초기 위치 (z축만 사용)
        self.player1_paddle_z = 0  # player1 패들의 초기 z 위치
        self.player2_paddle_z = 0  # player2 패들의 초기 z 위치

        # 점수 초기화
        self.player1_score = 0
        self.player2_score = 0

    def move_paddle(self, key):
        """
        패들은 키보드 입력에 따라 상대적으로 이동합니다.
        :param key: 'w', 's', 'o', 'l' 중 하나로, 각 키에 따라 패들의 이동 방향을 지정합니다.
        """
        if key == 'KeyW':
            # player1의 패들을 위로 이동 (z축 양의 방향)
            if self.player1_paddle_z > -self.table_length // 2 + self.paddle_width // 2:
                self.player1_paddle_z -= 1
        elif key == 'KeyS':
            # player1의 패들을 아래로 이동 (z축 음의 방향)
            if self.player1_paddle_z < self.table_length // 2 - self.paddle_width // 2:
                self.player1_paddle_z += 1
        elif key == 'KeyO':
            # player2의 패들을 위로 이동 (z축 양의 방향)
            if self.player2_paddle_z > -self.table_length // 2 + self.paddle_width // 2:
                self.player2_paddle_z -= 1
        elif key == 'KeyL':
            # player2의 패들을 아래로 이동 (z축 음의 방향)
            if self.player2_paddle_z < self.table_length // 2 - self.paddle_width // 2:
                self.player2_paddle_z += 1

    def move_ball(self):
        # 공은 x축과 z축으로만 이동
        self.ball_pos[0] += self.ball_dir[0]  # x축으로 공 이동
        self.ball_pos[1] += self.ball_dir[1]  # z축으로 공 이동

        # z축 경계에 부딪히면 방향 반전
        if self.ball_pos[1] <= -self.table_length // 2 or self.ball_pos[1] >= self.table_length // 2:
            self.ball_dir[1] *= -1

        # player1 패들 충돌 검사 (x축 왼쪽 끝 부분)
        if self.ball_pos[0] <= self.player1_paddle_x:
            if self.ball_pos[1] >= self.player1_paddle_z - self.paddle_width // 2 and self.ball_pos[1] <= self.player1_paddle_z + self.paddle_width // 2:
                # 패들에 맞았으면 반사
                self.ball_dir[0] *= -1
            else:
                # 패들에 맞지 않으면 player2가 득점
                self.player2_score += 1
                self.reset_ball()

        # player2 패들 충돌 검사 (x축 오른쪽 끝 부분)
        if self.ball_pos[0] >= self.player2_paddle_x:
            if self.ball_pos[1] >= self.player2_paddle_z - self.paddle_width // 2 and self.ball_pos[1] <= self.player2_paddle_z + self.paddle_width // 2:
                # 패들에 맞았으면 반사
                self.ball_dir[0] *= -1
            else:
                # 패들에 맞지 않으면 player1이 득점
                self.player1_score += 1
                self.reset_ball()

    def reset_ball(self):
        # 공을 중앙으로 리셋
        self.ball_pos = [0, 0]
        self.ball_dir = [1, 1]  # 기본 방향으로 리셋

    def get_game_state(self):
        # 게임 상태 반환 (패들 위치, 공 위치, 점수)
        return {
            'ball_pos': self.ball_pos,
            'player1' : self.player1,
            'player2' : self.player2,
            'player1_paddle_z': self.player1_paddle_z,
            'player2_paddle_z': self.player2_paddle_z,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score
        }

