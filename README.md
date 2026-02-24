# 🛒 E-Commerce Backend — FastAPI

A production-ready e-commerce REST API built with **Python 3.11+** and **FastAPI**.

---

## 📁 Project Structure

```
app/
├── main.py                          # Entry point — FastAPI app instance
├── api/v1/router.py                 # Central route registry
├── modules/                         # Domain modules (self-contained features)
│   ├── auth/
│   │   ├── auth_route.py            # /api/v1/auth/* endpoints
│   │   ├── auth_controller.py       # Thin orchestration layer
│   │   ├── auth_service.py          # Business logic
│   │   ├── auth_dto.py              # Pydantic request/response DTOs
│   │   ├── auth_dco.py              # Domain Class Object (UserDCO)
│   │   └── auth_model.py            # Data access (user CRUD)
│   ├── product/
│   │   ├── product_route.py         # /api/v1/products/* endpoints
│   │   ├── product_controller.py    # Thin orchestration layer
│   │   ├── product_service.py       # Validation + pagination logic
│   │   ├── product_dto.py           # Pydantic request/response DTOs
│   │   ├── product_dco.py           # Domain Class Object (ProductDCO)
│   │   └── product_model.py         # Data access (product CRUD)
│   └── order/
│       ├── order_route.py           # /api/v1/orders/* endpoints
│       ├── order_controller.py      # Thin orchestration layer
│       ├── order_service.py         # Validation + calculation logic
│       ├── order_dto.py             # Pydantic request/response DTOs
│       ├── order_dco.py             # Domain Class Objects (Order/Item/Address)
│       ├── order_model.py           # Data access (order CRUD)
│       └── order_tasks.py           # Celery tasks (email + payment)
├── core/                            # Shared config, security, logging
│   ├── config.py                    # Reads .env via pydantic-settings
│   ├── security.py                  # JWT + bcrypt + auth dependencies
│   ├── logging.py                   # Loguru setup (console + file + JSON)
│   └── exceptions.py                # Custom exception classes
├── common/                          # Shared utilities + services
│   ├── response.py                  # respond() / error_respond() wrappers
│   ├── base_dco.py                  # Base DCO dataclass (id, created_at)
│   ├── schemas/errors.py            # Error response Pydantic models
│   └── services/http_client.py      # Reusable async HTTP client (httpx)
├── middleware/                      # Request context + error handling
│   ├── error_handler.py
│   └── request_context.py
└── tasks/                           # Celery configuration
    └── celery_app.py                # Celery broker/backend config
```

> **Barrel exports:** Each module uses `__init__.py` barrel re-exports. Import from the module directly:
> ```python
> from app.modules.auth import RegisterRequestDTO, UserDCO
> from app.modules.product import CreateProductRequestDTO, ProductDCO
> from app.core import settings, get_current_user
> from app.common import respond, error_respond
> ```

---

## 🐍 Step 1 — Install Python (3.11 or higher)

### macOS

```bash
# Option A: Homebrew (recommended)
brew install python@3.12

# Option B: Official installer
# Download from https://www.python.org/downloads/macos/

# Verify
python3 --version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version
```

### Windows

```powershell
# Option A: Winget (recommended)
winget install Python.Python.3.12

# Option B: Official installer
# Download from https://www.python.org/downloads/windows/
# ⚠️ CHECK "Add python.exe to PATH" during installation

# Verify (restart terminal first)
python --version
```

> **Windows note:** On Windows, use `python` instead of `python3` in all commands below. If `python` doesn't work after installing, restart your terminal or add Python to your system PATH manually.

---

## 📦 Step 2 — Clone & Setup Virtual Environment

```bash
# Clone the repo
git clone <your-repo-url>
cd ecom-backend
```

### macOS / Ubuntu

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> If you get a PowerShell execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

You'll see `(venv)` in your terminal prompt when the virtual environment is active.

> **Deactivate** the venv anytime with: `deactivate`

---

## 📥 Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, Uvicorn, Pydantic, JWT auth, bcrypt, Redis client, Celery, Stripe SDK, AWS SDK, and more.

---

## ⚙️ Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | JWT signing key (min 32 chars, change in production) | ✅ |
| `REDIS_URL` | Redis connection string | ❌ (optional — enables caching + Celery) |
| `STRIPE_SECRET_KEY` | Stripe API key | ❌ (only for payments) |
| `SENDGRID_API_KEY` | SendGrid email API key | ❌ (only for emails) |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 | ❌ (only for file uploads) |
| `ALLOWED_ORIGINS` | CORS origins as JSON array | ❌ (defaults to `localhost:3000`) |

---

## 🗄️ Step 5 — Start Redis (optional)

Redis enables **response caching** and **Celery background tasks** (emails, payments). The API works fully without it — caching and background tasks are simply skipped.

> [!NOTE]
> **Without Redis:** The API runs normally but product responses aren't cached, and order emails/payments won't process in the background. You can add Redis anytime later by setting `REDIS_URL` in `.env`.

### macOS

```bash
brew install redis
brew services start redis
```

### Ubuntu

```bash
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis   # auto-start on boot
```

### Windows

```powershell
# Easiest via Docker (install Docker Desktop first)
docker run -d -p 6379:6379 --name redis redis:alpine
```

### Any OS (via Docker)

```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### Verify Redis is running

```bash
redis-cli ping
# Should return: PONG
```

---

## � Step 5 — Setup Security & Code Quality

```bash
# Install pre-commit hooks (runs automatically before each commit)
make pre-commit-setup

# Run security scans
make security

# Run full quality check (lint + format + security)
make quality-check
```

**What this does:**
- **Pre-commit hooks:** Automatically run linting, formatting, and security checks before each commit
- **Bandit:** Scans your code for security vulnerabilities (SQL injection, hardcoded secrets, etc.)
- **Safety:** Checks your dependencies for known CVEs
- **Ruff:** Lints and formats your Python code
- **MyPy:** Performs static type checking

---

## �🚀 Step 6 — Run the Project (Development)

> [!IMPORTANT]
> **You must activate the virtual environment first** in every new terminal session, otherwise commands like `uvicorn` and `celery` won't be found.
>
> ```bash
> # macOS / Ubuntu
> source venv/bin/activate
>
> # Windows (PowerShell)
> .\venv\Scripts\Activate.ps1
>
> # Windows (CMD)
> venv\Scripts\activate.bat
> ```
> You'll see `(venv)` in your terminal prompt when it's active.

```bash
uvicorn app.main:app --reload --port 8000
```

| Flag | What it does |
|---|---|
| `app.main:app` | Import path → `app` object from `app/main.py` |
| `--reload` | Auto-restart on code changes (like nodemon) |
| `--port 8000` | Listen on port 8000 |

### ✅ Verify it's running

- Health check: http://localhost:8000/health → `{"status": "ok"}`
- Swagger docs: http://localhost:8000/docs
- ReDoc docs: http://localhost:8000/redoc

---

## 🏭 Step 7 — Run in Production (Build / Deploy)

FastAPI doesn't have a separate "build" step like frontend apps. The Python source runs directly. For production, use **Gunicorn** with Uvicorn workers:

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

| Flag | What it does |
|---|---|
| `--workers 4` | Number of worker processes (rule of thumb: `2 × CPU cores + 1`) |
| `--worker-class uvicorn.workers.UvicornWorker` | Use async Uvicorn workers |
| `--bind 0.0.0.0:8000` | Listen on all interfaces, port 8000 |
| `--timeout 120` | Kill workers that are silent for 120 seconds |

> **Windows note:** Gunicorn does not run on Windows. Use `uvicorn app.main:app --host 0.0.0.0 --port 8000` directly, or deploy via Docker/WSL.

---

## ⏳ Step 8 — Run Celery Worker (Background Tasks)

Celery handles background jobs like sending emails and processing payments. Run in a **separate terminal**:

```bash
# Activate venv first
source venv/bin/activate       # macOS/Ubuntu
# .\venv\Scripts\Activate.ps1  # Windows

celery -A app.tasks.celery_app worker --loglevel=info
```

> **Windows note:** Celery 5.x has limited Windows support. Use `--pool=solo` flag:
> ```powershell
> celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
> ```

---

## 🔍 Code Quality

```bash
ruff check .         # Lint (find issues)
ruff check . --fix   # Lint + auto-fix
ruff format .        # Format code (like Prettier)
mypy app/            # Static type checking
```

---

## 📖 API Endpoints

### Auth — `/api/v1/auth`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/register` | ❌ | Register new user |
| `POST` | `/login` | ❌ | Login, get JWT tokens |
| `POST` | `/refresh` | ❌ | Refresh access token |
| `GET` | `/me` | ✅ Bearer | Get current user profile |

### Products — `/api/v1/products`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | ❌ | List products (paginated, filterable) |
| `GET` | `/:id` | ❌ | Get single product |
| `POST` | `/` | ✅ Admin | Create product |
| `PATCH` | `/:id` | ✅ Admin | Update product |
| `DELETE` | `/:id` | ✅ Admin | Delete product |

### Orders — `/api/v1/orders`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/` | ✅ Bearer | Place new order |
| `GET` | `/my-orders` | ✅ Bearer | Get my orders |
| `GET` | `/:id` | ✅ Bearer | Get order (own or admin) |
| `PATCH` | `/:id/status` | ✅ Admin | Update order status |

### Health — `/health`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | ❌ | Health check |

> **Full interactive docs** with try-it-out buttons available at `/docs` when the server is running.

---

## 🔧 Common Issues & Fixes

### `ModuleNotFoundError: No module named 'app'`
You're running the command from the wrong directory. Make sure you're in the project root (`ecom-backend/`) and your venv is activated.

### `python3: command not found` (Ubuntu)
```bash
sudo apt install python3
```

### `pip: command not found`
```bash
# Use pip3 instead, or:
python3 -m pip install -r requirements.txt
```

### PowerShell: `cannot be loaded because running scripts is disabled`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Redis connection refused
Redis isn't running. Start it with `brew services start redis` (macOS), `sudo systemctl start redis` (Ubuntu), or `docker run -d -p 6379:6379 redis:alpine`.

### `bcrypt` or `cryptography` build errors
You may need system build tools:
```bash
# Ubuntu
sudo apt install -y build-essential libffi-dev

# macOS
xcode-select --install
```

---

## 🧱 Adding a New Feature

Follow this pattern when adding a new module (e.g., Reviews):

1. **Create module folder** → `app/modules/review/`
2. **DCO** → Create `review_dco.py` with a `@dataclass` domain object (extends `BaseDCO`)
3. **DTO** → Create `review_dto.py` with Pydantic request/response DTOs
4. **Model** → Create `review_model.py` — accepts/returns DCOs
5. **Service** → Create `review_service.py` with pure business logic (validation, calculations)
6. **Controller** → Create `review_controller.py` — bridges DTO↔DCO, calls service + model
7. **Route** → Create `review_route.py` — thin handlers that use `respond()` wrapper
8. **Init** → Create `__init__.py` with barrel exports
9. **Register** → Add to `app/api/v1/router.py`:
   ```python
   from app.modules.review.review_route import router as review_router
   router.include_router(review_router, prefix="/reviews", tags=["Reviews"])
   ```

---

## 📋 Quick Reference

```bash
# ── Makefile shortcuts (no venv activation needed) ───
make dev              # start dev server with hot reload
make start            # start production server
make worker           # start Celery background worker
make lint             # lint + auto-fix
make format           # format code
make install          # create venv + install all deps
make security         # run security scans (bandit + safety)
make pre-commit-setup # install git hooks
make quality-check   # lint + format + security
make clean           # clean cache files

# ── Manual commands (need venv activated first) ──────
source venv/bin/activate                          # activate venv
uvicorn app.main:app --reload --port 8000         # start dev server
celery -A app.tasks.celery_app worker -l info     # start celery worker

# ── Security Scanning ───────────────────────────────
bandit -r app/                                    # scan code for vulnerabilities
safety check                                       # scan dependencies for CVEs
pre-commit run --all-files                        # run all git hooks

# ── Dependency Management ────────────────────────────
pip install <package>                             # install new package
pip freeze > requirements.txt                     # save to lockfile
```
# eastcoast-lubcriant-be
