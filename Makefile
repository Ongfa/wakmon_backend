.PHONY: help install install-dev test test-cov run format lint type-check clean migrate-create migrate-up migrate-down docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make run           - Run the application locally"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Lint code with ruff"
	@echo "  make type-check    - Type check with mypy"
	@echo "  make clean         - Clean temporary files"
	@echo "  make migrate-create MSG='message' - Create new migration"
	@echo "  make migrate-up    - Apply migrations"
	@echo "  make migrate-down  - Rollback last migration"
	@echo "  make docker-up     - Start docker containers"
	@echo "  make docker-down   - Stop docker containers"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

format:
	black app/ tests/

lint:
	ruff check app/ tests/

type-check:
	mypy app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	rm -f *.db test.db

migrate-create:
	alembic revision --autogenerate -m "$(MSG)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
