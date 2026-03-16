# Database Schema Documentation

**Project**: Bug Bounty and Its Simulation Platform  
**Database**: PostgreSQL 14+  
**Team**: Niway Tadesse, Abraham Asimamaw, Melkamu Tesfa  
**Advisor**: Yosef Worku  
**Date**: March 12, 2026

---

## Overview

This document describes the complete database schema for the Bug Bounty platform. The schema is designed for PostgreSQL and includes 50+ tables covering all platform features.

## Database Files

1. **database-schema-erd.puml** - Core tables (Users, Programs, Reports, Payments)
2. **database-schema-erd-extended.puml** - Extended tables (PTaaS, Simulation, Analytics, etc.)

---

## Table Categories

### 1. User Management (6 tables)
- `users` - Base user accounts
- `researchers` - Security researcher profiles
- `organizations` - Company accounts
- `triage_specialists` - Report reviewers
- `administrators` - Platform admins
- `kyc_verifications` - Identity verification

### 2. Bug Bounty Core (7 tables)
- `bounty_programs` - Bug bounty programs
- `program_scopes` - In-scope/out-of-scope assets
- `reward_tiers` - Severity-based rewards
- `vulnerability_reports` - Submitted vulnerabilities
- `attachments` - Evidence files
- `comments` - Report discussions
- `program_invitations` - Private program invites

### 3. Triage & Validation (2 tables)
- `triage_queue` - Report triage queue
- `validation_results` - Validation outcomes

### 4. Payment System (4 tables)
- `bounty_payments` - Bounty payments
- `researcher_balances` - Wallet balances
- `payout_requests` - Withdrawal requests
- `transactions` - All financial transactions

### 5. PTaaS System (2 tables)
- `ptaas_engagements` - Penetration testing engagements
- `retest_requests` - Retest tracking

### 6. Simulation Environment (2 tables)
- `simulated_environments` - Practice challenges
- `simulation_sessions` - User practice sessions

### 7. Code Review (2 tables)
- `code_review_engagements` - Code review requests
- `code_review_findings` - Identified issues

### 8. Live Hacking Events (2 tables)
- `live_hacking_events` - Time-bound events
- `event_participations` - Participant tracking

### 9. AI Red Teaming (2 tables)
- `ai_red_teaming_engagements` - AI security testing
- `ai_vulnerability_reports` - AI vulnerabilities

### 10. Communication System (4 tables)
- `notifications` - Multi-channel notifications
- `notification_preferences` - User preferences
- `messages` - Direct messaging
- `webhook_endpoints` - Organization webhooks

### 11. Analytics & Metrics (4 tables)
- `researcher_metrics` - Researcher performance
- `organization_metrics` - Organization analytics
- `platform_metrics` - Platform-wide stats
- `analytics_reports` - Custom reports

### 12. Audit & Logging (3 tables)
- `audit_logs` - Comprehensive audit trail
- `security_events` - Security monitoring
- `login_history` - Authentication tracking

### 13. Researcher Matching (5 tables)
- `matching_requests` - Matching requests
- `match_results` - Match scores
- `researcher_profiles` - Researcher capabilities
- `skill_tags` - Skill taxonomy
- `researcher_skills` - Skill proficiency

### 14. SSDLC Integration (2 tables)
- `external_integrations` - Jira/GitHub configs
- `sync_logs` - Sync activity logs

---

## Key Design Decisions

### Primary Keys
- All tables use `UUID` primary keys
- Generated using `gen_random_uuid()` (PostgreSQL extension)
- Benefits: Distributed system compatibility, no ID collision

### Timestamps
- All tables have `created_at TIMESTAMP DEFAULT NOW()`
- Most tables have `updated_at TIMESTAMP DEFAULT NOW()`
- Use triggers for automatic `updated_at` updates

### Soft Deletes
- Most entities use status fields instead of hard deletes
- Common statuses: ACTIVE, INACTIVE, DELETED, ARCHIVED
- Maintains audit trail and referential integrity

### JSON Fields
- PostgreSQL JSONB for flexible data
- Used for: skills, metadata, configurations, filters
- Indexed using GIN indexes for performance

### Encrypted Fields
- Sensitive data marked for encryption
- Password hashing: bcrypt (60 chars)
- API keys/secrets: AES-256 encryption

---

## Indexes Strategy

### Primary Indexes (Automatic)
- Primary key indexes on all `*_id` columns
- Unique indexes on email, username, etc.

### Foreign Key Indexes
```sql
CREATE INDEX idx_reports_program_id ON vulnerability_reports(program_id);
CREATE INDEX idx_reports_researcher_id ON vulnerability_reports(researcher_id);
CREATE INDEX idx_payments_researcher_id ON bounty_payments(researcher_id);
```

### Composite Indexes
```sql
CREATE INDEX idx_reports_status_severity ON vulnerability_reports(status, severity);
CREATE INDEX idx_reports_program_status ON vulnerability_reports(program_id, status);
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);
```

### Timestamp Indexes
```sql
CREATE INDEX idx_reports_created_at ON vulnerability_reports(created_at DESC);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

### JSONB Indexes
```sql
CREATE INDEX idx_researcher_skills ON researcher_profiles USING GIN (skills);
CREATE INDEX idx_program_criteria ON bounty_programs USING GIN (eligibility_criteria);
```

### Full-Text Search Indexes
```sql
CREATE INDEX idx_reports_title_fts ON vulnerability_reports USING GIN (to_tsvector('english', title));
CREATE INDEX idx_reports_description_fts ON vulnerability_reports USING GIN (to_tsvector('english', description));
```

---

## Constraints

### Foreign Key Constraints
```sql
ALTER TABLE researchers 
  ADD CONSTRAINT fk_researchers_user 
  FOREIGN KEY (user_id) REFERENCES users(user_id) 
  ON DELETE CASCADE;

ALTER TABLE vulnerability_reports 
  ADD CONSTRAINT fk_reports_program 
  FOREIGN KEY (program_id) REFERENCES bounty_programs(program_id) 
  ON DELETE CASCADE;
```

### Check Constraints
```sql
ALTER TABLE reward_tiers 
  ADD CONSTRAINT chk_reward_amount 
  CHECK (min_amount >= 0 AND max_amount >= min_amount);

ALTER TABLE vulnerability_reports 
  ADD CONSTRAINT chk_cvss_score 
  CHECK (cvss_score >= 0 AND cvss_score <= 10);

ALTER TABLE researcher_balances 
  ADD CONSTRAINT chk_balance_positive 
  CHECK (available_balance >= 0);
```

### Unique Constraints
```sql
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);
ALTER TABLE skill_tags ADD CONSTRAINT uk_skill_tags_name UNIQUE (name);
ALTER TABLE notification_preferences ADD CONSTRAINT uk_notif_prefs_user UNIQUE (user_id);
```

---

## Triggers

### Updated At Trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
  BEFORE UPDATE ON users 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Audit Log Trigger
```sql
CREATE OR REPLACE FUNCTION log_audit_trail()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id, action, entity_type, entity_id, 
        old_values, new_values, created_at
    ) VALUES (
        current_setting('app.current_user_id')::UUID,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        row_to_json(OLD),
        row_to_json(NEW),
        NOW()
    );
    RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## Data Types Reference

| Type | Usage | Example |
|------|-------|---------|
| UUID | Primary/Foreign keys | `user_id UUID` |
| VARCHAR(n) | Short text with limit | `email VARCHAR(255)` |
| TEXT | Long text, no limit | `description TEXT` |
| INTEGER | Whole numbers | `rank INTEGER` |
| BIGINT | Large numbers | `file_size BIGINT` |
| DECIMAL(p,s) | Precise decimals | `amount DECIMAL(15,2)` |
| BOOLEAN | True/false | `is_active BOOLEAN` |
| TIMESTAMP | Date and time | `created_at TIMESTAMP` |
| DATE | Date only | `date DATE` |
| JSON/JSONB | Structured data | `metadata JSONB` |

---

## Enums (Implemented as VARCHAR with CHECK)

### User Status
```sql
CHECK (status IN ('PENDING', 'ACTIVE', 'SUSPENDED', 'BANNED', 'INACTIVE', 'ARCHIVED'))
```

### Report Status
```sql
CHECK (status IN ('DRAFT', 'SUBMITTED', 'PENDING_TRIAGE', 'IN_REVIEW', 'TRIAGED', 
                  'PENDING_VALIDATION', 'VALIDATED', 'REJECTED', 'DUPLICATE', 
                  'DISPUTED', 'PENDING_PAYMENT', 'PAID', 'CLOSED'))
```

### Severity Levels
```sql
CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL'))
```

### Payment Status
```sql
CHECK (status IN ('PENDING', 'APPROVED', 'PROCESSING', 'COMPLETED', 
                  'FAILED', 'CANCELLED', 'ON_HOLD'))
```

---

## Sample Queries

### Get Researcher Dashboard Stats
```sql
SELECT 
    r.researcher_id,
    u.full_name,
    rm.total_reports,
    rm.validated_reports,
    rm.total_earnings,
    rm.success_rate,
    rm.reputation_score,
    rm.rank
FROM researchers r
JOIN users u ON r.user_id = u.user_id
JOIN researcher_metrics rm ON r.researcher_id = rm.researcher_id
WHERE r.researcher_id = $1;
```

### Get Active Programs with Report Count
```sql
SELECT 
    p.program_id,
    p.name,
    p.status,
    o.company_name,
    COUNT(vr.report_id) as total_reports,
    COUNT(CASE WHEN vr.status = 'VALIDATED' THEN 1 END) as validated_reports
FROM bounty_programs p
JOIN organizations o ON p.organization_id = o.organization_id
LEFT JOIN vulnerability_reports vr ON p.program_id = vr.program_id
WHERE p.status = 'ACTIVE'
GROUP BY p.program_id, p.name, p.status, o.company_name
ORDER BY total_reports DESC;
```

### Get Pending Payments
```sql
SELECT 
    bp.payment_id,
    vr.title as report_title,
    r.researcher_id,
    u.full_name as researcher_name,
    bp.amount,
    bp.created_at
FROM bounty_payments bp
JOIN vulnerability_reports vr ON bp.report_id = vr.report_id
JOIN researchers r ON bp.researcher_id = r.researcher_id
JOIN users u ON r.user_id = u.user_id
WHERE bp.status = 'PENDING'
ORDER BY bp.created_at ASC;
```

---

## Migration Strategy

### Using Alembic (Python)
```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Manual Migration Order
1. Create extensions (`uuid-ossp`, `pgcrypto`)
2. Create base tables (users, organizations, researchers)
3. Create dependent tables (programs, reports)
4. Create relationship tables (comments, attachments)
5. Create indexes
6. Create triggers
7. Insert seed data

---

## Backup & Maintenance

### Daily Backups
```bash
pg_dump -h localhost -U postgres -d bugbounty > backup_$(date +%Y%m%d).sql
```

### Vacuum & Analyze
```sql
VACUUM ANALYZE;  -- Run weekly
REINDEX DATABASE bugbounty;  -- Run monthly
```

### Table Partitioning (Future)
For large tables like `audit_logs`, consider partitioning by date:
```sql
CREATE TABLE audit_logs_2026_03 PARTITION OF audit_logs
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

---

## Security Considerations

1. **Row-Level Security (RLS)**
   - Enable for multi-tenant isolation
   - Researchers see only their reports
   - Organizations see only their programs

2. **Connection Pooling**
   - Use PgBouncer for connection management
   - Max connections: 100-200

3. **SSL/TLS**
   - Enforce SSL connections in production
   - `sslmode=require` in connection string

4. **Least Privilege**
   - Application user: SELECT, INSERT, UPDATE only
   - No DROP, TRUNCATE permissions
   - Admin user for migrations only

---

## Performance Tuning

### PostgreSQL Configuration
```ini
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Query Optimization
- Use EXPLAIN ANALYZE for slow queries
- Add indexes based on query patterns
- Use materialized views for complex aggregations
- Implement query result caching (Redis)

---

## Total Database Size Estimate

| Category | Tables | Est. Size (1 year) |
|----------|--------|-------------------|
| Users | 6 | 100 MB |
| Reports | 7 | 5 GB |
| Payments | 4 | 500 MB |
| Audit Logs | 3 | 10 GB |
| Analytics | 4 | 1 GB |
| Other | 26 | 2 GB |
| **Total** | **50** | **~20 GB** |

*Assumes: 10K users, 100K reports, 1M audit logs*

---

## Next Steps

1. ✅ ERD diagrams created
2. Generate SQL migration scripts (Alembic)
3. Set up PostgreSQL database
4. Create database user and permissions
5. Run migrations
6. Insert seed data
7. Set up backup automation
8. Configure monitoring (pg_stat_statements)

---

**Status**: Database schema design complete! Ready for implementation.

