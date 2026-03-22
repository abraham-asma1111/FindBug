# Testing Quick Start

## Why Integration Tests First?

After merging 3 major branches (payment-method, Live-hacking-Event, simulation-platform), we need to verify:
- ✅ All 23 endpoint modules are registered
- ✅ Database models work together
- ✅ Critical user flows work end-to-end
- ✅ No merge conflicts broke functionality

## Quick Setup (5 minutes)

### 1. Install Test Dependencies
```bash
cd backend
pip install pytest pytest-cov httpx
```

### 2. Create Test Database
```bash
# Option 1: Using createdb
createdb test_bugbounty

# Option 2: Using psql
psql -U postgres -c "CREATE DATABASE test_bugbounty;"
```

### 3. Update Test Database URL
Edit `tests/conftest.py` line 15:
```python
TEST_DATABASE_URL = "postgresql://YOUR_USER:YOUR_PASS@localhost:5432/test_bugbounty"
```

### 4. Run Tests
```bash
pytest tests/integration/ -v
```

## What Gets Tested?

### ✅ Test 1: Health & Endpoints (test_health_and_endpoints.py)
- Health check works
- All 23 endpoint modules registered
- API docs accessible
- CORS configured

### ✅ Test 2: Authentication (test_auth_flow.py)
- Researcher registration & login
- Organization registration & login
- JWT token generation
- Protected endpoints work

### ✅ Test 3: Bug Bounty Flow (test_bug_bounty_flow.py)
- Create program
- Submit vulnerability report
- Triage report
- Approve bounty
- Process payment with 30% commission

### ✅ Test 4: Subscription Flow (test_subscription_flow.py)
- View subscription tiers
- Subscribe to tier (quarterly billing)
- Check subscription status
- Calculate 30% commission
- View billing history

## Expected Output

```bash
tests/integration/test_health_and_endpoints.py::test_health_check PASSED
tests/integration/test_health_and_endpoints.py::test_all_endpoints_registered PASSED
tests/integration/test_auth_flow.py::TestAuthenticationFlow::test_researcher_registration_and_login PASSED
tests/integration/test_bug_bounty_flow.py::TestBugBountyFlow::test_complete_bug_bounty_flow PASSED
tests/integration/test_subscription_flow.py::TestSubscriptionFlow::test_commission_calculation PASSED

======================== 15 passed in 5.23s ========================
```

## If Tests Fail

### Common Issues:

1. **Database connection error**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Start if needed
   sudo systemctl start postgresql
   ```

2. **Import errors**
   ```bash
   # Make sure you're in backend directory
   cd backend
   pytest tests/integration/
   ```

3. **Table doesn't exist**
   ```bash
   # Run migrations on test database
   alembic upgrade head
   ```

4. **Endpoint not found (404)**
   - Check `backend/src/main.py` has all routers registered
   - Check `backend/src/api/v1/endpoints/__init__.py` imports all modules

## Next Steps After Integration Tests Pass

1. ✅ **Integration tests pass** → Merge is successful!
2. 🔧 **Some tests fail** → Fix the issues (likely import or registration problems)
3. 📝 **Add more integration tests** → PTaaS, Live Events, Simulation, AI Red Teaming
4. 🧪 **Start unit tests** → Test individual service methods

## Quick Commands

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_auth_flow.py -v

# Run with coverage
pytest tests/integration/ --cov=src --cov-report=html

# Stop on first failure
pytest tests/integration/ -x

# Run only failed tests from last run
pytest --lf
```

## Integration vs Unit Testing

**Integration Tests (Now)**
- Test multiple components together
- Verify end-to-end flows
- Catch integration issues
- Slower but more comprehensive

**Unit Tests (Later)**
- Test individual functions
- Verify business logic
- Fast and focused
- Better for TDD

Start with integration tests to verify the merge worked, then add unit tests for critical business logic.
