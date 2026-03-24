"""
Webhook Service — Webhook endpoint management and event delivery (FREQ-42)
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
import hmac
import hashlib
import json
import requests
from time import sleep

from src.domain.models.ops import WebhookEndpoint, WebhookLog
from src.domain.models.organization import Organization
from src.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from src.core.logging import get_logger

logger = get_logger(__name__)


class WebhookService:
    """Service for webhook endpoint management and event delivery"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Supported webhook events
        self.supported_events = [
            # Report events
            "report.submitted",
            "report.triaged",
            "report.validated",
            "report.duplicate",
            "report.closed",
            # Bounty events
            "bounty.approved",
            "bounty.paid",
            "bounty.rejected",
            # Program events
            "program.published",
            "program.paused",
            "program.closed",
            # PTaaS events
            "ptaas.engagement_created",
            "ptaas.finding_submitted",
            "ptaas.deliverable_ready",
            # Code Review events
            "code_review.started",
            "code_review.finding_submitted",
            "code_review.completed",
            # Live Event events
            "live_event.started",
            "live_event.ended",
            "live_event.report_submitted",
            # AI Red Teaming events
            "ai_redteam.engagement_created",
            "ai_redteam.vulnerability_found",
            "ai_redteam.report_ready"
        ]
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delays = [5, 30, 300]  # 5s, 30s, 5min
        self.timeout = 10  # seconds
    
    def create_webhook(
        self,
        organization_id: str,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict:
        """
        Create a new webhook endpoint.
        
        Args:
            organization_id: Organization ID
            url: Webhook URL
            events: List of events to subscribe to
            secret: HMAC signing secret (optional, auto-generated if not provided)
            
        Returns:
            Webhook endpoint details
        """
        # Validate organization exists
        org = self.db.query(Organization).filter(
            Organization.id == UUID(organization_id)
        ).first()
        
        if not org:
            raise NotFoundException("Organization not found.")
        
        # Validate URL
        if not url.startswith(("http://", "https://")):
            raise ValueError("Webhook URL must start with http:// or https://")
        
        # Validate events
        invalid_events = [e for e in events if e not in self.supported_events]
        if invalid_events:
            raise ValueError(f"Invalid events: {', '.join(invalid_events)}")
        
        # Check for duplicate URL
        existing = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == UUID(organization_id),
            WebhookEndpoint.url == url
        ).first()
        
        if existing:
            raise ConflictException("Webhook URL already registered for this organization.")
        
        # Generate secret if not provided
        if not secret:
            import secrets
            secret = secrets.token_urlsafe(32)
        
        # Create webhook endpoint
        webhook = WebhookEndpoint(
            organization_id=UUID(organization_id),
            url=url,
            secret=secret,
            events=events,
            is_active=True
        )
        
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        
        logger.info("Webhook created", extra={
            "webhook_id": str(webhook.id),
            "organization_id": organization_id,
            "url": url
        })
        
        return {
            "webhook_id": str(webhook.id),
            "organization_id": str(webhook.organization_id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "created_at": webhook.created_at.isoformat(),
            "message": "Webhook endpoint created successfully."
        }
    
    def list_webhooks(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """
        List webhook endpoints for an organization.
        
        Args:
            organization_id: Organization ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of webhook endpoints
        """
        query = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == UUID(organization_id)
        ).order_by(WebhookEndpoint.created_at.desc())
        
        total = query.count()
        webhooks = query.offset(skip).limit(limit).all()
        
        return {
            "webhooks": [
                {
                    "webhook_id": str(w.id),
                    "url": w.url,
                    "events": w.events,
                    "is_active": w.is_active,
                    "created_at": w.created_at.isoformat(),
                    "updated_at": w.updated_at.isoformat() if w.updated_at else None
                }
                for w in webhooks
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_webhook(self, webhook_id: str, organization_id: str) -> Dict:
        """
        Get webhook endpoint details.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID (for authorization)
            
        Returns:
            Webhook endpoint details
        """
        webhook = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == UUID(webhook_id)
        ).first()
        
        if not webhook:
            raise NotFoundException("Webhook not found.")
        
        # Verify ownership
        if str(webhook.organization_id) != organization_id:
            raise ForbiddenException("You don't have access to this webhook.")
        
        return {
            "webhook_id": str(webhook.id),
            "organization_id": str(webhook.organization_id),
            "url": webhook.url,
            "secret": webhook.secret,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "created_at": webhook.created_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat() if webhook.updated_at else None
        }
    
    def update_webhook(
        self,
        webhook_id: str,
        organization_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Dict:
        """
        Update webhook endpoint.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID (for authorization)
            url: New webhook URL (optional)
            events: New event list (optional)
            is_active: Active status (optional)
            
        Returns:
            Updated webhook endpoint details
        """
        webhook = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == UUID(webhook_id)
        ).first()
        
        if not webhook:
            raise NotFoundException("Webhook not found.")
        
        # Verify ownership
        if str(webhook.organization_id) != organization_id:
            raise ForbiddenException("You don't have access to this webhook.")
        
        # Update fields
        if url is not None:
            if not url.startswith(("http://", "https://")):
                raise ValueError("Webhook URL must start with http:// or https://")
            webhook.url = url
        
        if events is not None:
            invalid_events = [e for e in events if e not in self.supported_events]
            if invalid_events:
                raise ValueError(f"Invalid events: {', '.join(invalid_events)}")
            webhook.events = events
        
        if is_active is not None:
            webhook.is_active = is_active
        
        self.db.commit()
        self.db.refresh(webhook)
        
        logger.info("Webhook updated", extra={
            "webhook_id": webhook_id,
            "organization_id": organization_id
        })
        
        return {
            "webhook_id": str(webhook.id),
            "url": webhook.url,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "updated_at": webhook.updated_at.isoformat() if webhook.updated_at else None,
            "message": "Webhook updated successfully."
        }
    
    def delete_webhook(self, webhook_id: str, organization_id: str) -> Dict:
        """
        Delete webhook endpoint.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID (for authorization)
            
        Returns:
            Deletion confirmation
        """
        webhook = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == UUID(webhook_id)
        ).first()
        
        if not webhook:
            raise NotFoundException("Webhook not found.")
        
        # Verify ownership
        if str(webhook.organization_id) != organization_id:
            raise ForbiddenException("You don't have access to this webhook.")
        
        self.db.delete(webhook)
        self.db.commit()
        
        logger.info("Webhook deleted", extra={
            "webhook_id": webhook_id,
            "organization_id": organization_id
        })
        
        return {
            "webhook_id": webhook_id,
            "message": "Webhook deleted successfully."
        }
    
    def get_webhook_logs(
        self,
        webhook_id: str,
        organization_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """
        Get webhook delivery logs.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID (for authorization)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of webhook logs
        """
        webhook = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == UUID(webhook_id)
        ).first()
        
        if not webhook:
            raise NotFoundException("Webhook not found.")
        
        # Verify ownership
        if str(webhook.organization_id) != organization_id:
            raise ForbiddenException("You don't have access to this webhook.")
        
        query = self.db.query(WebhookLog).filter(
            WebhookLog.endpoint_id == UUID(webhook_id)
        ).order_by(WebhookLog.created_at.desc())
        
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        
        return {
            "logs": [
                {
                    "log_id": str(log.id),
                    "event": log.event,
                    "response_status": log.response_status,
                    "error_message": log.error_message,
                    "retry_count": log.retry_count,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def test_webhook(self, webhook_id: str, organization_id: str) -> Dict:
        """
        Test webhook endpoint with a ping event.
        
        Args:
            webhook_id: Webhook ID
            organization_id: Organization ID (for authorization)
            
        Returns:
            Test result
        """
        webhook = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.id == UUID(webhook_id)
        ).first()
        
        if not webhook:
            raise NotFoundException("Webhook not found.")
        
        # Verify ownership
        if str(webhook.organization_id) != organization_id:
            raise ForbiddenException("You don't have access to this webhook.")
        
        # Send test event
        test_payload = {
            "event": "webhook.test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "This is a test webhook event"
            }
        }
        
        result = self._deliver_webhook(webhook, "webhook.test", test_payload)
        
        return {
            "webhook_id": webhook_id,
            "success": result["success"],
            "status_code": result.get("status_code"),
            "error": result.get("error"),
            "message": "Webhook test completed."
        }
    
    def trigger_webhook(
        self,
        organization_id: str,
        event: str,
        payload: Dict
    ) -> Dict:
        """
        Trigger webhook event for an organization.
        
        Args:
            organization_id: Organization ID
            event: Event name
            payload: Event payload
            
        Returns:
            Delivery results
        """
        # Get active webhooks subscribed to this event
        webhooks = self.db.query(WebhookEndpoint).filter(
            WebhookEndpoint.organization_id == UUID(organization_id),
            WebhookEndpoint.is_active == True
        ).all()
        
        # Filter webhooks subscribed to this event
        subscribed_webhooks = [w for w in webhooks if event in w.events]
        
        if not subscribed_webhooks:
            logger.info("No webhooks subscribed to event", extra={
                "organization_id": organization_id,
                "event": event
            })
            return {
                "event": event,
                "webhooks_triggered": 0,
                "message": "No webhooks subscribed to this event."
            }
        
        # Deliver to all subscribed webhooks
        results = []
        for webhook in subscribed_webhooks:
            result = self._deliver_webhook(webhook, event, payload)
            results.append({
                "webhook_id": str(webhook.id),
                "success": result["success"],
                "status_code": result.get("status_code")
            })
        
        successful = sum(1 for r in results if r["success"])
        
        logger.info("Webhooks triggered", extra={
            "organization_id": organization_id,
            "event": event,
            "total": len(results),
            "successful": successful
        })
        
        return {
            "event": event,
            "webhooks_triggered": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }
    
    def _deliver_webhook(
        self,
        webhook: WebhookEndpoint,
        event: str,
        payload: Dict,
        retry_count: int = 0
    ) -> Dict:
        """
        Deliver webhook event with retry logic.
        
        Args:
            webhook: Webhook endpoint
            event: Event name
            payload: Event payload
            retry_count: Current retry attempt
            
        Returns:
            Delivery result
        """
        # Prepare payload
        full_payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Generate signature
        signature = self._generate_signature(webhook.secret, full_payload)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event,
            "User-Agent": "BugBountyPlatform-Webhook/1.0"
        }
        
        try:
            # Send webhook
            response = requests.post(
                webhook.url,
                json=full_payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Log delivery
            log = WebhookLog(
                endpoint_id=webhook.id,
                event=event,
                payload=full_payload,
                response_status=response.status_code,
                response_body=response.text[:1000],  # Limit to 1000 chars
                retry_count=retry_count
            )
            self.db.add(log)
            self.db.commit()
            
            # Check if successful (2xx status code)
            if 200 <= response.status_code < 300:
                logger.info("Webhook delivered successfully", extra={
                    "webhook_id": str(webhook.id),
                    "event": event,
                    "status_code": response.status_code
                })
                return {
                    "success": True,
                    "status_code": response.status_code
                }
            else:
                # Retry if not successful and retries remaining
                if retry_count < self.max_retries:
                    sleep(self.retry_delays[retry_count])
                    return self._deliver_webhook(webhook, event, payload, retry_count + 1)
                
                logger.warning("Webhook delivery failed", extra={
                    "webhook_id": str(webhook.id),
                    "event": event,
                    "status_code": response.status_code
                })
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
        
        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            
            # Log error
            log = WebhookLog(
                endpoint_id=webhook.id,
                event=event,
                payload=full_payload,
                error_message=error_msg,
                retry_count=retry_count
            )
            self.db.add(log)
            self.db.commit()
            
            # Retry if retries remaining
            if retry_count < self.max_retries:
                sleep(self.retry_delays[retry_count])
                return self._deliver_webhook(webhook, event, payload, retry_count + 1)
            
            logger.error("Webhook delivery timeout", extra={
                "webhook_id": str(webhook.id),
                "event": event
            })
            return {
                "success": False,
                "error": error_msg
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Log error
            log = WebhookLog(
                endpoint_id=webhook.id,
                event=event,
                payload=full_payload,
                error_message=error_msg,
                retry_count=retry_count
            )
            self.db.add(log)
            self.db.commit()
            
            logger.error("Webhook delivery error", extra={
                "webhook_id": str(webhook.id),
                "event": event,
                "error": error_msg
            })
            return {
                "success": False,
                "error": error_msg
            }
    
    def _generate_signature(self, secret: str, payload: Dict) -> str:
        """
        Generate HMAC signature for webhook payload.
        
        Args:
            secret: Webhook secret
            payload: Payload to sign
            
        Returns:
            HMAC signature
        """
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_signature(self, secret: str, payload: Dict, signature: str) -> bool:
        """
        Verify webhook signature.
        
        Args:
            secret: Webhook secret
            payload: Payload to verify
            signature: Provided signature
            
        Returns:
            True if signature is valid
        """
        expected_signature = self._generate_signature(secret, payload)
        return hmac.compare_digest(expected_signature, signature)
