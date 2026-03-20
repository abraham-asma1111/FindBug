# FREQ-20 Subscription Implementation Summary

## Overview

Successfully implemented the dual revenue model for FREQ-20, combining quarterly subscription fees with per-transaction commissions.

---

## Dual Revenue Model

### Revenue Stream 1: Subscription Fees
- **Billing Cycle**: Every 4 months (quarterly)
- **Payments Per Year**: 3 times
- **Tiers**:
  - **Basic**: 15,000 ETB/quarter
    - 3 programs, 50 researchers, 20 reports/month
    - Email support
  - **Professional**: 45,000 ETB/quarter
    - 10 programs, 200 researchers, 100 reports/month
    - PTaaS, Code Review, Live Events, SSDLC Integration
    - Priority support
  - **Enterprise**: 120,000 ETB/quarter
    - Unlimited programs, researchers, reports
    - All features including AI Red Teaming
    - Dedicated support

### Revenue Stream 2: Bounty Commissions
- **Commission Rate**: 30% of researcher amount
- **Calculation**: Organization pays researcher_amount + 30%
- **Example**:
  ```
  Researcher receives: 1,000 ETB
  Platform commission: 300 ETB (30%)
  Organization pays: 1,300 ETB total
  ```

---

## Implementation Components

### 1. Database Tables (3 new tables)
- `subscription_tier_pricing` - Tier configuration
- `organization_subscriptions` - Active subscriptions
- `subscription_payments` - Payment records

### 2. Services (1 new service)
- `SubscriptionService` - Complete subscription lifecycle management
  - Create subscription with trial support
  - Automatic billing cycle management
  - Payment processing
  - Overdue tracking and suspension
  - Revenue reporting

### 3. API Endpoints (10 new endpoints)

#### Subscription Management
- `GET /api/v1/subscriptions/tiers` - List available tiers
- `POST /api/v1/subscriptions` - Create subscription
- `GET /api/v1/subscriptions/organization/{id}` - Get org subscription
- `GET /api/v1/subscriptions/{id}/payments` - Payment history
- `POST /api/v1/subscriptions/payments/{id}/mark-paid` - Mark payment paid
- `POST /api/v1/subscriptions/{id}/cancel` - Cancel subscription
- `GET /api/v1/subscriptions/overdue` - List overdue subscriptions
- `POST /api/v1/subscriptions/suspend-overdue` - Suspend overdue accounts
- `GET /api/v1/subscriptions/revenue-report` - Subscription revenue
- `POST /api/v1/subscriptions/seed-tiers` - Initialize tier pricing

#### Financial Reporting
- `GET /api/v1/financial/revenue-summary` - Combined revenue (subscriptions + commissions)
- `GET /api/v1/financial/commission-report` - Detailed commission report
- `GET /api/v1/financial/pending-payments` - All pending payments
- `GET /api/v1/financial/overdue-payments` - All overdue payments

---

## Key Features

### Automatic Billing Cycle
```python
# Quarterly billing (every 4 months)
start_date = 2026-01-01
current_period_start = 2026-01-01
current_period_end = 2026-05-01  # +4 months
next_billing_date = 2026-05-01

# After payment:
current_period_start = 2026-05-01
current_period_end = 2026-09-01  # +4 months
next_billing_date = 2026-09-01
```

### Trial Period Support
```python
# Create subscription with 30-day trial
subscription = service.create_subscription(
    organization_id=org_id,
    tier="professional",
    trial_days=30
)
# No payment due until trial ends
```

### Overdue Management
```python
# Automatically suspend subscriptions overdue by 7+ days
suspended_count = service.suspend_overdue_subscriptions(
    days_threshold=7
)
```

### Revenue Reporting
```python
# Get comprehensive revenue breakdown
report = financial.get_revenue_summary(
    start_date="2026-01-01",
    end_date="2026-12-31"
)
# Returns:
# - Subscription revenue by tier
# - Commission revenue from bounties
# - Total revenue
# - Revenue breakdown percentages
```

---

## Integration with Existing Systems

### Bounty Service Integration
Updated `BountyService` to use `EnhancedPayoutService`:

```python
# New method for processing payments
result = bounty_service.process_bounty_payment(
    report_id=report_id,
    approved_by=user_id,
    payment_method="telebirr",
    payment_details={"phone_number": "+251912345678"}
)
# Automatically:
# - Calculates 30% commission
# - Verifies KYC
# - Processes via Saga pattern
# - Updates report status
# - Sends notifications
```

### Financial Dashboard
New unified financial reporting showing both revenue streams:

```json
{
  "subscription_revenue": {
    "total": 180000.00,
    "payment_count": 4,
    "by_tier": {
      "basic": {"count": 2, "revenue": 30000.00},
      "professional": {"count": 2, "revenue": 90000.00}
    }
  },
  "commission_revenue": {
    "total": 45000.00,
    "payment_count": 150
  },
  "total_revenue": 225000.00,
  "revenue_breakdown": {
    "subscription_percentage": 80.0,
    "commission_percentage": 20.0
  }
}
```

---

## Usage Examples

### 1. Create Subscription
```python
POST /api/v1/subscriptions
{
  "organization_id": "uuid",
  "tier": "professional",
  "trial_days": 30
}
```

### 2. Mark Subscription Payment Paid
```python
POST /api/v1/subscriptions/payments/{payment_id}/mark-paid
{
  "payment_method": "bank_transfer",
  "gateway_transaction_id": "TXN123456"
}
```

### 3. Get Revenue Summary
```python
GET /api/v1/financial/revenue-summary?start_date=2026-01-01&end_date=2026-12-31
```

### 4. Process Bounty Payment (with commission)
```python
result = bounty_service.process_bounty_payment(
    report_id=report_id,
    approved_by=user_id,
    payment_method="manual"
)
# Automatically calculates 30% commission
```

---

## Database Schema

### organization_subscriptions
```sql
subscription_id UUID PRIMARY KEY
organization_id UUID REFERENCES organizations(id)
tier VARCHAR(50)  -- basic, professional, enterprise
status VARCHAR(50)  -- active, pending, expired, cancelled, suspended
subscription_fee DECIMAL(15,2)
billing_cycle_months NUMERIC(3,0) DEFAULT 4
payments_per_year NUMERIC(2,0) DEFAULT 3
start_date TIMESTAMP
current_period_start TIMESTAMP
current_period_end TIMESTAMP
next_billing_date TIMESTAMP
features JSON
```

### subscription_payments
```sql
payment_id UUID PRIMARY KEY
subscription_id UUID REFERENCES organization_subscriptions
organization_id UUID REFERENCES organizations
amount DECIMAL(15,2)
period_start TIMESTAMP
period_end TIMESTAMP
status VARCHAR(50)  -- pending, paid, failed, refunded
due_date TIMESTAMP
paid_at TIMESTAMP
invoice_number VARCHAR(100)
```

### subscription_tier_pricing
```sql
pricing_id UUID PRIMARY KEY
tier VARCHAR(50) UNIQUE
name VARCHAR(100)
quarterly_price DECIMAL(15,2)
max_programs NUMERIC(5,0)
max_researchers NUMERIC(6,0)
ptaas_enabled BOOLEAN
code_review_enabled BOOLEAN
ai_red_teaming_enabled BOOLEAN
support_level VARCHAR(50)
```

---

## Testing

### Seed Tier Pricing
```bash
POST /api/v1/subscriptions/seed-tiers
# Creates Basic, Professional, Enterprise tiers
```

### Test Subscription Flow
1. Create subscription with trial
2. Wait for trial to end (or manually set next_billing_date)
3. Mark payment as paid
4. Verify subscription renewed
5. Check revenue report

### Test Commission Flow
1. Approve bounty for $1000
2. Process payment
3. Verify commission = $300
4. Verify organization paid $1300
5. Check commission report

---

## Migration

Run migrations to create tables:
```bash
cd backend
alembic upgrade head
```

This will create:
- `subscription_tier_pricing` table
- `organization_subscriptions` table
- `subscription_payments` table

---

## Next Steps

1. **Seed Tier Pricing**: Call `/api/v1/subscriptions/seed-tiers` to initialize tiers
2. **Test Subscription Creation**: Create test subscriptions for organizations
3. **Test Payment Processing**: Process test payments
4. **Monitor Revenue**: Use financial endpoints to track revenue
5. **Payment Gateway Integration**: Integrate actual Telebirr, CBE Birr, Bank APIs (your task)

---

## Files Modified/Created

### New Files (9)
- `backend/src/domain/models/subscription.py`
- `backend/src/services/subscription_service.py`
- `backend/src/api/v1/endpoints/subscription.py`
- `backend/src/api/v1/endpoints/financial.py`
- `backend/src/api/v1/schemas/subscription.py`
- `backend/migrations/versions/2026_03_20_2230_create_subscription_tables.py`
- `backend/FREQ-20-RAD-IMPLEMENTATION-PROGRESS.md`
- `backend/FREQ-20-SUBSCRIPTION-IMPLEMENTATION-SUMMARY.md`

### Modified Files (4)
- `backend/src/domain/models/__init__.py` (added subscription exports)
- `backend/src/services/bounty_service.py` (added process_bounty_payment)
- `backend/src/api/v1/endpoints/__init__.py` (added subscription, financial)
- `backend/src/main.py` (registered subscription, financial routers)

---

## Summary

The subscription implementation is complete and ready for use. Organizations can now:
- Subscribe to tiered plans (Basic, Professional, Enterprise)
- Pay quarterly (every 4 months, 3 times/year)
- Platform earns from both subscriptions AND 30% commission on bounties
- Comprehensive financial reporting shows both revenue streams
- Automatic billing cycle management
- Overdue payment tracking and suspension

The dual revenue model ensures sustainable platform growth through predictable subscription income plus performance-based commission revenue.
