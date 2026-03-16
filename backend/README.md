# Bug Bounty Platform - Backend

FastAPI backend for the Bug Bounty and Simulation Platform.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start Services (Docker)
```bash
cd ..
docker-compose up -d postgres redis minio
```

### 5. Run Migrations
```bash
alembic upgrade head
```

### 6. Start Development Server
```bash
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── src/
│   ├── core/           # Core utilities (config, security, database)
│   ├── domain/         # Domain models and repositories
│   ├── services/       # Business logic
│   ├── api/            # API endpoints and schemas
│   ├── tasks/          # Celery tasks
│   └── utils/          # Helper functions
├── tests/              # Test suite
├── migrations/         # Alembic migrations
└── scripts/            # Utility scripts
```

## Development

### Run Tests
```bash
pytest
pytest --cov=src tests/
```

### Code Formatting
```bash
black src/
isort src/
flake8 src/
```

### Create Migration
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Team

- Niway Tadesse - Backend Lead
- Abraham Asimamaw - Frontend Lead
- Melkamu Tesfa - Full-stack & DevOps
