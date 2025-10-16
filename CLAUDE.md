# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FindMyGap is an AI-powered product gap analysis platform built with FastAPI (backend) + Next.js (frontend). The application analyzes customer feedback from multiple sources (app stores, e-commerce reviews, Reddit, support tickets) using LLM analysis via OpenRouter to identify unmet market needs and product opportunities.

## Architecture

**Monorepo Structure:**
- `backend/` - FastAPI backend with async architecture
- `frontend/` - Next.js 14+ frontend with App Router
- Root-level `docker-compose.yml` for orchestrating all services

**Key Technologies:**
- Backend: FastAPI, SQLAlchemy 2.0+, Alembic, Celery, Agno (AI agent framework)
- Frontend: Next.js 14+, TypeScript, Clerk.com (auth), Tailwind CSS
- Infrastructure: PostgreSQL, Redis, Kafka, RabbitMQ, Pinecone (vector DB)
- LLM: OpenRouter (500+ models), Agno for agent orchestration
- Package Manager: uv (backend), npm (frontend)

## Development Commands

### Backend

```bash
cd backend

# Environment setup
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
uv run pytest                              # All tests
uv run pytest tests/unit/                  # Unit tests only
uv run pytest tests/integration/           # Integration tests
uv run pytest --cov=app --cov-report=html  # With coverage

# Code quality
uv run black .                    # Format code
uv run isort .                    # Sort imports
uv run ruff check .               # Lint
uv run mypy .                     # Type check

# Database migrations
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
uv run alembic downgrade -1

# CLI commands
uv run python -m app.cli database init     # Initialize database
uv run python -m app.cli database migrate  # Run migrations
uv run python -m app.cli health check      # Health check
```

### Frontend

```bash
cd frontend

# Development
npm install
npm run dev              # Start dev server on port 3000

# Production build
npm run build
npm run start

# Code quality
npm run lint             # ESLint
npm run type-check       # TypeScript check
```

### Docker

```bash
# Start all services (from project root)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

## Backend Architecture Details

### Async Database Layer
- **Full async support** with SQLAlchemy 2.0+ and asyncpg
- **Repository pattern** in `backend/app/database/repositories/`
- **Transaction management** via `backend/app/database/transaction.py`
- All database operations use `AsyncSession` - never use sync Session

### Dependency Injection
- **DI container** manages service lifecycle (singleton, scoped, transient)
- Services are injected via FastAPI's `Depends()`
- Request-scoped services auto-cleanup after request
- Never use global service instances

### Configuration System
- **Pydantic Settings** in `backend/app/config.py`
- Environment-aware config (development, testing, staging, production)
- Secrets management via env vars or Docker/K8s secrets
- Startup validation checks configuration security

### Error Handling
- Structured exceptions in `backend/app/exceptions.py` and `backend/app/core/exceptions.py`
- Rich context with request correlation IDs
- Auto error tracking and aggregation
- Circuit breakers and retry mechanisms with exponential backoff

### LLM Integration
- **Agno framework** for AI agent orchestration (`backend/app/core/llm/`)
- **OpenRouter** provides access to 500+ models
- Memory systems in `backend/app/core/memory/`:
  - Agno-based memory (preferred, uses Pinecone vector DB)
  - Redis memory (fallback)
  - In-memory (dev/testing only)
- Factory pattern for switching LLM providers

### Background Tasks
- **Celery workers** in `backend/app/tasks/`
- Three specialized queues:
  - `general` - General tasks (2 workers)
  - `chat` - Chat processing (3 workers)
  - `llm` - LLM-intensive tasks (2 workers with prefork pool)
- **Celery Flower** monitoring on port 5555

### Security
- **Database authentication** with password policies
- JWT tokens with configurable expiration
- API key management with permissions tracking
- Rate limiting per endpoint
- Input validation and sanitization (`backend/app/core/security/`)
- **Clerk integration** for frontend authentication

### API Structure
- API v1 routes in `backend/app/api/v1/`
- Health checks: `/api/v1/health/` (database, redis, kafka checks)
- Metrics: `/api/v1/metrics/` (Prometheus-compatible)
- Standardized response wrapper for consistency

## Frontend Architecture Details

### Next.js App Router
- Uses Next.js 14+ App Router (not Pages Router)
- Routes in `frontend/src/app/`
- Server and client components pattern

### Authentication
- **Clerk.com** integration for user authentication
- Google social login enabled
- Protected routes with automatic redirection
- JWT tokens passed to backend API

### API Communication
- API client in `frontend/src/lib/api.ts`
- Backend URL from `NEXT_PUBLIC_API_URL` env var
- HTTP polling for real-time updates (WebSocket not enabled)
- Error handling with toast notifications

### State Management
- Context-based state management
- Custom hooks in `frontend/src/hooks/`
- `useChat` hook for chat functionality

### Styling
- Tailwind CSS with custom design system
- Dark theme by default with gradient backgrounds
- Responsive mobile-first design
- Components in `frontend/src/components/ui/` and `frontend/src/components/chat/`

## Database Models and Migrations

### Key Models (backend/app/database/models/)
- `user.py` - User accounts with authentication
- `chat_session.py` - Chat conversation sessions
- `chat_message.py` - Individual messages
- `completion.py` - Text completion records
- `api_key.py` - API key management
- `task_result.py` - Background task results

### Alembic Migrations
- Migrations in `backend/alembic/versions/`
- Current migration: `001_initial_migration.py`
- Always use `uv run alembic revision --autogenerate` for new migrations
- Test migrations with both upgrade and downgrade

## Environment Variables

### Backend (.env)
```bash
# Required
OPENROUTER_API_KEY=your-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/findmygap
SECRET_KEY=minimum-32-chars-secret
PINECONE_API_KEY=your-key

# Optional
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
KAFKA_BOOTSTRAP_SERVERS=localhost:9093
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your-key
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=FindMyGap
```

## Service Ports

- Frontend: 3000
- Backend API: 8000
- PostgreSQL: 5432
- Redis: 6379
- Kafka: 9092 (internal), 9093 (localhost)
- RabbitMQ: 5672 (AMQP), 15672 (management UI)
- Celery Flower: 5555
- Zookeeper: 2181

## Common Patterns

### Adding a New API Endpoint
1. Define Pydantic models in `backend/app/models/`
2. Create database models if needed in `backend/app/database/models/`
3. Create repository in `backend/app/database/repositories/`
4. Implement service logic in `backend/app/services/`
5. Add API route in `backend/app/api/v1/`
6. Write tests in `tests/unit/` or `tests/integration/`

### Adding a New Database Table
1. Create SQLAlchemy model in `backend/app/database/models/`
2. Import in `backend/app/database/models/__init__.py`
3. Generate migration: `uv run alembic revision --autogenerate -m "Add table"`
4. Review and edit migration in `backend/alembic/versions/`
5. Apply: `uv run alembic upgrade head`

### Adding Background Tasks
1. Define task in `backend/app/tasks/` (llm_tasks.py, chat_tasks.py, or general_tasks.py)
2. Use appropriate queue decorator: `@celery_app.task(queue='llm')`
3. Task submission via API: POST `/api/v1/tasks/`
4. Monitor in Celery Flower or via `/api/v1/tasks/stats`

### Working with LLMs
- LLM clients in `backend/app/core/llm/`
- Use factory: `LLMFactory.create(provider="openrouter")`
- Agno agents for multi-step workflows
- Memory storage via `backend/app/core/memory/factory.py`

## Testing Strategy

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test API endpoints and database operations
- **Mock external services**: LLM providers, Redis, Kafka in tests
- **Use async fixtures**: All tests use async/await pattern
- **In-memory SQLite** for test database isolation

## Production Deployment

### Security Checklist
1. Set strong SECRET_KEY (32+ characters)
2. Configure CORS_ORIGINS (no wildcards)
3. Set ENVIRONMENT=production
4. Use managed database (not Docker PostgreSQL)
5. Configure SSL/TLS certificates
6. Use production Pinecone instance
7. Set reasonable ACCESS_TOKEN_EXPIRE_MINUTES

### Docker Production
```bash
docker-compose -f docker-compose.yml up -d
docker-compose up --scale celery-worker-general=3 -d  # Scale workers
```

### Health Checks
- Liveness: `/api/v1/health/live`
- Readiness: `/api/v1/health/ready`
- Full health: `/api/v1/health/`
- Prometheus metrics: `/api/v1/metrics/prometheus`

## Important Notes

- **Never commit secrets** to version control
- **Use uv for Python** package management (not pip)
- **Always use async/await** for database operations
- **Type hints required** for all functions
- **Run tests before committing**: `uv run pytest`
- **Code formatting before commits**: `uv run black . && uv run isort .`
- **Frontend uses HTTP polling**, not WebSockets
- **Clerk handles auth**, backend validates JWT tokens
- **Agno is preferred** for LLM agent orchestration
- **PostgreSQL is the primary database** (SQLite for testing only)
- **Three Celery worker pools** for different task types
