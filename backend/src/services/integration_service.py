"""
SSDLC Integration Service
Implements FREQ-42: Bi-directional sync with Jira/GitHub
Enhanced with WebhookEndpoint and WebhookLog integration (FREQ-12, FREQ-15, FREQ-22)
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import asyncio
import hmac
import hashlib
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domain.models.integration import (
    ExternalIntegration,
    SyncLog,
    IntegrationFieldMapping,
    IntegrationWebhookEvent,
    IntegrationTemplate,
    IntegrationType,
    IntegrationStatus,
    SyncAction,
    SyncStatus
)
from src.domain.models.ops import WebhookEndpoint, WebhookLog
from src.domain.models.report import VulnerabilityReport
from src.services.integration_clients.github_client import GitHubClient
from src.services.integration_clients.jira_client import JiraClient
from src.core.message_broker import MessageBrokerService

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy:
    """Conflict resolution strategies for bi-directional sync"""
    
    @staticmethod
    def resolve_by_timestamp(
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve conflict by choosing most recent update
        
        Args:
            local_data: Local system data with updated_at
            remote_data: Remote system data with updated_at
            
        Returns:
            Winning data
        """
        local_time = datetime.fromisoformat(
            local_data.get("updated_at", "1970-01-01T00:00:00")
        )
        remote_time = datetime.fromisoformat(
            remote_data.get("updated_at", "1970-01-01T00:00:00")
        )
        
        if remote_time > local_time:
            logger.info("Conflict resolved: Remote data is newer")
            return remote_data
        else:
            logger.info("Conflict resolved: Local data is newer")
            return local_data
    
    @staticmethod
    def resolve_by_priority(
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any],
        priority: str = "remote"
    ) -> Dict[str, Any]:
        """
        Resolve conflict by priority (local or remote wins)
        
        Args:
            local_data: Local system data
            remote_data: Remote system data
            priority: "local" or "remote"
            
        Returns:
            Winning data
        """
        if priority == "remote":
            logger.info("Conflict resolved: Remote priority")
            return remote_data
        else:
            logger.info("Conflict resolved: Local priority")
            return local_data


class IntegrationService:
    """
    Service for managing SSDLC integrations.
    Enhanced with WebhookEndpoint and WebhookLog management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.message_broker = MessageBrokerService()
    
    # ═══════════════════════════════════════════════════════════════════════
    # WEBHOOK ENDPOINT MANAGEMENT (New - WebhookEndpoint model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def register_webhook_endpoint(
        self,
        organization_id: UUID,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> WebhookEndpoint:
        """
        Register webhook endpoint for organization.
        
        Args:
            organization_id: Organization UUID
            url: Webhook URL
            events: List of event types to subscribe to
            secret: HMAC signing secret (optional)
            
        Returns:
            Created WebhookEndpoint
        """
        # Check if endpoint already exists
        existing = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == organization_id,
            WebhookEndpoint.url == url
        ).first()
        
        if existing:
            # Update existing endpoint
            existing.events = events
            existing.secret = secret
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            
            logger.info(f"Updated webhook endpoint {existing.id} for org {organization_id}")
            return existing
        
        # Create new endpoint
        endpoint = WebhookEndpoint(
            organization_id=organization_id,
            url=url,
            secret=secret,
            events=events,
            is_active=True
        )
        
        self.db.add(endpoint)
        self.db.commit()
        self.db.refresh(endpoint)
        
        logger.info(f"Registered webhook endpoint {endpoint.id} for org {organization_id}")
        return endpoint
    
    def get_webhook_endpoint(self, endpoint_id: UUID) -> Optional[WebhookEndpoint]:
        """Get webhook endpoint by ID"""
        return self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == endpoint_id
        ).first()
    
    def list_webhook_endpoints(
        self,
        organization_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[WebhookEndpoint]:
        """
        List webhook endpoints for organization.
        
        Args:
            organization_id: Organization UUID
            is_active: Filter by active status (optional)
            
        Returns:
            List of WebhookEndpoint
        """
        query = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == organization_id
        )
        
        if is_active is not None:
            query = query.filter(WebhookEndpoint.is_active == is_active)
        
        return query.all()
    
    def update_webhook_endpoint(
        self,
        endpoint_id: UUID,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        secret: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> WebhookEndpoint:
        """
        Update webhook endpoint.
        
        Args:
            endpoint_id: Endpoint UUID
            url: New URL (optional)
            events: New event list (optional)
            secret: New secret (optional)
            is_active: New active status (optional)
            
        Returns:
            Updated WebhookEndpoint
        """
        endpoint = self.get_webhook_endpoint(endpoint_id)
        if not endpoint:
            raise ValueError(f"Webhook endpoint {endpoint_id} not found")
        
        if url is not None:
            endpoint.url = url
        if events is not None:
            endpoint.events = events
        if secret is not None:
            endpoint.secret = secret
        if is_active is not None:
            endpoint.is_active = is_active
        
        endpoint.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(endpoint)
        
        logger.info(f"Updated webhook endpoint {endpoint_id}")
        return endpoint
    
    def delete_webhook_endpoint(self, endpoint_id: UUID) -> bool:
        """
        Delete webhook endpoint.
        
        Args:
            endpoint_id: Endpoint UUID
            
        Returns:
            True if deleted
        """
        endpoint = self.get_webhook_endpoint(endpoint_id)
        if not endpoint:
            return False
        
        self.db.delete(endpoint)
        self.db.commit()
        
        logger.info(f"Deleted webhook endpoint {endpoint_id}")
        return True
    
    # ═══════════════════════════════════════════════════════════════════════
    # WEBHOOK DELIVERY (New - WebhookLog model)
    # ═══════════════════════════════════════════════════════════════════════
    
    def trigger_webhook(
        self,
        organization_id: UUID,
        event: str,
        payload: Dict[str, Any]
    ) -> List[WebhookLog]:
        """
        Trigger webhook for event.
        
        Args:
            organization_id: Organization UUID
            event: Event type (e.g., "report.submitted")
            payload: Event payload
            
        Returns:
            List of WebhookLog for delivery attempts
        """
        # Get active endpoints subscribed to this event
        endpoints = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == organization_id,
            WebhookEndpoint.is_active == True
        ).all()
        
        # Filter endpoints subscribed to this event
        subscribed_endpoints = [
            ep for ep in endpoints
            if event in ep.events or "*" in ep.events
        ]
        
        if not subscribed_endpoints:
            logger.info(f"No endpoints subscribed to event {event} for org {organization_id}")
            return []
        
        # Deliver to each endpoint
        logs = []
        for endpoint in subscribed_endpoints:
            log = self._deliver_webhook(endpoint, event, payload)
            logs.append(log)
        
        logger.info(f"Triggered webhook {event} for {len(logs)} endpoints")
        return logs
    
    def _deliver_webhook(
        self,
        endpoint: WebhookEndpoint,
        event: str,
        payload: Dict[str, Any],
        retry_count: int = 0
    ) -> WebhookLog:
        """
        Deliver webhook to endpoint.
        
        Args:
            endpoint: WebhookEndpoint
            event: Event type
            payload: Event payload
            retry_count: Retry attempt number
            
        Returns:
            WebhookLog
        """
        import requests
        import json
        
        # Generate HMAC signature if secret is configured
        signature = None
        if endpoint.secret:
            signature = self._generate_webhook_signature(
                payload=json.dumps(payload).encode(),
                secret=endpoint.secret
            )
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event,
            "X-Webhook-Delivery": str(UUID(bytes=uuid.uuid4().bytes))
        }
        
        if signature:
            headers["X-Webhook-Signature"] = signature
        
        # Attempt delivery
        log = WebhookLog(
            endpoint_id=endpoint.id,
            event=event,
            payload=payload,
            retry_count=retry_count
        )
        
        try:
            response = requests.post(
                endpoint.url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            log.response_status = response.status_code
            log.response_body = response.text[:1000]  # Limit to 1000 chars
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook delivered successfully to {endpoint.url}")
            else:
                log.error_message = f"HTTP {response.status_code}"
                logger.warning(f"Webhook delivery failed: HTTP {response.status_code}")
        
        except Exception as e:
            log.error_message = str(e)[:500]  # Limit to 500 chars
            logger.error(f"Webhook delivery error: {str(e)}")
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def _generate_webhook_signature(self, payload: bytes, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook.
        
        Args:
            payload: Payload bytes
            secret: Secret key
            
        Returns:
            Hex signature
        """
        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook signature.
        
        Args:
            payload: Payload bytes
            signature: Received signature
            secret: Secret key
            
        Returns:
            True if signature is valid
        """
        expected_signature = self._generate_webhook_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def get_webhook_logs(
        self,
        endpoint_id: UUID,
        limit: int = 100
    ) -> List[WebhookLog]:
        """
        Get webhook delivery logs for endpoint.
        
        Args:
            endpoint_id: Endpoint UUID
            limit: Maximum number of logs
            
        Returns:
            List of WebhookLog
        """
        return self.db.query(WebhookLog).filter(
            WebhookLog.endpoint_id == endpoint_id
        ).order_by(
            WebhookLog.created_at.desc()
        ).limit(limit).all()
    
    def retry_failed_webhook(self, log_id: UUID) -> WebhookLog:
        """
        Retry failed webhook delivery.
        
        Args:
            log_id: WebhookLog UUID
            
        Returns:
            New WebhookLog for retry attempt
        """
        log = self.db.query(WebhookLog).filter(
            WebhookLog.id == log_id
        ).first()
        
        if not log:
            raise ValueError(f"Webhook log {log_id} not found")
        
        endpoint = self.get_webhook_endpoint(log.endpoint_id)
        if not endpoint:
            raise ValueError(f"Webhook endpoint {log.endpoint_id} not found")
        
        # Retry delivery
        new_log = self._deliver_webhook(
            endpoint=endpoint,
            event=log.event,
            payload=log.payload,
            retry_count=log.retry_count + 1
        )
        
        logger.info(f"Retried webhook delivery (attempt {new_log.retry_count})")
        return new_log
    
    # ═══════════════════════════════════════════════════════════════════════
    # INTEGRATION MANAGEMENT (Existing methods)
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_integration(
        self,
        organization_id: UUID,
        integration_type: IntegrationType,
        config: Dict[str, Any]
    ) -> ExternalIntegration:
        """
        Create new external integration
        
        Args:
            organization_id: Organization UUID
            integration_type: Integration type (jira, github)
            config: Integration configuration
            
        Returns:
            Created integration
        """
        integration = ExternalIntegration(
            organization_id=organization_id,
            type=integration_type,
            status=IntegrationStatus.PENDING,
            config=config
        )
        
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        
        logger.info(f"Created integration {integration.id} for org {organization_id}")
        return integration
    
    def get_integration(self, integration_id: UUID) -> Optional[ExternalIntegration]:
        """Get integration by ID"""
        return self.db.query(ExternalIntegration).filter(
            ExternalIntegration.id == integration_id
        ).first()
    
    def list_integrations(
        self,
        organization_id: UUID,
        integration_type: Optional[IntegrationType] = None
    ) -> List[ExternalIntegration]:
        """List integrations for organization"""
        query = self.db.query(ExternalIntegration).filter(
            ExternalIntegration.organization_id == organization_id
        )
        
        if integration_type:
            query = query.filter(ExternalIntegration.type == integration_type)
        
        return query.all()
    
    def update_integration_status(
        self,
        integration_id: UUID,
        status: IntegrationStatus
    ) -> ExternalIntegration:
        """Update integration status"""
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        integration.status = status
        self.db.commit()
        self.db.refresh(integration)
        
        return integration
    
    def sync_report_to_external(
        self,
        integration_id: str,
        report_id: str,
        action: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync vulnerability report to external system
        
        Args:
            integration_id: Integration UUID
            report_id: Report UUID
            action: Sync action (create, update, delete)
            payload: Report data
            
        Returns:
            Sync result with external ID
        """
        integration = self.get_integration(UUID(integration_id))
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Get client for integration type
        client = self._get_client(integration)
        
        # Apply field mappings
        mapped_payload = self._apply_field_mappings(integration.id, payload)
        
        # Sync to external system
        try:
            if action == "create":
                result = asyncio.run(client.create_issue(mapped_payload))
            elif action == "update":
                external_id = payload.get("external_id")
                if not external_id:
                    raise ValueError("external_id required for update")
                result = asyncio.run(client.update_issue(external_id, mapped_payload))
            elif action == "delete":
                external_id = payload.get("external_id")
                if not external_id:
                    raise ValueError("external_id required for delete")
                result = asyncio.run(client.close_issue(external_id))
            else:
                raise ValueError(f"Unknown action: {action}")
            
            # Log success
            self._log_sync(
                integration_id=UUID(integration_id),
                report_id=UUID(report_id) if report_id else None,
                action=SyncAction(action),
                status=SyncStatus.SUCCESS
            )
            
            # Update last sync time
            integration.last_sync_at = datetime.utcnow()
            self.db.commit()
            
            return result
            
        except Exception as e:
            # Log failure
            self._log_sync(
                integration_id=UUID(integration_id),
                report_id=UUID(report_id) if report_id else None,
                action=SyncAction(action),
                status=SyncStatus.FAILED,
                error=str(e)
            )
            raise
    
    def queue_sync(
        self,
        integration_id: UUID,
        report_id: UUID,
        action: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Queue async sync task
        
        Args:
            integration_id: Integration UUID
            report_id: Report UUID
            action: Sync action
            payload: Report data
            
        Returns:
            Task ID
        """
        task_id = self.message_broker.queue_sync_task(
            integration_id=str(integration_id),
            report_id=str(report_id),
            action=action,
            payload=payload
        )
        
        logger.info(f"Queued sync task {task_id} for report {report_id}")
        return task_id
    
    def process_webhook(
        self,
        integration_id: str,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process incoming webhook from external system
        
        Args:
            integration_id: Integration UUID
            event_id: Webhook event UUID
            event_type: Event type
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        integration = self.get_integration(UUID(integration_id))
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Get webhook event
        event = self.db.query(IntegrationWebhookEvent).filter(
            IntegrationWebhookEvent.id == UUID(event_id)
        ).first()
        
        if not event:
            raise ValueError(f"Webhook event {event_id} not found")
        
        # Process based on event type
        result = {}
        
        if integration.type == IntegrationType.GITHUB:
            result = self._process_github_webhook(integration, event_type, payload)
        elif integration.type == IntegrationType.JIRA:
            result = self._process_jira_webhook(integration, event_type, payload)
        
        # Mark event as processed
        event.processed = True
        event.processed_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Processed webhook event {event_id}")
        return result
    
    def receive_webhook(
        self,
        integration_id: UUID,
        event_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        signature: Optional[str] = None
    ) -> IntegrationWebhookEvent:
        """
        Receive and store webhook event
        
        Args:
            integration_id: Integration UUID
            event_type: Event type
            payload: Webhook payload
            headers: Request headers
            signature: Webhook signature
            
        Returns:
            Created webhook event
        """
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Verify signature
        is_verified = False
        if signature:
            client = self._get_client(integration)
            secret = integration.config.get("webhook_secret", "")
            is_verified = client.verify_webhook_signature(
                payload=str(payload).encode(),
                signature=signature,
                secret=secret
            )
        
        # Store webhook event
        event = IntegrationWebhookEvent(
            integration_id=integration_id,
            event_type=event_type,
            payload=payload,
            headers=headers,
            signature=signature,
            is_verified=is_verified,
            processed=False
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Queue processing task
        if is_verified:
            self.message_broker.queue_webhook_task(
                integration_id=str(integration_id),
                event_id=str(event.id),
                event_type=event_type,
                payload=payload
            )
        
        logger.info(f"Received webhook event {event.id}")
        return event
    
    def resolve_conflict(
        self,
        integration_id: UUID,
        report_id: UUID,
        strategy: str = "timestamp"
    ) -> Dict[str, Any]:
        """
        Resolve sync conflict
        
        Args:
            integration_id: Integration UUID
            report_id: Report UUID
            strategy: Resolution strategy (timestamp, local, remote)
            
        Returns:
            Resolution result
        """
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Get local report
        report = self.db.query(VulnerabilityReport).filter(
            VulnerabilityReport.id == report_id
        ).first()
        
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Get remote data
        client = self._get_client(integration)
        external_id = report.external_id  # Assuming this field exists
        
        if not external_id:
            raise ValueError("Report not synced to external system")
        
        remote_data = asyncio.run(client.get_issue(external_id))
        
        local_data = {
            "title": report.title,
            "description": report.description,
            "severity": report.severity,
            "updated_at": report.updated_at.isoformat()
        }
        
        # Resolve conflict
        if strategy == "timestamp":
            winning_data = ConflictResolutionStrategy.resolve_by_timestamp(
                local_data, remote_data
            )
        elif strategy == "local":
            winning_data = ConflictResolutionStrategy.resolve_by_priority(
                local_data, remote_data, priority="local"
            )
        elif strategy == "remote":
            winning_data = ConflictResolutionStrategy.resolve_by_priority(
                local_data, remote_data, priority="remote"
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Apply winning data
        if winning_data == local_data:
            # Sync local to remote
            self.queue_sync(integration_id, report_id, "update", local_data)
        else:
            # Update local from remote
            report.title = winning_data.get("title", report.title)
            report.description = winning_data.get("description", report.description)
            self.db.commit()
        
        logger.info(f"Resolved conflict for report {report_id}")
        return {"strategy": strategy, "winner": "local" if winning_data == local_data else "remote"}
    
    def log_sync_failure(
        self,
        integration_id: str,
        report_id: str,
        action: str,
        error: str,
        retry_count: int
    ):
        """Log sync failure"""
        self._log_sync(
            integration_id=UUID(integration_id),
            report_id=UUID(report_id) if report_id else None,
            action=SyncAction(action),
            status=SyncStatus.FAILED,
            error=f"Retry {retry_count}: {error}"
        )
    
    def _get_client(self, integration: ExternalIntegration):
        """Get API client for integration type"""
        if integration.type == IntegrationType.GITHUB:
            return GitHubClient(integration.config)
        elif integration.type == IntegrationType.JIRA:
            return JiraClient(integration.config)
        else:
            raise ValueError(f"Unsupported integration type: {integration.type}")
    
    def _apply_field_mappings(
        self,
        integration_id: UUID,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply field mappings to payload"""
        mappings = self.db.query(IntegrationFieldMapping).filter(
            IntegrationFieldMapping.integration_id == integration_id
        ).all()
        
        mapped_payload = {}
        
        for mapping in mappings:
            source_value = payload.get(mapping.source_field)
            
            if source_value is not None:
                mapped_payload[mapping.target_field] = source_value
            elif mapping.default_value:
                mapped_payload[mapping.target_field] = mapping.default_value
        
        # Include unmapped fields
        for key, value in payload.items():
            if key not in mapped_payload:
                mapped_payload[key] = value
        
        return mapped_payload
    
    def _log_sync(
        self,
        integration_id: UUID,
        report_id: Optional[UUID],
        action: SyncAction,
        status: SyncStatus,
        error: Optional[str] = None
    ):
        """Log sync operation"""
        log = SyncLog(
            integration_id=integration_id,
            report_id=report_id,
            action=action,
            status=status,
            error_message=error
        )
        
        self.db.add(log)
        self.db.commit()
    
    def _process_github_webhook(
        self,
        integration: ExternalIntegration,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process GitHub webhook event"""
        if event_type == "issues":
            action = payload.get("action")
            issue = payload.get("issue", {})
            
            # Map to local report and update
            # Implementation depends on your report model
            logger.info(f"Processing GitHub issue {action}: {issue.get('number')}")
            
            return {"processed": True, "action": action}
        
        return {"processed": False}
    
    def _process_jira_webhook(
        self,
        integration: ExternalIntegration,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Jira webhook event"""
        if event_type == "jira:issue_updated":
            issue = payload.get("issue", {})
            
            # Map to local report and update
            logger.info(f"Processing Jira issue update: {issue.get('key')}")
            
            return {"processed": True, "event": event_type}
        
        return {"processed": False}
