all: up

up:
	docker-compose -f docker-compose.yml -p transcendence up --build -d

down:
	docker-compose -f docker-compose.yml -p transcendence down

re: down up
