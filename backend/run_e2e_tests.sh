#!/bin/bash
# E2E Test Runner Script
# Runs all end-to-end integration tests for the Bug Bounty Platform

echo "🧪 Starting E2E Integration Tests..."
echo "=================================="
echo ""

# Set test database URL
export TEST_DATABASE_URL="postgresql://bugbounty_user:changeme123@localhost:5432/test_bugbounty"

# Run tests by category
echo "📋 Running Authentication Tests (FREQ-01 to FREQ-05)..."
pytest tests/e2e/test_e2e_freq_01_05_authentication.py -v --tb=short

echo ""
echo "📋 Running Bug Bounty Core Tests (FREQ-06 to FREQ-11)..."
pytest tests/e2e/test_e2e_freq_06_11_bug_bounty_core.py -v --tb=short

echo ""
echo "📋 Running Platform Features Tests (FREQ-12 to FREQ-19)..."
pytest tests/e2e/test_e2e_freq_12_19_platform_features.py -v --tb=short

echo ""
echo "📋 Running Revenue Tests (FREQ-20 to FREQ-22)..."
pytest tests/e2e/test_e2e_freq_20_22_revenue.py -v --tb=short

echo ""
echo "📋 Running Simulation Tests (FREQ-23 to FREQ-28)..."
pytest tests/e2e/test_e2e_freq_23_28_simulation.py -v --tb=short

echo ""
echo "📋 Running PTaaS Tests (FREQ-29 to FREQ-37)..."
pytest tests/e2e/test_e2e_freq_29_37_ptaas.py -v --tb=short

echo ""
echo "📋 Running KYC & Wallet Tests (FREQ-38 to FREQ-40)..."
pytest tests/e2e/test_e2e_freq_38_40_kyc_wallet.py -v --tb=short

echo ""
echo "📋 Running Code Review & Events Tests (FREQ-41 to FREQ-44)..."
pytest tests/e2e/test_e2e_freq_41_44_code_review_events.py -v --tb=short

echo ""
echo "📋 Running AI Red Teaming Tests (FREQ-45 to FREQ-48)..."
pytest tests/e2e/test_e2e_freq_45_48_ai_red_teaming.py -v --tb=short

echo ""
echo "📋 Running Workflow Tests..."
pytest tests/e2e/test_e2e_researcher_workflow.py -v --tb=short
pytest tests/e2e/test_e2e_organization_workflow.py -v --tb=short
pytest tests/e2e/test_e2e_ptaas_workflow.py -v --tb=short
pytest tests/e2e/test_e2e_simulation_workflow.py -v --tb=short

echo ""
echo "📋 Running Complete Platform Test..."
pytest tests/e2e/test_e2e_complete_platform.py -v --tb=short

echo ""
echo "=================================="
echo "✅ E2E Test Run Complete!"
echo ""
echo "📊 Generate summary report:"
echo "pytest tests/e2e/ --tb=no -q"
