.PHONY: dev start worker lint format install security pre-commit-setup quality-check clean

# ── Development ──────────────────────────────────────────
dev:
	./venv/bin/python -m uvicorn app.main:app --reload --port 8000

# ── Production ───────────────────────────────────────────
start:
	./venv/bin/python -m gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# ── Celery Worker ────────────────────────────────────────
worker:
	./venv/bin/python -m celery -A app.tasks.celery_app worker --loglevel=info

# ── Code Quality ─────────────────────────────────────────
lint:
	./venv/bin/python -m ruff check . --fix

format:
	./venv/bin/python -m ruff format .

# ── Setup ────────────────────────────────────────────────
install:
	python3 -m venv venv
	./venv/bin/python -m pip install -r requirements.txt

# ── Security ───────────────────────────────────────────────
security:
	./venv/bin/python -m bandit -r app/ -f json -o security_report.json
	./venv/bin/python -m safety check --json --output safety_deps.json

# ── Pre-commit Setup ───────────────────────────────────────
pre-commit-setup:
	./venv/bin/python -m pre_commit install
	./venv/bin/python -m pre_commit run --all-files

# ── Quality Check ───────────────────────────────────────────
quality-check: lint format security

# ── Clean Cache ─────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache .mypy_cache .pytest_cache

