"""
Message Broker Service with RabbitMQ and Dead Letter Queue
Implements exponential backoff retry mechanism for FREQ-42
"""
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio

from celery import Celery
from celery.exceptions import Retry
from kombu import Queue, Exchange

from src.core.config import settings

logger = logging.getLogger(__name__)

# Celery app configuration
celery_app = Celery(
    "bugcrowd_integration",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Dead Letter Exchange and Queue
dlx_exchange = Exchange('dlx', type='topic', durable=True)
dlx_queue = Queue('dlq', exchange=dlx_exchange, routing_key='#', durable=True)

# Main exchange and queues
main_exchange = Exchange('integration', type='topic', durable=True)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_queues=(
        Queue(
            'integration.sync',
            exchange=main_exchange,
            routing_key='integration.sync',
            durable=True,
            queue_arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': 'integration.sync.failed'
            }
        ),
        Queue(
            'integration.webhook',
            exchange=main_exchange,
            routing_key='integration.webhook',
            durable=True,
            queue_arguments={
                'x-dead-letter-exchange': 'dlx',
                'x-dead-letter-routing-key': 'integration.webhook.failed'
            }
        ),
        dlx_queue,
    )
)


class ExponentialBackoff:
    """Exponential backoff calculator"""
    
    @staticmethod
    def calculate_delay(retry_count: int, base_delay: int = 1, max_delay: int = 16) -> int:
        """
        Calculate exponential backoff delay
        
        Args:
            retry_count: Current retry attempt (0-indexed)
            base_delay: Base delay in seconds (default: 1)
            max_delay: Maximum delay in seconds (default: 16)
            
        Returns:
            Delay in seconds: 1s, 2s, 4s, 8s, 16s
        """
        delay = base_delay * (2 ** retry_count)
        return min(delay, max_delay)


@celery_app.task(
    bind=True,
    max_retries=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=16,
    retry_jitter=False
)
def sync_to_external_system(
    self,
    integration_id: str,
    report_id: str,
    action: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Sync vulnerability report to external system (Jira/GitHub)
    
    Args:
        integration_id: Integration UUID
        report_id: Report UUID
        action: Sync action (create, update, delete)
        payload: Data to sync
        
    Returns:
        Sync result with external ID
    """
    from src.services.integration_service import IntegrationService
    from src.core.database import SessionLocal
    
    retry_count = self.request.retries
    delay = ExponentialBackoff.calculate_delay(retry_count)
    
    logger.info(
        f"Syncing to external system - Integration: {integration_id}, "
        f"Report: {report_id}, Action: {action}, Retry: {retry_count}"
    )
    
    db = SessionLocal()
    try:
        service = IntegrationService(db)
        result = service.sync_report_to_external(
            integration_id=integration_id,
            report_id=report_id,
            action=action,
            payload=payload
        )
        
        logger.info(f"Sync successful - External ID: {result.get('external_id')}")
        return result
        
    except Exception as e:
        logger.error(
            f"Sync failed (attempt {retry_count + 1}/5) - "
            f"Integration: {integration_id}, Error: {str(e)}"
        )
        
        # Log failure to database
        try:
            service = IntegrationService(db)
            service.log_sync_failure(
                integration_id=integration_id,
                report_id=report_id,
                action=action,
                error=str(e),
                retry_count=retry_count
            )
        except Exception as log_error:
            logger.error(f"Failed to log sync failure: {str(log_error)}")
        
        # Retry with exponential backoff
        if retry_count < 5:
            logger.info(f"Retrying in {delay} seconds...")
            raise self.retry(exc=e, countdown=delay)
        else:
            logger.error(f"Max retries reached - Moving to DLQ")
            raise
            
    finally:
        db.close()


@celery_app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def process_webhook_event(
    self,
    integration_id: str,
    event_id: str,
    event_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process incoming webhook event from external system
    
    Args:
        integration_id: Integration UUID
        event_id: Webhook event UUID
        event_type: Event type (issue.created, issue.updated, etc.)
        payload: Webhook payload
        
    Returns:
        Processing result
    """
    from src.services.integration_service import IntegrationService
    from src.core.database import SessionLocal
    
    retry_count = self.request.retries
    
    logger.info(
        f"Processing webhook event - Integration: {integration_id}, "
        f"Event: {event_type}, Retry: {retry_count}"
    )
    
    db = SessionLocal()
    try:
        service = IntegrationService(db)
        result = service.process_webhook(
            integration_id=integration_id,
            event_id=event_id,
            event_type=event_type,
            payload=payload
        )
        
        logger.info(f"Webhook processed successfully - Event ID: {event_id}")
        return result
        
    except Exception as e:
        logger.error(
            f"Webhook processing failed (attempt {retry_count + 1}/3) - "
            f"Event ID: {event_id}, Error: {str(e)}"
        )
        
        if retry_count < 3:
            delay = ExponentialBackoff.calculate_delay(retry_count)
            raise self.retry(exc=e, countdown=delay)
        else:
            logger.error(f"Max retries reached for webhook - Moving to DLQ")
            raise
            
    finally:
        db.close()


class MessageBrokerService:
    """Message broker service for async integration tasks"""
    
    @staticmethod
    def queue_sync_task(
        integration_id: str,
        report_id: str,
        action: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Queue a sync task to external system
        
        Args:
            integration_id: Integration UUID
            report_id: Report UUID
            action: Sync action
            payload: Data to sync
            
        Returns:
            Task ID
        """
        task = sync_to_external_system.apply_async(
            args=[integration_id, report_id, action, payload],
            queue='integration.sync',
            routing_key='integration.sync'
        )
        
        logger.info(f"Queued sync task - Task ID: {task.id}")
        return task.id
    
    @staticmethod
    def queue_webhook_task(
        integration_id: str,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Queue a webhook processing task
        
        Args:
            integration_id: Integration UUID
            event_id: Webhook event UUID
            event_type: Event type
            payload: Webhook payload
            
        Returns:
            Task ID
        """
        task = process_webhook_event.apply_async(
            args=[integration_id, event_id, event_type, payload],
            queue='integration.webhook',
            routing_key='integration.webhook'
        )
        
        logger.info(f"Queued webhook task - Task ID: {task.id}")
        return task.id
    
    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get task status"""
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.state,
            "result": result.result if result.ready() else None,
            "error": str(result.info) if result.failed() else None
        }
