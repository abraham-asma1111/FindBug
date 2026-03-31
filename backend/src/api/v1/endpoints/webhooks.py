"""
Webhook Endpoints — API routes for webhook management (FREQ-42)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.webhook_service import WebhookService
from src.domain.models.user import User
from src.domain.models.organization import Organization
from src.core.dependencies import get_current_user
from src.api.v1.schemas.webhooks import (
    WebhookCreateRequest,
    WebhookUpdateRequest,
    WebhookResponse,
    WebhookListResponse,
    WebhookLogsResponse,
    WebhookTestResponse,
    WebhookDeleteResponse,
    WebhookEventsResponse
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def get_webhook_service(db: Session = Depends(get_db)) -> WebhookService:
    """Dependency to get WebhookService instance"""
    return WebhookService(db)


def get_organization_id(current_user: User, db: Session) -> str:
    """Get organization ID for current user"""
    if current_user.role != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizations can manage webhooks."
        )
    
    # Get organization
    org = db.query(Organization).filter(
        Organization.user_id == current_user.id
    ).first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found."
        )
    
    return str(org.id)


@router.post(
    "/create",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Webhook",
    description="Create a new webhook endpoint (Organization only)"
)
async def create_webhook(
    data: WebhookCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Create a new webhook endpoint.
    
    Requirements:
    - User must be an organization
    - URL must be valid (http:// or https://)
    - Events must be from supported list
    
    Supported events:
    - report.submitted, report.triaged, report.validated, report.duplicate, report.closed
    - bounty.approved, bounty.paid, bounty.rejected
    - program.published, program.paused, program.closed
    - ptaas.engagement_created, ptaas.finding_submitted, ptaas.deliverable_ready
    - code_review.started, code_review.finding_submitted, code_review.completed
    - live_event.started, live_event.ended, live_event.report_submitted
    - ai_redteam.engagement_created, ai_redteam.vulnerability_found, ai_redteam.report_ready
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.create_webhook(
            organization_id=organization_id,
            url=data.url,
            events=data.events,
            secret=data.secret
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "WEBHOOK_CREATED",
            str(current_user.id),
            {
                "webhook_id": result["webhook_id"],
                "url": data.url,
                "events": data.events
            },
            request
        )
        
        return WebhookResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create webhook: {str(e)}"
        )


@router.get(
    "/list",
    response_model=WebhookListResponse,
    summary="List Webhooks",
    description="List all webhook endpoints for organization"
)
async def list_webhooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    List all webhook endpoints for the organization.
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.list_webhooks(
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
        
        return WebhookListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list webhooks: {str(e)}"
        )


@router.get(
    "/{webhook_id}",
    response_model=WebhookResponse,
    summary="Get Webhook",
    description="Get webhook endpoint details"
)
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Get webhook endpoint details.
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.get_webhook(
            webhook_id=webhook_id,
            organization_id=organization_id
        )
        
        return WebhookResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook: {str(e)}"
        )


@router.put(
    "/{webhook_id}",
    response_model=WebhookResponse,
    summary="Update Webhook",
    description="Update webhook endpoint"
)
async def update_webhook(
    webhook_id: str,
    data: WebhookUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Update webhook endpoint.
    
    Can update:
    - URL
    - Events list
    - Active status
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.update_webhook(
            webhook_id=webhook_id,
            organization_id=organization_id,
            url=data.url,
            events=data.events,
            is_active=data.is_active
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "WEBHOOK_UPDATED",
            str(current_user.id),
            {"webhook_id": webhook_id},
            request
        )
        
        return WebhookResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update webhook: {str(e)}"
        )


@router.delete(
    "/{webhook_id}",
    response_model=WebhookDeleteResponse,
    summary="Delete Webhook",
    description="Delete webhook endpoint"
)
async def delete_webhook(
    webhook_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Delete webhook endpoint.
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.delete_webhook(
            webhook_id=webhook_id,
            organization_id=organization_id
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "WEBHOOK_DELETED",
            str(current_user.id),
            {"webhook_id": webhook_id},
            request
        )
        
        return WebhookDeleteResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete webhook: {str(e)}"
        )


@router.get(
    "/{webhook_id}/logs",
    response_model=WebhookLogsResponse,
    summary="Get Webhook Logs",
    description="Get webhook delivery logs"
)
async def get_webhook_logs(
    webhook_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Get webhook delivery logs.
    
    Shows:
    - Event name
    - Response status
    - Error messages
    - Retry count
    - Timestamp
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.get_webhook_logs(
            webhook_id=webhook_id,
            organization_id=organization_id,
            skip=skip,
            limit=limit
        )
        
        return WebhookLogsResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook logs: {str(e)}"
        )


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookTestResponse,
    summary="Test Webhook",
    description="Test webhook endpoint with a ping event"
)
async def test_webhook(
    webhook_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Test webhook endpoint.
    
    Sends a test event to verify:
    - URL is reachable
    - Endpoint responds correctly
    - Signature verification works
    """
    try:
        organization_id = get_organization_id(current_user, db)
        
        result = webhook_service.test_webhook(
            webhook_id=webhook_id,
            organization_id=organization_id
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "WEBHOOK_TESTED",
            str(current_user.id),
            {"webhook_id": webhook_id, "success": result["success"]},
            request
        )
        
        return WebhookTestResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test webhook: {str(e)}"
        )


@router.get(
    "/events/supported",
    response_model=WebhookEventsResponse,
    summary="Get Supported Events",
    description="Get list of supported webhook events"
)
async def get_supported_events(
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """
    Get list of all supported webhook events.
    
    Events are grouped by category:
    - Report events
    - Bounty events
    - Program events
    - PTaaS events
    - Code Review events
    - Live Event events
    - AI Red Teaming events
    """
    return WebhookEventsResponse(
        events=webhook_service.supported_events,
        total=len(webhook_service.supported_events)
    )
