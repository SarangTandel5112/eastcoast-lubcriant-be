# 🚀 Roadmap: From 8.5 to 9.5 Production Readiness

This document outlines the exact steps needed to take this FastAPI backend from **8.5/10 to 9.5/10** production readiness.

**Current Score:** 8.5/10
**Target Score:** 9.5/10
**Estimated Effort:** 3-4 weeks (1 developer)

---

## 📊 Gap Analysis: What's Missing?

| Component | Current State | Target State | Impact |
|-----------|--------------|--------------|--------|
| **Database** | In-memory dicts | PostgreSQL + async SQLAlchemy | 🔴 Critical |
| **Migrations** | None | Alembic with version control | 🔴 Critical |
| **Testing** | 0% coverage | 80%+ coverage (unit + integration) | 🔴 Critical |
| **Repository Pattern** | Direct model calls | Proper abstraction layer | 🟡 High |
| **Performance** | Basic async | Optimized queries, caching | 🟡 High |
| **Monitoring** | Basic logging | Metrics, tracing, alerts | 🟡 High |
| **CI/CD** | None | Automated testing + deployment | 🟡 High |
| **Docker** | None | Multi-stage production images | 🟢 Medium |
| **Load Testing** | None | Validated for 10k+ concurrent users | 🟢 Medium |

---

## 🎯 Phase 1: Database Foundation (Week 1)

**Goal:** Replace in-memory storage with production-grade PostgreSQL database.

### Step 1.1: Install Database Dependencies

```bash
# Add to requirements.txt
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9  # For migrations
```

```bash
pip install -r requirements.txt
```

### Step 1.2: Set Up PostgreSQL

**Option A: Local Docker**
```bash
docker run --name eastcoast-postgres \
  -e POSTGRES_USER=eastcoast \
  -e POSTGRES_PASSWORD=dev_password \
  -e POSTGRES_DB=eastcoast_db \
  -p 5432:5432 \
  -d postgres:15-alpine
```

**Option B: Managed Service** (Recommended for production)
- AWS RDS
- Google Cloud SQL
- DigitalOcean Managed Databases
- Supabase

### Step 1.3: Create Database Configuration

**File:** `app/core/database.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings

# Base class for all ORM models
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

# Create async engine
engine = create_async_engine(
    settings.database_url,  # postgresql+asyncpg://user:pass@host:port/db
    echo=settings.debug,  # SQL query logging in debug mode
    pool_size=20,  # Connection pool size
    max_overflow=40,  # Extra connections on high load
    pool_timeout=30,  # Wait 30s for connection
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Dependency for routes
async def get_db() -> AsyncSession:
    """
    Dependency that provides a database session.
    Automatically commits on success, rolls back on error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Mixin for common fields
class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class SoftDeleteMixin:
    """Mixin to add soft delete functionality."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
```

### Step 1.4: Update Configuration

**File:** `app/core/config.py` (add database settings)
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Database
    database_url: str = Field(
        ...,  # Required
        description="PostgreSQL connection URL: postgresql+asyncpg://user:pass@host:port/db"
    )

    # Test database (for running tests)
    test_database_url: str = Field(
        default="",
        description="Test database URL (optional)"
    )

    @validator("database_url")
    def validate_database_url(cls, v):
        """Ensure database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver. "
                "Format: postgresql+asyncpg://user:pass@host:port/db"
            )
        return v
```

### Step 1.5: Create ORM Models

**File:** `app/modules/auth/models.py`
```python
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import enum

from app.core.database import Base, TimestampMixin, SoftDeleteMixin

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.CUSTOMER)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"
```

**File:** `app/modules/product/models.py`
```python
from sqlalchemy import String, Float, Integer, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base, TimestampMixin, SoftDeleteMixin

class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    images: Mapped[list] = mapped_column(ARRAY(String), default=list)
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optimistic locking for stock management
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Product {self.name}>"
```

**File:** `app/modules/order/models.py`
```python
from sqlalchemy import String, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import enum

from app.core.database import Base, TimestampMixin

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, index=True)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_intent_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # Shipping address (embedded)
    shipping_name: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    shipping_address_line2: Mapped[str] = mapped_column(String(255), nullable=True)
    shipping_city: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_state: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    shipping_country: Mapped[str] = mapped_column(String(2), nullable=False, default="US")

    # Relationships
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User", back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    order_id: Mapped[str] = mapped_column(String(50), ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(50), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
```

### Step 1.6: Initialize Alembic

```bash
# Initialize Alembic
alembic init alembic

# This creates:
# - alembic/
# - alembic.ini
```

**Edit:** `alembic.ini`
```ini
# Line 63: Update sqlalchemy.url
sqlalchemy.url = postgresql+asyncpg://eastcoast:dev_password@localhost:5432/eastcoast_db
# Or use: sqlalchemy.url = %(DATABASE_URL)s  # Read from env
```

**Edit:** `alembic/env.py`
```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models here
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.product.models import Product
from app.modules.order.models import Order, OrderItem

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 1.7: Create Initial Migration

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Review the generated migration in alembic/versions/
# Then apply it:
alembic upgrade head
```

### Step 1.8: Update `.env`

```bash
# Add to .env
DATABASE_URL=postgresql+asyncpg://eastcoast:dev_password@localhost:5432/eastcoast_db
TEST_DATABASE_URL=postgresql+asyncpg://eastcoast:dev_password@localhost:5432/eastcoast_test_db
```

### Step 1.9: Create Repository Layer

**File:** `app/modules/auth/repository.py`
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.modules.auth.models import User

class UserRepository:
    """Repository for User data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        email: str,
        password: str,
        role: str = "customer"
    ) -> User:
        """Create a new user."""
        user = User(
            id=f"user_{uuid.uuid4().hex[:12]}",
            name=name,
            email=email,
            password=password,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()  # Get ID without committing
        return user

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        stmt = select(User).where(
            User.email == email,
            User.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        stmt = select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = await self.find_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            setattr(user, key, value)

        await self.session.flush()
        return user
```

### Step 1.10: Update Service Layer

**File:** `app/modules/auth/auth_service.py` (updated)
```python
async def register_user(
    body: RegisterRequestDTO,
    db: AsyncSession  # Add database dependency
) -> UserResponseDTO:
    """Register a new user."""
    repo = UserRepository(db)

    # Check if email exists
    existing = await repo.find_by_email(body.email)
    if existing:
        raise ConflictError("Email already registered", resource="user", field="email")

    # Hash password
    hashed = hash_password(body.password)

    # Create user
    user = await repo.create(
        name=body.name,
        email=body.email,
        password=hashed
    )

    logger.info("User registered | user_id={}", user.id)

    # Convert ORM model to DTO
    return UserResponseDTO(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.value
    )
```

### Step 1.11: Update Routes with Database Dependency

**File:** `app/modules/auth/auth_route.py` (updated)
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register(
    request: Request,
    body: RegisterRequestDTO,
    db: AsyncSession = Depends(get_db)  # Add database dependency
):
    """Register a new user account."""
    user = await auth_service.register_user(body, db)
    return respond(data=user, message="User registered successfully", status_code=201)
```

### Step 1.12: Update Application Startup

**File:** `app/main.py` (add to lifespan)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    setup_logging()
    logger.info("Starting {} ...", settings.app_name)

    # Test database connection
    try:
        from app.core.database import engine
        async with engine.begin() as conn:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error("Database connection failed | error={}", str(e))
        raise

    # ... rest of startup

    yield

    # ── Shutdown ─────────────────────────────────────────
    # Dispose database engine
    from app.core.database import engine
    await engine.dispose()
    logger.info("Shutting down...")
```

---

## 🧪 Phase 2: Testing Infrastructure (Week 2)

**Goal:** Achieve 80%+ test coverage with unit and integration tests.

### Step 2.1: Set Up Testing Dependencies

```bash
# Add to requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.27.2  # For testing FastAPI
faker==22.0.0  # For generating test data
factory-boy==3.3.0  # For test fixtures
```

### Step 2.2: Configure Pytest

**File:** `pytest.ini`
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing:skip-covered
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Step 2.3: Create Test Database Setup

**File:** `tests/conftest.py`
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = settings.test_database_url or "postgresql+asyncpg://eastcoast:dev_password@localhost:5432/eastcoast_test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    """Create test database session."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Step 2.4: Write Unit Tests

**File:** `tests/unit/test_auth_service.py`
```python
import pytest
from unittest.mock import AsyncMock

from app.modules.auth.auth_service import register_user
from app.modules.auth.auth_dto import RegisterRequestDTO
from app.modules.auth.repository import UserRepository
from app.modules.auth.models import User
from app.core.exceptions import ConflictError

@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_success():
    """Test successful user registration."""
    # Arrange
    mock_db = AsyncMock()
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.find_by_email.return_value = None  # Email not taken
    mock_repo.create.return_value = User(
        id="user_123",
        name="Test User",
        email="test@example.com",
        password="hashed_password",
        role="customer"
    )

    dto = RegisterRequestDTO(
        name="Test User",
        email="test@example.com",
        password="SecurePass123!@#"
    )

    # Act
    result = await register_user(dto, mock_db)

    # Assert
    assert result.email == "test@example.com"
    assert result.name == "Test User"
    mock_repo.create.assert_called_once()

@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_user_duplicate_email():
    """Test registration with existing email."""
    # Arrange
    mock_db = AsyncMock()
    mock_repo = AsyncMock(spec=UserRepository)
    mock_repo.find_by_email.return_value = User(id="existing", email="test@example.com")

    dto = RegisterRequestDTO(
        name="Test User",
        email="test@example.com",
        password="SecurePass123!@#"
    )

    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        await register_user(dto, mock_db)

    assert "Email already registered" in str(exc_info.value.message)
```

### Step 2.5: Write Integration Tests

**File:** `tests/integration/test_auth_api.py`
```python
import pytest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_endpoint(client):
    """Test /auth/register endpoint."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123!@#"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == "john@example.com"
    assert "password" not in data["data"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_endpoint(client):
    """Test /auth/login endpoint."""
    # First register
    await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "SecurePass123!@#"
        }
    )

    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "jane@example.com",
            "password": "SecurePass123!@#"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
```

### Step 2.6: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit  # Only unit tests
pytest -m integration  # Only integration tests

# Open coverage report
open htmlcov/index.html
```

---

## 🚀 Phase 3: Performance & Monitoring (Week 3)

### Step 3.1: Add Prometheus Metrics

```bash
# Add to requirements.txt
prometheus-fastapi-instrumentator==6.1.0
```

**File:** `app/core/metrics.py`
```python
from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app):
    """Setup Prometheus metrics."""
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    instrumentator.instrument(app).expose(app, endpoint="/metrics")
```

### Step 3.2: Add Distributed Tracing

```bash
# Add to requirements.txt
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
```

### Step 3.3: Add Performance Monitoring Middleware

**File:** `app/middleware/performance.py`
```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests
        if duration_ms > 1000:  # > 1 second
            logger.warning(
                "Slow request | path={} method={} duration_ms={:.2f}",
                request.url.path,
                request.method,
                duration_ms
            )

        # Add header
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

        return response
```

### Step 3.4: Add Database Query Optimization

**Implement connection pooling monitoring:**
```python
from sqlalchemy import event
from loguru import logger

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries."""
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time."""
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 0.5:  # Log queries > 500ms
        logger.warning(f"Slow query ({total:.2f}s): {statement}")
```

---

## 🐳 Phase 4: Containerization & CI/CD (Week 4)

### Step 4.1: Create Production Dockerfile

**File:** `docker/Dockerfile`
```dockerfile
# Multi-stage build for production

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
```

### Step 4.2: Create Docker Compose

**File:** `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: eastcoast
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: eastcoast_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eastcoast"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://eastcoast:dev_password@postgres:5432/eastcoast_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:
  redis_data:
```

### Step 4.3: Create GitHub Actions CI/CD

**File:** `.github/workflows/ci.yml`
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          ruff check app/
          mypy app/

      - name: Run security checks
        run: |
          bandit -r app/
          safety check

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key-min-32-characters-long-for-testing
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t eastcoast-api:${{ github.sha }} -f docker/Dockerfile .

      - name: Push to registry
        # Add your registry push logic here
        run: echo "Push to Docker registry"
```

---

## 📊 Phase 4: Load Testing

### Step 4.1: Install Locust

```bash
# Add to requirements-dev.txt
locust==2.20.0
```

### Step 4.2: Create Load Test

**File:** `tests/load/locustfile.py`
```python
from locust import HttpUser, task, between
import random

class EcommerceUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Register and login before starting tasks."""
        # Register
        email = f"loadtest{random.randint(1, 100000)}@test.com"
        response = self.client.post("/api/v1/auth/register", json={
            "name": "Load Test User",
            "email": email,
            "password": "SecurePass123!@#"
        })

        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "SecurePass123!@#"
        })

        data = response.json()
        self.token = data["data"]["access_token"]

    @task(3)
    def view_products(self):
        """View product list."""
        self.client.get("/api/v1/products/")

    @task(2)
    def view_product_detail(self):
        """View single product."""
        self.client.get("/api/v1/products/prod_1")

    @task(1)
    def create_order(self):
        """Create an order."""
        self.client.post(
            "/api/v1/orders/",
            json={
                "items": [
                    {"product_id": "prod_1", "quantity": 2, "price": 29.99}
                ],
                "shipping_address": {
                    "full_name": "Test User",
                    "address_line1": "123 Test St",
                    "city": "Test City",
                    "state": "TS",
                    "postal_code": "12345",
                    "country": "US"
                },
                "payment_method": "stripe"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

### Run Load Test

```bash
# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Open browser: http://localhost:8089
```

---

## ✅ Final Checklist: From 8.5 to 9.5

### Critical (Must Have)
- [ ] PostgreSQL database implemented
- [ ] Alembic migrations configured
- [ ] Repository pattern implemented
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests for all endpoints
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Load testing completed (validated for 10k users)

### Important (Should Have)
- [ ] Prometheus metrics
- [ ] Performance monitoring
- [ ] Database query optimization
- [ ] Connection pool monitoring
- [ ] Distributed tracing setup
- [ ] Production logging configuration

### Nice to Have
- [ ] E2E tests
- [ ] API documentation updates
- [ ] Postman collection
- [ ] Database backup strategy
- [ ] Disaster recovery plan

---

## 📈 Expected Score After Completion

| Component | Score | Notes |
|-----------|-------|-------|
| Database | 9.5/10 | PostgreSQL + proper ORM |
| Testing | 9.0/10 | 80%+ coverage |
| Security | 9.0/10 | Already strong from Phase 1 |
| Architecture | 9.5/10 | Clean separation of concerns |
| Performance | 8.5/10 | Optimized queries + caching |
| Monitoring | 8.0/10 | Metrics + logging |
| CI/CD | 9.0/10 | Automated pipeline |
| Documentation | 8.5/10 | Comprehensive docs |

**Final Score: 9.5/10** 🎉

---

## 🚀 Quick Start Commands

```bash
# Week 1: Database
pip install -r requirements.txt
alembic upgrade head
pytest tests/

# Week 2: Testing
pip install -r requirements-dev.txt
pytest --cov=app

# Week 3: Performance
# Add monitoring endpoints
# Run performance tests

# Week 4: Deploy
docker-compose up -d
# Monitor metrics at /metrics
```

---

## 📞 Support

If you encounter issues during implementation:
1. Check the logs: `tail -f logs/app.log`
2. Verify database connection: `alembic current`
3. Run tests: `pytest -v`
4. Check metrics: `curl http://localhost:8000/metrics`

---

**Estimated Timeline:** 3-4 weeks
**Effort Required:** 1 senior developer full-time
**Cost Impact:** ~$20-30/month for production infrastructure
**Expected Uptime:** 99.9%+
