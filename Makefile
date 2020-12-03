docker-run:
	docker-compose -f docker-compose.yml up -d

docker-run-dev:
	docker-compose -f docker-compose-dev.yml up

docker-run-dev-dettach:
	docker-compose -f docker-compose-dev.yml up -d

docker-stop-dev:
	docker-compose -f docker-compose-dev.yml down

docker-stop-all:
	docker-compose -f docker-compose.yml down -v

docker-stop:
	docker-compose -f docker-compose.yml down

