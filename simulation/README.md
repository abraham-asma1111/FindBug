# 🎯 Bug Bounty Simulation Platform

## Overview
Isolated bug bounty practice environment for researchers to develop skills safely.

## 📋 Features Implemented

### ✅ Core Simulation Features (FREQ-23 to FREQ-28)
- **FREQ-23**: Simulation Environment - Complete isolated practice targets
- **FREQ-24**: Simulation Workflow Mirroring - Real bug bounty process simulation
- **FREQ-25**: Simulation Difficulty Levels - Beginner to Expert challenges
- **FREQ-26**: Simulation Reporting - Detailed performance analytics
- **FREQ-27**: Simulation Data Isolation - Complete environment separation
- **FREQ-28**: Simulation Feedback - Personalized improvement tips

### 🔒 Security & Isolation
- Container-based isolation for each simulation
- Network separation from production systems
- Time-limited sessions with automatic cleanup
- Private scoring (BR-13: No public leaderboards)

### 🎮 Challenge Types
- **Web Application Security**: XSS, SQLi, CSRF, RCE
- **API Security**: Authentication bypass, data exposure
- **Mobile Security**: Android/iOS vulnerability patterns
- **Network Security**: Service enumeration, exploitation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend    │    │  Simulation    │    │   Isolation    │
│   (React)     │◄──►│     API        │◄──►│  Containers    │
│   Port:3000   │    │   Port:8001    │    │   Docker DIND  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis        │    │  PostgreSQL     │    │   File Storage │
│   Port:6380   │    │   Port:5433    │    │   /app/uploads │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for development)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd simulation

# Start simulation platform
docker-compose up -d

# View API documentation
open http://localhost:8001/docs
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Run database migrations
alembic upgrade head
```

## 📚 API Documentation

### Core Endpoints
- `GET /api/v1/simulation/levels` - Available difficulty levels
- `POST /api/v1/simulation/start` - Start new simulation
- `GET /api/v1/simulation/{id}` - Get simulation details
- `POST /api/v1/simulation/{id}/submit` - Submit results

### Challenge Endpoints
- `GET /api/v1/challenges/` - List available challenges
- `POST /api/v1/challenges/{id}/start` - Start challenge
- `POST /api/v1/challenges/{id}/submit` - Submit solution

### Isolation Endpoints
- `POST /api/v1/isolation/create` - Create isolated environment
- `GET /api/v1/isolation/{id}` - Get session details
- `POST /api/v1/isolation/{id}/terminate` - End session

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost:5433/simulation_db
REDIS_URL=redis://localhost:6380/0
SECRET_KEY=your-secret-key
ISOLATION_ENABLED=true
MAX_SIMULATION_TIME=7200  # 2 hours
```

### Docker Configuration
- **Database**: PostgreSQL 15 on port 5433
- **Cache**: Redis 7 on port 6380
- **API**: FastAPI on port 8001
- **Isolation**: Docker-in-Docker for container isolation

## 📊 Scoring System

### Difficulty Levels
| Level | Time Limit | Max Hints | Base Score |
|--------|-------------|-------------|-------------|
| Beginner | 1 hour | 3 | 100 |
| Intermediate | 1.5 hours | 2 | 200 |
| Advanced | 2 hours | 1 | 300 |
| Expert | 3 hours | 0 | 500 |

### Score Calculation
```
Total Score = Base Score + Time Bonus - Hint Penalty + Accuracy Bonus
```

### Business Rules (BR-13)
- ✅ Simulation scores are private to individual users
- ✅ No public leaderboards for simulation results
- ✅ Scores don't contribute to researcher reputation
- ✅ No real rewards for simulation completion

## 🔒 Security Features

### Isolation
- Each simulation runs in isolated Docker container
- Network separation prevents access to production systems
- Automatic cleanup after session expiration
- Resource limits (CPU, Memory, Disk)

### Data Protection
- No persistent data storage in simulation containers
- All simulation data isolated from main platform
- Automatic sanitization of user inputs
- Audit logging for all simulation activities

## 📈 Monitoring & Analytics

### Metrics Tracked
- Session duration and completion rates
- Vulnerability identification accuracy
- Hint usage patterns
- Performance by difficulty level
- User progress over time

### Feedback System
- Personalized improvement tips
- Detailed scoring breakdown
- Performance comparison with averages
- Recommended next challenges

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/
```

### Test Coverage
- All API endpoints tested
- Database operations verified
- Isolation security validated
- Performance benchmarks included

## 📝 Business Rules Implemented

### BR-13: Simulation Progression and Scoring
✅ Internal scoring system based on challenge completion
✅ Severity accuracy tracking
✅ Private scores visible only to user
✅ No contribution to public leaderboards
✅ No real rewards or reputation impact

### Data Isolation (FREQ-27)
✅ Complete separation from production data
✅ Container-based isolation
✅ Network segmentation
✅ Automatic cleanup and sanitization

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose exec simulation-api alembic upgrade head

# Create admin user
docker-compose exec simulation-api python scripts/create_admin.py
```

### Environment Configuration
- **Development**: `docker-compose.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`

## 📞 Support

### Documentation
- [API Documentation](http://localhost:8001/docs)
- [Business Rules](./docs/business-rules.md)
- [Security Guidelines](./docs/security.md)

### Contact
- Platform Administrator: admin@findbug.com
- Technical Support: support@findbug.com
- Security Issues: security@findbug.com

## 📄 License

© 2026 FindBug Platform. All rights reserved.

---

**🎯 Practice Safe. Build Skills. Join the Bug Bounty Community!**
