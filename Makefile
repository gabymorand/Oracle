.PHONY: help build up down logs test init-db clean

help:
	@echo "Oracle - LoL Coaching Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs"
	@echo "  make init-db    - Initialize database with migrations"
	@echo "  make test       - Run backend tests"
	@echo "  make clean      - Clean containers and volumes"

build:
	docker compose build

up:
	docker compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker compose down

logs:
	docker compose logs -f

init-db:
	docker compose exec backend alembic revision --autogenerate -m "Initial migration"
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest

clean:
	docker compose down -v
	docker system prune -f
