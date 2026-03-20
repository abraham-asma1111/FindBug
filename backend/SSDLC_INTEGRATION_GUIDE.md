# SSDLC Integration Guide (FREQ-42)

## Overview

The SSDLC Integration feature enables bi-directional synchronization between the Bug Bounty Platform and external development tools (Jira and GitHub). This allows vulnerability reports to be automatically synced as issues in your development workflow.

## Features

- ✅ **Bi-directional Sync**: Platform ↔ Jira/GitHub
- ✅ **Asynchronous Processing**: RabbitMQ message broker with Dead Letter Queue
- ✅ **Exponential Backoff**: Automatic retry with 1s, 2s, 4s, 8s, 16s delays
- ✅ **Real-time Webhooks**: Instant updates from external systems
- ✅ **Conflict Resolution**: Timestamp, local, or remote priority strategies
- ✅ **Field Mapping**: Custom field transformations
- ✅ **Webhook Verification**: HMAC signature validation

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start RabbitMQ

Using Docker:
```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

Access RabbitMQ Management UI: http://localhost:15672 (guest/guest)

### 3. Configure Environment

Add to `.env`:
```bash
# RabbitMQ
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# GitHub (optional)
GITHUB_TOKEN=ghp_your_token
GITHUB_WEBHOOK_SECRET=your_secret

# Jira (optional)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=admin@example.com
JIRA_API_TOKEN=your_token
JIRA_WEBHOOK_SECRET=your_secret
```

### 4. Run Database Migration

```bash
alembic upgrade head
```

### 5. Start Celery Worker

```bash
celery -A backend.src.core.message_broker worker \
  --loglevel=info \
  --queues=integration.sync,integration.webhook,dlq
```

### 6. Start API Server

```bash
python run_dev.py
```

## Usage

### Create GitHub Integration

```bash
curl -X POST http://localhost:8001/api/v1/integrations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "github",
    "config": {
      "token": "ghp_xxxxxxxxxxxxx",
      "owner": "your-org",
      "repo": "your-repo",
      "webhook_secret": "your-secret"
    }
  }'
```

### Create Jira Integration

```bash
curl -X POST http://localhost:8001/api/v1/integrations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "jira",
    "config": {
      "url": "https://your-domain.atlassian.net",
      "email": "admin@example.com",
      "api_token": "your-token",
      "project_key": "PROJ",
      "webhook_secret": "your-secret"
    }
  }'
```

### Sync Vulnerability Report

```bash
curl -X POST http://localhost:8001/api/v1/integrations/{integration_id}/sync \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "report-uuid",
    "action": "create",
    "payload": {
      "title": "XSS Vulnerability in Login Form",
      "description": "Detailed description...",
      "severity": "high",
      "labels": ["security", "xss"]
    }
  }'
```

### Configure Webhook (GitHub)

1. Go to your GitHub repository settings
2. Navigate to Webhooks → Add webhook
3. Set Payload URL: `https://your-domain.com/api/v1/integrations/{integration_id}/webhook`
4. Set Content type: `application/json`
5. Set Secret: Your webhook secret
6. Select events: Issues, Issue comments
7. Save webhook

### Configure Webhook (Jira)

1. Go to Jira Settings → System → WebHooks
2. Create webhook
3. Set URL: `https://your-domain.com/api/v1/integrations/{integration_id}/webhook`
4. Set Events: Issue created, Issue updated, Issue deleted
5. Save webhook

### Resolve Conflicts

```bash
curl -X POST http://localhost:8001/api/v1/integrations/{integration_id}/resolve-conflict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "report-uuid",
    "strategy": "timestamp"
  }'
```

Strategies:
- `timestamp` - Choose most recent update
- `local` - Local data wins
- `remote` - Remote data wins

## API Endpoints

### Integration Management
- `POST /api/v1/integrations` - Create integration
- `GET /api/v1/integrations` - List integrations
- `GET /api/v1/integrations/{id}` - Get integration
- `PATCH /api/v1/integrations/{id}` - Update integration

### Synchronization
- `POST /api/v1/integrations/{id}/sync` - Queue sync task
- `GET /api/v1/integrations/{id}/sync-logs` - Get sync logs
- `GET /api/v1/integrations/tasks/{task_id}/status` - Get task status

### Webhooks
- `POST /api/v1/integrations/{id}/webhook` - Receive webhook

### Conflict Resolution
- `POST /api/v1/integrations/{id}/resolve-conflict` - Resolve conflict

### Field Mappings
- `POST /api/v1/integrations/{id}/field-mappings` - Create mapping
- `GET /api/v1/integrations/{id}/field-mappings` - List mappings

## Architecture

### Sync Flow (Platform → External)

```
User Action → API Request → Queue Task → RabbitMQ
                                            ↓
                                      Celery Worker
                                            ↓
                                    GitHub/Jira API
                                            ↓
                                    Success/Retry/DLQ
```

### Webhook Flow (External → Platform)

```
GitHub/Jira → Webhook → Verify Signature → Store Event
                                                ↓
                                          Queue Task
                                                ↓
                                          Celery Worker
                                                ↓
                                      Update Local Report
```

## Monitoring

### Check RabbitMQ Queues

Access management UI: http://localhost:15672

Queues:
- `integration.sync` - Sync tasks
- `integration.webhook` - Webhook tasks
- `dlq` - Failed tasks (Dead Letter Queue)

### Check Task Status

```bash
curl http://localhost:8001/api/v1/integrations/tasks/{task_id}/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Sync Logs

```bash
curl http://localhost:8001/api/v1/integrations/{integration_id}/sync-logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Task Stuck in Queue

1. Check Celery worker is running
2. Check RabbitMQ connection
3. Check worker logs for errors

### Webhook Not Processing

1. Verify webhook signature is correct
2. Check webhook event is stored in database
3. Check Celery worker logs
4. Verify integration is active

### Sync Failing

1. Check external API credentials
2. Check network connectivity
3. Check sync logs for error messages
4. Check Dead Letter Queue for failed tasks

### Inspect Dead Letter Queue

```bash
# Using RabbitMQ Management UI
# Navigate to Queues → dlq → Get messages
```

## Best Practices

1. **Use Webhooks**: Enable webhooks for real-time updates
2. **Monitor DLQ**: Regularly check Dead Letter Queue for failed tasks
3. **Set Conflict Strategy**: Choose appropriate conflict resolution strategy
4. **Field Mappings**: Configure field mappings for custom fields
5. **Rate Limiting**: Be aware of external API rate limits
6. **Secure Secrets**: Store webhook secrets securely
7. **Test Integration**: Test with non-production data first

## Security

1. **Webhook Signatures**: Always verified before processing
2. **API Tokens**: Stored encrypted in database
3. **Access Control**: Organization-level isolation
4. **HTTPS Only**: Use HTTPS for webhook endpoints in production
5. **Secret Rotation**: Rotate webhook secrets periodically

## Performance

1. **Async Processing**: All sync operations are async
2. **Worker Scaling**: Deploy multiple Celery workers
3. **Connection Pooling**: HTTP clients use connection pooling
4. **Timeout Handling**: 30s timeout for external API calls
5. **Batch Operations**: Consider batching for large syncs

## Support

For issues or questions:
1. Check implementation status: `FREQ-42-SSDLC-INTEGRATION-IMPLEMENTATION-STATUS.md`
2. Review API documentation: http://localhost:8001/docs
3. Check Celery worker logs
4. Check RabbitMQ management UI

## Related Documentation

- [FREQ-42 Implementation Status](FREQ-42-SSDLC-INTEGRATION-IMPLEMENTATION-STATUS.md)
- [API Documentation](http://localhost:8001/docs)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [Jira API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
