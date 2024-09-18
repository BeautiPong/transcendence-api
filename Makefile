# 변수 정의
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_FILE = docker-compose.yml

.PHONY: build up down logs

# 기본 목표
all: up

# Docker 이미지를 빌드
build:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build

# Docker Compose로 컨테이너 실행
up: build
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

# Docker Compose로 컨테이너 중지
down:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

# Docker Compose 로그 출력
logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

# 컨테이너 상태 확인
status:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

re: down up
