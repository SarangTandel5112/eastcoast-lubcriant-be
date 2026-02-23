.PHONY: dev start worker lint format install security pre-commit-setup quality-check clean

# ── Development ──────────────────────────────────────────
dev:
	./venv/bin/uvicorn app.main:app --reload --port 8000

# ── Production ───────────────────────────────────────────
start:
	./venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# ── Celery Worker ────────────────────────────────────────
worker:
	./venv/bin/celery -A app.tasks.celery_app worker --loglevel=info

# ── Code Quality ─────────────────────────────────────────
lint:
	./venv/bin/ruff check . --fix

format:
	./venv/bin/ruff format .

# ── Setup ────────────────────────────────────────────────
install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

# ── Security ───────────────────────────────────────────────
security:
	./venv/bin/bandit -r app/ -f json -o security_report.json
	./venv/bin/safety check --json --output safety_deps.json

# ── Pre-commit Setup ───────────────────────────────────────
pre-commit-setup:
	./venv/bin/pre-commit install
	./venv/bin/pre-commit run --all-files

# ── Quality Check ───────────────────────────────────────────
quality-check: lint format security

# ── Clean Cache ─────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache .mypy_cache .pytest_cache
