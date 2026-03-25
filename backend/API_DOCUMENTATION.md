# Bug Bounty Platform - API Documentation

**Version**: 1.0.0  
**Base URL**: `http://localhost:8001/api/v1`  
**Date**: March 25, 2026

---

## 📚 Table of Contents

1. [Authentication](#authentication)
2. [Core Features](#core-features)
3. [Triage & Workflow](#triage--workflow)
4. [Advanced Features](#advanced-features)
5. [Platform Services](#platform-services)
6. [New Services](#new-services)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

All API endpoints (except public ones) require JWT authentication.

### Headers
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user (researcher or organization).

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "researcher",
  "organization_name": "Optional for organizations"
}
```

**Response**: `201 Created`
```json
{
  "message": "User registered successfully",
  "user_id": "uuid",
  "email": "user@example.com"
}
```

#### POST /api/v1/auth/login
Login and receive JWT token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "researcher"
  }
}
```

#### POST /api/v1/auth/verify-email
Verify email address with token.

#### POST /api/v1/auth/forgot-password
Request password reset.

#### POST /api/v1/auth/reset-password
Reset password with token.

#### POST /api/v1/auth/mfa/setup
Setup multi-factor authentication.

#### POST /api/v1/auth/mfa/verify
Verify MFA code.

---

## 🎯 Core Features

### Programs

#### GET /api/v1/programs
List all active bug bounty programs.

**Query Parameters**:
- `status`: Filter by status (active, paused, closed)
- `limit`: Results per page (default: 50)
- `offset`: Pagination offset (default: 0)

**Response**: `200 OK`
```json
{
  "programs": [
    {
      "id": "uuid",
      "name": "Program Name",
      "description": "Program description",
      "status": "active",
      "organization_id": "uuid",
      "created_at": "2026-03-25T10:00:00Z"
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

#### POST /api/v1/programs
Create a new bug bounty program (organization only).

**Request Body**:
```json
{
  "name": "My Bug Bounty Program",
  "description": "Program description",
  "scope": {
    "in_scope": ["*.example.com", "api.example.com"],
    "out_of_scope": ["admin.example.com"]
  },
  "reward_tiers": [
    {
      "severity": "critical",
      "min_amount": 5000,
      "max_amount": 10000
    }
  ]
}
```

#### GET /api/v1/programs/{program_id}
Get program details.

#### PUT /api/v1/programs/{program_id}
Update program (organization only).

#### POST /api/v1/programs/{program_id}/publish
Publish program to make it active.

---

### Reports

#### POST /api/v1/reports
Submit a vulnerability report (researcher only).

**Request Body**:
```json
{
  "program_id": "uuid",
  "title": "SQL Injection in Login Form",
  "description": "Detailed description...",
  "severity": "high",
  "vrt_category": "server_side_injection",
  "vrt_entry": "sql_injection",
  "steps_to_reproduce": "1. Go to login page...",
  "impact": "Attacker can access database...",
  "proof_of_concept": "Payload: ' OR '1'='1..."
}
```

**Response**: `201 Created`
```json
{
  "message": "Report submitted successfully",
  "report_id": "uuid",
  "status": "new"
}
```

#### GET /api/v1/reports
List reports (filtered by role).

**Query Parameters**:
- `status`: Filter by status
- `severity`: Filter by severity
- `program_id`: Filter by program
- `limit`: Results per page
- `offset`: Pagination offset

#### GET /api/v1/reports/{report_id}
Get report details.

#### POST /api/v1/reports/{report_id}/attachments
Upload attachment (screenshot, video, etc.).

#### POST /api/v1/reports/{report_id}/comments
Add comment to report.

---

## 🔍 Triage & Workflow

### Triage

#### GET /api/v1/triage/queue
Get triage queue (triage specialists only).

**Query Parameters**:
- `status_filter`: Filter by status
- `severity_filter`: Filter by severity
- `program_id`: Filter by program
- `limit`: Results per page
- `offset`: Pagination offset

**Response**: `200 OK`
```json
{
  "reports": [
    {
      "id": "uuid",
      "title": "SQL Injection",
      "status": "new",
      "severity": "high",
      "submitted_at": "2026-03-25T10:00:00Z"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

#### POST /api/v1/triage/reports/{report_id}/update
Update report triage information.

**Request Body**:
```json
{
  "status": "triaged",
  "assigned_severity": "high",
  "cvss_score": 7.5,
  "vrt_category": "server_side_injection",
  "triage_notes": "Confirmed SQL injection vulnerability"
}
```

#### POST /api/v1/triage/reports/{report_id}/mark-duplicate
Mark report as duplicate.

**Query Parameters**:
- `original_report_id`: UUID of original report

#### GET /api/v1/triage/reports/{report_id}/similar
Find similar reports for duplicate detection.

#### POST /api/v1/triage/reports/{report_id}/acknowledge
Acknowledge report (24-hour requirement).

#### POST /api/v1/triage/reports/{report_id}/resolve
Mark report as resolved.

#### GET /api/v1/triage/statistics
Get triage statistics.

#### GET /api/v1/triage/reports/{report_id}/history
Get report status history (audit trail).

---

### Bounty

#### POST /api/v1/bounty/approve
Approve bounty payment (organization only).

**Request Body**:
```json
{
  "report_id": "uuid",
  "amount": 5000,
  "currency": "ETB"
}
```

#### POST /api/v1/bounty/reject
Reject bounty with reason.

#### GET /api/v1/bounty/payments
List bounty payments.

#### GET /api/v1/bounty/payments/{payment_id}
Get payment details.

---

## 🚀 Advanced Features

### PTaaS (Penetration Testing as a Service)

#### POST /api/v1/ptaas/engagements
Create PTaaS engagement (organization only).

**Request Body**:
```json
{
  "name": "Q1 2026 Penetration Test",
  "description": "Comprehensive security assessment",
  "testing_methodology": "black_box",
  "scope": {
    "targets": ["app.example.com", "api.example.com"],
    "required_skills": ["web_app", "api_security"]
  },
  "team_size": 3,
  "start_date": "2026-04-01",
  "end_date": "2026-04-15",
  "compliance_requirements": ["PCI-DSS", "ISO 27001"]
}
```

**Response**: `201 Created`
```json
{
  "message": "PTaaS engagement created successfully",
  "engagement_id": 1,
  "status": "pending"
}
```

#### GET /api/v1/ptaas/engagements
List PTaaS engagements.

#### GET /api/v1/ptaas/engagements/{engagement_id}
Get engagement details.

#### POST /api/v1/ptaas/engagements/{engagement_id}/findings
Submit finding (researcher only).

#### GET /api/v1/ptaas/engagements/{engagement_id}/dashboard
Get engagement dashboard (progress, metrics).

#### POST /api/v1/ptaas/engagements/{engagement_id}/deliverables
Upload deliverable (report, documentation).

#### POST /api/v1/ptaas/findings/{finding_id}/retest
Request retest for fixed finding.

---

### BountyMatch (Advanced Matching)

#### POST /api/v1/matching/requests
Create matching request (organization only).

**Request Body**:
```json
{
  "engagement_type": "ptaas",
  "criteria": {
    "required_skills": ["web_app", "api_security"],
    "min_reputation": 80,
    "min_experience_years": 2
  },
  "engagement_id": 1
}
```

#### POST /api/v1/matching/requests/{request_id}/match
Execute matching algorithm.

**Query Parameters**:
- `limit`: Maximum number of matches (default: 10)

**Response**: `200 OK`
```json
{
  "message": "Matching completed successfully",
  "total_matches": 5,
  "matches": [
    {
      "researcher_id": "uuid",
      "match_score": 0.92,
      "skill_score": 0.95,
      "reputation_score": 0.88,
      "rank": 1
    }
  ]
}
```

#### GET /api/v1/matching/requests/{request_id}/results
Get matching results.

#### POST /api/v1/matching/requests/{request_id}/invite
Send invitations to researchers.

**Request Body**:
```json
{
  "researcher_ids": ["uuid1", "uuid2"],
  "message": "We'd like to invite you to our PTaaS engagement",
  "expires_in_days": 7
}
```

#### GET /api/v1/matching/invitations
Get researcher invitations (researcher only).

#### POST /api/v1/matching/invitations/{invitation_id}/respond
Respond to invitation (accept/decline).

**Request Body**:
```json
{
  "accept": true,
  "response_note": "I'm interested in this engagement"
}
```

#### GET /api/v1/matching/recommendations
Get program recommendations (researcher only).

#### POST /api/v1/matching/configuration
Configure matching criteria (organization only).

**Request Body**:
```json
{
  "skill_weight": 0.3,
  "reputation_weight": 0.3,
  "performance_weight": 0.2,
  "expertise_weight": 0.1,
  "availability_weight": 0.1,
  "min_overall_score": 0.7,
  "require_approval": true,
  "auto_approve_threshold": 0.9
}
```

---

### Code Review

#### POST /api/v1/code-review/engagements
Create code review engagement.

#### POST /api/v1/code-review/engagements/{engagement_id}/findings
Submit code review finding.

#### GET /api/v1/code-review/engagements/{engagement_id}/findings
List findings for engagement.

---

### Live Hacking Events

#### POST /api/v1/live-events
Create live hacking event (organization only).

**Request Body**:
```json
{
  "name": "Q1 2026 Live Hacking Event",
  "description": "24-hour live hacking competition",
  "start_time": "2026-04-01T09:00:00Z",
  "end_time": "2026-04-02T09:00:00Z",
  "max_participants": 50,
  "program_id": "uuid"
}
```

#### POST /api/v1/live-events/{event_id}/participate
Register for event (researcher only).

#### POST /api/v1/live-events/{event_id}/invite
Invite researchers to event.

#### GET /api/v1/live-events/{event_id}/metrics
Get event metrics (leaderboard, submissions).

---

### AI Red Teaming

#### POST /api/v1/ai-red-teaming/engagements
Create AI red teaming engagement.

**Request Body**:
```json
{
  "name": "LLM Security Assessment",
  "description": "Security testing of AI model",
  "ai_system_type": "llm",
  "model_details": {
    "model_name": "GPT-4",
    "version": "1.0"
  },
  "testing_scope": ["prompt_injection", "data_leakage", "bias_testing"]
}
```

#### POST /api/v1/ai-red-teaming/engagements/{engagement_id}/environments
Setup testing environment.

#### POST /api/v1/ai-red-teaming/engagements/{engagement_id}/reports
Submit AI vulnerability report.

---

## 🎓 Platform Services

### Simulation (Learning Platform)

#### GET /api/v1/simulation/challenges
List available challenges.

**Query Parameters**:
- `difficulty`: Filter by difficulty (beginner, intermediate, advanced)
- `category`: Filter by category

**Response**: `200 OK`
```json
{
  "challenges": [
    {
      "id": 1,
      "title": "SQL Injection Basics",
      "description": "Learn SQL injection fundamentals",
      "difficulty": "beginner",
      "category": "web",
      "points": 100
    }
  ]
}
```

#### POST /api/v1/simulation/challenges/{challenge_id}/start
Start challenge instance.

#### POST /api/v1/simulation/challenges/{challenge_id}/submit
Submit solution.

**Request Body**:
```json
{
  "solution": "' OR '1'='1",
  "flag": "FLAG{sql_injection_complete}"
}
```

#### GET /api/v1/simulation/progress
Get learning progress.

#### GET /api/v1/simulation/leaderboard
Get leaderboard.

---

### Analytics

#### GET /api/v1/analytics/dashboard
Get analytics dashboard.

**Query Parameters**:
- `start_date`: Start date for metrics
- `end_date`: End date for metrics

**Response**: `200 OK`
```json
{
  "total_reports": 150,
  "valid_reports": 120,
  "total_bounties_paid": 50000,
  "avg_resolution_time": 7.5,
  "top_researchers": [...]
}
```

#### GET /api/v1/analytics/reports
Get report analytics.

#### GET /api/v1/analytics/researchers
Get researcher analytics.

#### GET /api/v1/analytics/programs
Get program analytics.

---

### Integration (SSDLC)

#### POST /api/v1/integration/github
Connect GitHub integration.

**Request Body**:
```json
{
  "access_token": "github_token",
  "repository": "owner/repo"
}
```

#### POST /api/v1/integration/jira
Connect Jira integration.

#### POST /api/v1/integration/webhooks
Configure webhook for external system.

#### GET /api/v1/integration/sync-logs
Get integration sync logs.

---

## 🆕 New Services

### KYC (Know Your Customer)

#### POST /api/v1/kyc/submit
Submit KYC documents (researcher only).

**Request Body** (multipart/form-data):
```
document_type: passport
document_number: AB123456
expiry_date: 2028-12-31
file: [binary file data]
```

**Response**: `201 Created`
```json
{
  "message": "KYC documents submitted successfully",
  "kyc_id": "uuid",
  "status": "pending"
}
```

#### GET /api/v1/kyc/status
Check KYC status (researcher only).

**Response**: `200 OK`
```json
{
  "status": "approved",
  "verified_at": "2026-03-25T10:00:00Z",
  "expires_at": "2028-03-25T10:00:00Z"
}
```

#### GET /api/v1/kyc/admin/pending
Get pending KYC reviews (admin only).

#### POST /api/v1/kyc/admin/review/{kyc_id}
Approve or reject KYC (admin only).

**Request Body**:
```json
{
  "action": "approve",
  "notes": "Documents verified successfully"
}
```

#### GET /api/v1/kyc/admin/history
Get KYC review history (admin only).

---

### Security

#### GET /api/v1/security/events
Get security events (admin only).

**Query Parameters**:
- `event_type`: Filter by event type
- `severity`: Filter by severity
- `user_id`: Filter by user
- `start_date`: Start date
- `end_date`: End date
- `limit`: Results per page
- `offset`: Pagination offset

**Response**: `200 OK`
```json
{
  "events": [
    {
      "id": "uuid",
      "event_type": "brute_force",
      "severity": "high",
      "user_id": "uuid",
      "ip_address": "192.168.1.1",
      "timestamp": "2026-03-25T10:00:00Z",
      "details": {...}
    }
  ]
}
```

#### GET /api/v1/security/login-history
Get login history (user can see own, admin can see all).

#### GET /api/v1/security/audit-trail
Get comprehensive audit trail (admin only).

#### POST /api/v1/security/report-incident
Report security incident.

**Request Body**:
```json
{
  "incident_type": "suspicious_activity",
  "description": "Multiple failed login attempts",
  "severity": "medium"
}
```

#### GET /api/v1/security/statistics
Get security statistics (admin only).

---

### Webhooks

#### POST /api/v1/webhooks/create
Create webhook endpoint (organization only).

**Request Body**:
```json
{
  "url": "https://example.com/webhook",
  "secret": "webhook_secret_key",
  "events": ["report_submitted", "bounty_approved"],
  "is_active": true
}
```

**Response**: `201 Created`
```json
{
  "message": "Webhook created successfully",
  "webhook_id": "uuid",
  "signature_header": "X-Webhook-Signature"
}
```

#### GET /api/v1/webhooks/list
List webhooks (organization only).

#### GET /api/v1/webhooks/{webhook_id}
Get webhook details.

#### PUT /api/v1/webhooks/{webhook_id}
Update webhook.

#### DELETE /api/v1/webhooks/{webhook_id}
Delete webhook.

#### GET /api/v1/webhooks/{webhook_id}/logs
Get webhook delivery logs.

**Response**: `200 OK`
```json
{
  "logs": [
    {
      "id": "uuid",
      "event_type": "report_submitted",
      "status": "success",
      "response_code": 200,
      "delivered_at": "2026-03-25T10:00:00Z",
      "retry_count": 0
    }
  ]
}
```

#### POST /api/v1/webhooks/{webhook_id}/test
Test webhook delivery.

#### GET /api/v1/webhooks/events/supported
Get list of supported webhook events.

---

### Email Templates

#### POST /api/v1/email-templates
Create email template (admin only).

**Request Body**:
```json
{
  "name": "welcome_email",
  "subject": "Welcome to {{platform_name}}",
  "html_body": "<h1>Welcome {{user_name}}</h1>",
  "text_body": "Welcome {{user_name}}",
  "variables": ["platform_name", "user_name"]
}
```

#### GET /api/v1/email-templates
List email templates.

#### GET /api/v1/email-templates/{template_id}
Get template details.

#### PUT /api/v1/email-templates/{template_id}
Update template (admin only).

#### DELETE /api/v1/email-templates/{template_id}
Delete template (admin only).

#### POST /api/v1/email-templates/{template_id}/render
Render template with variables.

**Request Body**:
```json
{
  "variables": {
    "platform_name": "Bug Bounty Platform",
    "user_name": "John Doe"
  }
}
```

#### POST /api/v1/email-templates/{template_id}/test
Send test email (admin only).

---

### Data Exports

#### POST /api/v1/data-exports/request
Request data export.

**Request Body**:
```json
{
  "export_type": "reports",
  "format": "csv",
  "filters": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "status": "resolved"
  }
}
```

**Response**: `202 Accepted`
```json
{
  "message": "Export request created",
  "export_id": "uuid",
  "status": "processing"
}
```

#### GET /api/v1/data-exports
List export requests.

#### GET /api/v1/data-exports/{export_id}
Get export status.

**Response**: `200 OK`
```json
{
  "export_id": "uuid",
  "status": "completed",
  "download_url": "/api/v1/data-exports/uuid/download",
  "expires_at": "2026-04-01T10:00:00Z"
}
```

#### GET /api/v1/data-exports/{export_id}/download
Download export file.

#### DELETE /api/v1/data-exports/{export_id}
Cancel or delete export.

---

### Compliance

#### POST /api/v1/compliance/reports/generate
Generate compliance report (admin only).

**Request Body**:
```json
{
  "report_type": "pci_dss",
  "period_start": "2026-01-01",
  "period_end": "2026-03-31"
}
```

**Response**: `202 Accepted`
```json
{
  "message": "Compliance report generation started",
  "report_id": "uuid",
  "status": "processing"
}
```

#### GET /api/v1/compliance/reports
List compliance reports (admin only).

#### GET /api/v1/compliance/reports/{report_id}
Get compliance report details.

#### GET /api/v1/compliance/reports/{report_id}/download
Download compliance report.

#### POST /api/v1/compliance/exports
Request data export for compliance.

#### GET /api/v1/compliance/exports/{export_id}
Get export status.

---

### Payments

#### POST /api/v1/payments/bounty
Create bounty payment (organization only).

**Request Body**:
```json
{
  "report_id": "uuid",
  "amount": 5000,
  "currency": "ETB"
}
```

#### GET /api/v1/payments/bounty
List bounty payments.

#### GET /api/v1/payments/bounty/{payment_id}
Get payment details.

#### POST /api/v1/payments/bounty/{payment_id}/process
Process payment (admin only).

#### POST /api/v1/payments/payout/request
Request payout (researcher only).

**Request Body**:
```json
{
  "amount": 5000,
  "payment_method": "telebirr",
  "payment_details": {
    "phone_number": "+251912345678"
  }
}
```

#### GET /api/v1/payments/payout/requests
List payout requests.

#### POST /api/v1/payments/payout/{request_id}/approve
Approve payout (admin only).

#### POST /api/v1/payments/payout/{request_id}/reject
Reject payout (admin only).

#### POST /api/v1/payments/payout/{request_id}/process
Process payout (admin only).

#### GET /api/v1/payments/gateways
List payment gateways.

#### POST /api/v1/payments/gateways
Configure payment gateway (admin only).

#### GET /api/v1/payments/transactions
List transactions.

#### GET /api/v1/payments/transactions/{transaction_id}
Get transaction details.

#### GET /api/v1/payments/history
Get payment history.

---

## ⚠️ Error Handling

### Standard Error Response

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🚦 Rate Limiting

Rate limits are applied per user/IP address:

- **Authentication endpoints**: 5 requests per minute
- **Report submission**: 10 requests per hour
- **General API**: 100 requests per minute
- **Admin endpoints**: 200 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1648201200
```

---

## 📊 Pagination

List endpoints support pagination:

**Query Parameters**:
- `limit`: Results per page (default: 50, max: 100)
- `offset`: Number of results to skip (default: 0)

**Response**:
```json
{
  "items": [...],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

## 🔍 Filtering & Sorting

Many list endpoints support filtering and sorting:

**Query Parameters**:
- `status`: Filter by status
- `severity`: Filter by severity
- `start_date`: Filter by start date
- `end_date`: Filter by end date
- `sort_by`: Sort field (e.g., "created_at")
- `sort_order`: Sort order ("asc" or "desc")

---

## 📝 Webhook Signature Verification

Webhooks include HMAC-SHA256 signature for verification:

**Header**:
```http
X-Webhook-Signature: sha256=<signature>
```

**Verification** (Python):
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 🎯 Best Practices

1. **Always use HTTPS** in production
2. **Store JWT tokens securely** (httpOnly cookies recommended)
3. **Implement token refresh** for long-lived sessions
4. **Validate webhook signatures** before processing
5. **Handle rate limits** with exponential backoff
6. **Use pagination** for large datasets
7. **Implement proper error handling**
8. **Log API requests** for debugging
9. **Monitor API performance**
10. **Keep API documentation updated**

---

## 📞 Support

- **API Documentation**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

---

**Last Updated**: March 25, 2026  
**API Version**: 1.0.0  
**Backend Status**: 100% Complete ✅

