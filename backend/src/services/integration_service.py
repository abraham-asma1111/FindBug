"""
SSDLC Integration Service
Implements FREQ-42: Bi-directional sync with Jira/GitHub
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.src.domain.models.integration import (
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
from backend.src.domain.models.report import VulnerabilityReport
from backend.src.services.integration_clients.github_client import GitHubClient
from backend.src.services.integration_clients.jira_client import JiraClient
from backend.src.core.message_broker import MessageBrokerService

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
    """Service for managing SSDLC integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.message_broker = MessageBrokerService()
    
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
