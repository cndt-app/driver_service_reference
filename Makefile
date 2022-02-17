build: 
	docker-compose build

up:
	docker-compose up -d


down:
	docker-compose down

restart: down up

ps:
	docker-compose ps

logs:
	docker-compose logs --tail 1000 -f
