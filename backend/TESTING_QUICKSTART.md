# Testing Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
cd backend
pip install pytest pytest-cov pytest-asyncio faker
```

### 2. Start PostgreSQL
```bash
docker start bugbounty-postgres-prod
```

### 3. Run Tests
```bash
./run_tests.sh
```

That's it! 🎉

## 📊 Test Options

### Run All Tests
```bash
./run_tests.sh all
```

### Run Only Unit Tests
```bash
./run_tests.sh unit
```

### Run Only Integration Tests
```bash
./run_tests.sh integration
```

### Run All 48 FREQ Tests
```bash
./run_tests.sh freq
```

### Run with Coverage Report
```bash
./run_tests.sh coverage
# Open htmlcov/index.html in browser
```

### Run Quick Tests (No Coverage)
```bash
./run_tests.sh quick
```

## 🎯 Test Specific Features

### Test Authentication (FREQ-01)
```bash
pytest tests/integration/test_all_freqs.py::TestFREQ01_Authentication -v
```

### Test Subscription Model (FREQ-20)
```bash
pytest tests/integration/test_all_freqs.py::TestFREQ20_Subscription -v
pytest tests/unit/test_subscription_service.py -v
```

### Test Bug Bounty Flow (FREQ-02-08)
```bash
pytest tests/integration/test_bug_bounty_flow.py -v
```

### Test PTaaS (FREQ-29-38)
```bash
pytest tests/integration/test_all_freqs.py::TestFREQ29_31_PTaaS -v
```

### Test Simulation Platform (FREQ-23-28)
```bash
pytest tests/integration/test_all_freqs.py::TestFREQ23_28_Simulation -v
```

### Test Live Events (FREQ-43-44)
```bash
pytest tests/integration/test_all_freqs.py::TestFREQ43_44_LiveEvents -v
```

## 🔍 Debugging Failed Tests

### Run with Verbose Output
```bash
pytest -vv
```

### Stop on First Failure
```bash
pytest -x
```

### Run Specific Test
```bash
pytest tests/unit/test_auth_service.py::TestAuthService::test_hash_password -v
```

### Show Print Statements
```bash
pytest -s
```

### Run Last Failed Tests
```bash
pytest --lf
```

## 📈 Coverage Reports

### Generate HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Generate Terminal Coverage Report
```bash
pytest --cov=src --cov-report=term-missing
```

### Generate XML Coverage (for CI/CD)
```bash
pytest --cov=src --cov-report=xml
```

## 🛠️ Troubleshooting

### Database Connection Error
```bash
# Start PostgreSQL
docker start bugbounty-postgres-prod

# Create test database
docker exec bugbounty-postgres-prod psql -U bugbounty_user -d postgres -c "CREATE DATABASE test_bugbounty;"
```

### Import Errors
```bash
# Ensure you're in backend directory
cd backend
pytest
```

### Clean Test Database
```bash
docker exec bugbounty-postgres-prod psql -U bugbounty_user -d test_bugbounty -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Permission Denied on run_tests.sh
```bash
chmod +x run_tests.sh
```

## 📝 Test Structure

```
tests/
├── unit/                           # Unit tests (fast, isolated)
│   ├── test_auth_service.py       # Authentication logic
│   ├── test_subscription_service.py  # Subscription & commission
│   └── test_report_service.py     # Report validation
│
├── integration/                    # Integration tests (full workflows)
│   ├── test_all_freqs.py          # All 48 FREQs ⭐
│   ├── test_auth_flow.py          # Auth workflow
│   ├── test_bug_bounty_flow.py    # Bug bounty workflow
│   └── test_subscription_flow.py  # Subscription workflow
│
└── conftest.py                     # Shared fixtures
```

## ✅ What's Tested

### All 48 FREQs Covered:
- ✅ FREQ-01: Authentication
- ✅ FREQ-02: Report Submission
- ✅ FREQ-03-08: Program Management
- ✅ FREQ-09: Messaging
- ✅ FREQ-10: Bounty Payments
- ✅ FREQ-11: Reputation
- ✅ FREQ-12: Analytics
- ✅ FREQ-13: Notifications
- ✅ FREQ-14: Search
- ✅ FREQ-15: Audit Logs
- ✅ FREQ-16: Triage
- ✅ FREQ-17: Duplicate Detection
- ✅ FREQ-18: File Attachments
- ✅ FREQ-19: Email Notifications
- ✅ FREQ-20: Subscription (Quarterly + 30% Commission)
- ✅ FREQ-21: Payment Methods
- ✅ FREQ-22: KYC
- ✅ FREQ-23-28: Simulation Platform
- ✅ FREQ-29-31: PTaaS
- ✅ FREQ-32-33: Matching
- ✅ FREQ-34: PTaaS Dashboard
- ✅ FREQ-35-38: PTaaS Advanced
- ✅ FREQ-39-40: Recommendations
- ✅ FREQ-41: Code Review
- ✅ FREQ-42: SSDLC Integration
- ✅ FREQ-43-44: Live Events
- ✅ FREQ-45-48: AI Red Teaming

## 🎓 Writing New Tests

### Unit Test Template
```python
def test_your_function(self):
    # Arrange
    input_data = "test"
    
    # Act
    result = your_function(input_data)
    
    # Assert
    assert result == expected_value
```

### Integration Test Template
```python
def test_your_workflow(self, client, researcher_token):
    headers = {"Authorization": f"Bearer {researcher_token}"}
    
    # Step 1: Create resource
    response = client.post("/api/v1/resource", headers=headers, json={...})
    assert response.status_code == 201
    
    # Step 2: Verify resource
    resource_id = response.json()["id"]
    response = client.get(f"/api/v1/resource/{resource_id}", headers=headers)
    assert response.status_code == 200
```

## 📚 Additional Resources

- Full Test Documentation: `tests/README.md`
- Coverage Report: `TEST_COVERAGE_REPORT.md`
- Test Runner Script: `run_tests.sh`
- Pytest Docs: https://docs.pytest.org/

## 🚦 CI/CD Integration

Tests run automatically on:
- Every commit to main
- Every pull request
- Nightly builds

### GitHub Actions Example
```yaml
- name: Run Tests
  run: |
    cd backend
    ./run_tests.sh coverage
```

## 💡 Tips

1. **Run tests before committing**: `./run_tests.sh quick`
2. **Check coverage regularly**: `./run_tests.sh coverage`
3. **Test one feature at a time**: `pytest tests/unit/test_auth_service.py`
4. **Use fixtures**: Leverage `conftest.py` fixtures
5. **Mock external services**: Don't call real payment APIs in tests

## 🎯 Coverage Goals

- Overall: > 80% ✅
- Critical paths: > 95% ✅
- Business logic: > 90% ✅
- API endpoints: 100% ✅

---

**Need Help?** Check `tests/README.md` for detailed documentation.
