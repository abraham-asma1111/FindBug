#!/bin/bash
# Test Runner Script for Bug Bounty Platform
# Runs all tests with coverage reporting

set -e

echo "========================================="
echo "Bug Bounty Platform - Test Suite"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if ! docker ps | grep -q bugbounty-postgres-prod; then
    echo -e "${RED}PostgreSQL container not running. Starting...${NC}"
    docker start bugbounty-postgres-prod
    sleep 3
fi

# Create test database if it doesn't exist
echo -e "${YELLOW}Setting up test database...${NC}"
docker exec bugbounty-postgres-prod psql -U bugbounty_user -d postgres -c "CREATE DATABASE test_bugbounty;" 2>/dev/null || echo "Test database already exists"

# Clean test database
echo -e "${YELLOW}Cleaning test database...${NC}"
docker exec bugbounty-postgres-prod psql -U bugbounty_user -d test_bugbounty -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO bugbounty_user; GRANT ALL ON SCHEMA public TO public;"

echo ""
echo "========================================="
echo "Running Tests"
echo "========================================="
echo ""

# Run tests based on argument
case "${1:-all}" in
    unit)
        echo -e "${GREEN}Running Unit Tests...${NC}"
        pytest tests/unit/ -v
        ;;
    integration)
        echo -e "${GREEN}Running Integration Tests...${NC}"
        pytest tests/integration/ -v
        ;;
    freq)
        echo -e "${GREEN}Running All FREQ Tests...${NC}"
        pytest tests/integration/test_all_freqs.py -v
        ;;
    business)
        echo -e "${GREEN}Running Business Logic Tests...${NC}"
        pytest tests/unit/test_business_logic.py -v
        ;;
    quick)
        echo -e "${GREEN}Running Quick Test (business logic only)...${NC}"
        pytest tests/unit/test_business_logic.py -v
        ;;
    all)
        echo -e "${GREEN}Running All Tests...${NC}"
        pytest -v --tb=short
        ;;
    *)
        echo -e "${RED}Unknown test type: $1${NC}"
        echo "Usage: ./run_tests.sh [unit|integration|freq|business|quick|all]"
        exit 1
        ;;
esac

# Check test results
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ All Tests Passed!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}✗ Tests Failed${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi
