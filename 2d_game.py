import os
import time

# 게임 설정
width = 40
height = 20
paddle_height = 4
ball_pos = [width // 2, height // 2]
ball_dir = [1, 1]
left_paddle_pos = height // 2 - paddle_height // 2
right_paddle_pos = height // 2 - paddle_height // 2
left_score = 0
right_score = 0

def print_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  # 화면을 지우기 위한 명령어
    for y in range(height):
        if y == 0 or y == height - 1:
            print("#" * width)  # 위아래 벽
        else:
            line = ""
            for x in range(width):
                if x == 0 or x == width - 1:
                    line += "#"  # 좌우 벽
                elif [x, y] == ball_pos:
                    line += "O"  # 공
                elif x == 2 and left_paddle_pos <= y < left_paddle_pos + paddle_height:
                    line += "|"  # 왼쪽 패들
                elif x == width - 3 and right_paddle_pos <= y < right_paddle_pos + paddle_height:
                    line += "|"  # 오른쪽 패들
                else:
                    line += " "  # 빈 공간
            print(line)
    print(f"Left Player: {left_score}   Right Player: {right_score}")

def move_paddle(paddle, direction):
    if paddle == 'left':
        global left_paddle_pos
        if direction == 'up' and left_paddle_pos > 1:
            left_paddle_pos -= 1
        elif direction == 'down' and left_paddle_pos < height - paddle_height - 1:
            left_paddle_pos += 1
    elif paddle == 'right':
        global right_paddle_pos
        if direction == 'up' and right_paddle_pos > 1:
            right_paddle_pos -= 1
        elif direction == 'down' and right_paddle_pos < height - paddle_height - 1:
            right_paddle_pos += 1

def move_ball():
    global ball_pos, ball_dir, left_score, right_score
    # 공 이동
    ball_pos[0] += ball_dir[0]
    ball_pos[1] += ball_dir[1]
    
    # 위아래 벽에 부딪히면 방향 반전
    if ball_pos[1] == 1 or ball_pos[1] == height - 2:
        ball_dir[1] *= -1
    
    # 왼쪽 패들에 부딪히면 방향 반전
    if ball_pos[0] == 3 and left_paddle_pos <= ball_pos[1] < left_paddle_pos + paddle_height:
        ball_dir[0] *= -1
    
    # 오른쪽 패들에 부딪히면 방향 반전
    if ball_pos[0] == width - 4 and right_paddle_pos <= ball_pos[1] < right_paddle_pos + paddle_height:
        ball_dir[0] *= -1
    
    # 공이 왼쪽으로 나가면 오른쪽 플레이어 점수 증가
    if ball_pos[0] == 1:
        right_score += 1
        reset_ball()
    
    # 공이 오른쪽으로 나가면 왼쪽 플레이어 점수 증가
    if ball_pos[0] == width - 2:
        left_score += 1
        reset_ball()

def reset_ball():
    global ball_pos, ball_dir
    ball_pos = [width // 2, height // 2]
    ball_dir = [1, 1]

# 게임 루프
while True:
    print_screen()
    move_ball()
    
    # 간단한 입력 처리 (왼쪽 패들: W, S / 오른쪽 패들: I, K)
    command = input("Move (W/S for left, I/K for right, Q to quit): ").lower()
    if command == 'w':
        move_paddle('left', 'up')
    elif command == 's':
        move_paddle('left', 'down')
    elif command == 'i':
        move_paddle('right', 'up')
    elif command == 'k':
        move_paddle('right', 'down')
    elif command == 'q':
        break
    
    # 짧은 시간 대기
    time.sleep(0.1)
