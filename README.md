# FindBug - Bug Bounty and Its Simulation Platform

**Final Year Project - BSc Cyber Security**  
**Bahir Dar University**

## Team Members
- Niway Tadesse
- Abraham Asimamaw
- Melkamu Tesfa

**Advisor**: Yosef Worku

---

## Project Overview

A comprehensive bug bounty platform with integrated simulation environment for security researchers and organizations. The platform enables vulnerability reporting, penetration testing as a service (PTaaS), code review, and AI red teaming capabilities.

## Project Structure

```
Final-year-project/
├── backend/              # FastAPI backend application
├── frontend/             # Next.js frontend application
├── infrastructure/       # Infrastructure as code (Terraform, K8s)
├── simulation/           # Simulation environment
├── docker-compose.yml    # Docker orchestration
└── some documents/       # Project documentation and planning files
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Security**: bcrypt, passlib
- **Caching**: Redis
- **Task Queue**: Celery
- **Storage**: MinIO (S3-compatible)

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TBD
- **API Client**: Axios/Fetch

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **Reverse Proxy**: Nginx
- **Caching**: Varnish
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.13+
- Node.js 18+
- PostgreSQL 15

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## API Documentation

Once the backend is running, access the API documentation at:
- **Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc**: http://127.0.0.1:8001/redoc

## Current Implementation Status

### ✅ Completed (FREQ-01)
- Database schema aligned with Extended ERD
- User authentication system
- Multi-role registration (Researcher, Organization)
- JWT-based authentication
- Password security (hashing, strength validation)
- Account lockout mechanism
- Security audit logging
- API endpoints for auth operations

### 🚧 In Progress
- Profile management (FREQ-02)
- Bug bounty program creation
- Vulnerability reporting

### 📋 Planned
- Payment system integration
- PTaaS features
- Simulation environment
- Code review system
- AI red teaming
- Analytics and reporting

## Security Features

- OWASP Top 10 compliance
- Password hashing with SHA-256 + salt
- JWT token authentication
- Account lockout after failed attempts
- Input sanitization and validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Security event logging

## Database Schema

The database schema follows the Extended ERD design with 50+ tables covering:
- User management (6 tables)
- Bug bounty core (7 tables)
- Triage & validation (2 tables)
- Payment system (4 tables)
- PTaaS system (2 tables)
- Simulation environment (2 tables)
- And more...

See `some documents/docs/design/database-erd/` for detailed ERD diagrams.

## Documentation

All project documentation, planning files, and diagrams are located in the `some documents/` directory:
- Design documents and ERD diagrams
- Implementation guides
- Security documentation
- Activity diagrams
- Planning and validation documents

## Contributing

This is an academic project. For questions or contributions, please contact the team members.

## License

This project is developed as part of academic requirements at Bahir Dar University.

---

**Last Updated**: March 16, 2026
