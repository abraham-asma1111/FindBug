# Testing Guide

## Overview
This directory contains integration and unit tests for the Bug Bounty Platform.

## Test Structure
```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── integration/                   # Integration tests (test multiple components)
│   ├── test_health_and_endpoints.py
│   ├── test_auth_flow.py
│   ├── test_bug_bounty_flow.py
│   └── test_subscription_flow.py
└── unit/                          # Unit tests (test individual functions)
    └── (to be added)
```

## Setup

### 1. Install Test Dependencies
```bash
cd backend
pip install pytest pytest-cov httpx
```

### 2. Create Test Database
```bash
# Create PostgreSQL test database
createdb test_bugbounty

# Or using psql
psql -U postgres -c "CREATE DATABASE test_bugbounty;"
```

### 3. Configure Test Environment
Update `conftest.py` with your test database credentials:
```python
TEST_DATABASE_URL = "postgresql://your_user:your_pass@localhost:5432/test_bugbounty"
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Integration Tests Only
```bash
pytest tests/integration/
```

### Run Specific Test File
```bash
pytest tests/integration/test_auth_flow.py
```

### Run Specific Test
```bash
pytest tests/integration/test_auth_flow.py::TestAuthenticationFlow::test_researcher_registration_and_login
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run and Stop on First Failure
```bash
pytest -x
```

## Test Priorities

### Phase 1: Integration Tests (Current)
✅ Health check and endpoint registration
✅ Authentication flow
✅ Bug bounty flow (program → report → triage → payment)
✅ Subscription flow (quarterly billing + 30% commission)

### Phase 2: Additional Integration Tests (Next)
- [ ] PTaaS engagement flow
- [ ] Live hacking events flow
- [ ] Simulation platform flow
- [ ] AI red teaming flow
- [ ] Code review flow
- [ ] SSDLC integration flow

### Phase 3: Unit Tests (After Integration)
- [ ] Service layer tests
- [ ] Repository tests
- [ ] Validation tests
- [ ] Utility function tests

## Expected Test Results

After running integration tests, you should see:
- ✅ All endpoints registered (23 modules)
- ✅ Authentication working (register, login, JWT)
- ✅ Database operations working (CRUD)
- ✅ Business logic working (commission calculation, etc.)

## Troubleshooting

### Database Connection Error
```
Error: could not connect to database
```
**Solution**: Ensure PostgreSQL is running and test database exists

### Import Errors
```
ModuleNotFoundError: No module named 'src'
```
**Solution**: Run tests from backend directory: `cd backend && pytest`

### Migration Errors
```
Table does not exist
```
**Solution**: Run migrations on test database:
```bash
alembic upgrade head
```

## CI/CD Integration

These tests can be integrated into GitHub Actions:
```yaml
- name: Run Tests
  run: |
    cd backend
    pytest --cov=src --cov-report=xml
```

## Next Steps

1. Run integration tests to verify merge
2. Fix any failing tests
3. Add more integration tests for remaining features
4. Start writing unit tests for critical business logic
