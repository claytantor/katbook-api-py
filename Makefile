.PHONY: install dev test lint migrate seed docker-up docker-down

install:
	uv sync

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest --cov=app tests/

lint:
	ruff check . && mypy app/

migrate:
	uv run alembic upgrade head

migrate-docker:
	docker compose exec api uv run alembic upgrade head

seed:
	python scripts/seed.py

docker-up:
	docker compose up -d

docker-down:
	docker compose down
