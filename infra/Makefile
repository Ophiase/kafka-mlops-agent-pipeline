clean:
	docker compose down --remove-orphans
	docker system prune -f

build:
	docker compose build

run:
	docker compose up -d

run-build:
	docker compose up --build -d

rb: run-build
