"""
Integration API Endpoints
Implements FREQ-42: SSDLC Integration with Jira/GitHub
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.integration_service import IntegrationService
from src.domain.models.integration import IntegrationType, IntegrationStatus
from src.api.v1.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    SyncRequest,
    SyncResponse,
    WebhookEventCreate,
    WebhookEventResponse,
    ConflictResolutionRequest,
    ConflictResolutionResponse,
    FieldMappingCreate,
    FieldMappingResponse,
    SyncLogResponse,
    TaskStatusResponse
)
from src.core.message_broker import MessageBrokerService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    data: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new SSDLC integration (Jira/GitHub)
    
    Requires organization admin role
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    service = IntegrationService(db)
    
    try:
        integration_type = IntegrationType(data.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid integration type: {data.type}"
        )
    
    integration = service.create_integration(
        organization_id=current_user.organization_id,
        integration_type=integration_type,
        config=data.config
    )
    
    return integration


@router.get("", response_model=List[IntegrationResponse])
def list_integrations(
    integration_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List integrations for current organization
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to an organization"
        )
    
    service = IntegrationService(db)
    
    type_filter = None
    if integration_type:
        try:
            type_filter = IntegrationType(integration_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid integration type: {integration_type}"
            )
    
    integrations = service.list_integrations(
        organization_id=current_user.organization_id,
        integration_type=type_filter
    )
    
    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get integration by ID
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: UUID,
    data: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update integration configuration or status
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if data.status:
        try:
            status_enum = IntegrationStatus(data.status)
            integration = service.update_integration_status(integration_id, status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {data.status}"
            )
    
    if data.config:
        integration.config = data.config
        db.commit()
        db.refresh(integration)
    
    return integration


@router.post("/{integration_id}/sync", response_model=SyncResponse)
def sync_report(
    integration_id: UUID,
    data: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Queue sync task to external system
    
    Syncs vulnerability report to Jira/GitHub with exponential backoff retry
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if integration.status != IntegrationStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration is not active"
        )
    
    task_id = service.queue_sync(
        integration_id=integration_id,
        report_id=data.report_id,
        action=data.action,
        payload=data.payload
    )
    
    return SyncResponse(
        task_id=task_id,
        status="queued",
        message="Sync task queued successfully"
    )


@router.post("/{integration_id}/webhook", response_model=WebhookEventResponse)
async def receive_webhook(
    integration_id: UUID,
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_gitlab_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive webhook from external system (GitHub/Jira)
    
    Public endpoint with signature verification
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Get payload and headers
    payload = await request.json()
    headers = dict(request.headers)
    
    # Determine event type
    event_type = headers.get("x-github-event") or headers.get("x-gitlab-event") or "unknown"
    
    # Get signature
    signature = x_hub_signature_256 or x_gitlab_token
    
    # Receive and verify webhook
    event = service.receive_webhook(
        integration_id=integration_id,
        event_type=event_type,
        payload=payload,
        headers=headers,
        signature=signature
    )
    
    if not event.is_verified and signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    return event


@router.post("/{integration_id}/resolve-conflict", response_model=ConflictResolutionResponse)
def resolve_conflict(
    integration_id: UUID,
    data: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resolve sync conflict between local and remote data
    
    Strategies:
    - timestamp: Choose most recent update
    - local: Local data wins
    - remote: Remote data wins
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    result = service.resolve_conflict(
        integration_id=integration_id,
        report_id=data.report_id,
        strategy=data.strategy
    )
    
    return ConflictResolutionResponse(
        strategy=result["strategy"],
        winner=result["winner"],
        message=f"Conflict resolved using {result['strategy']} strategy"
    )


@router.get("/{integration_id}/sync-logs", response_model=List[SyncLogResponse])
def get_sync_logs(
    integration_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sync logs for integration
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    from src.domain.models.integration import SyncLog
    
    logs = db.query(SyncLog).filter(
        SyncLog.integration_id == integration_id
    ).order_by(SyncLog.created_at.desc()).limit(limit).all()
    
    return logs


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of async sync task
    """
    broker = MessageBrokerService()
    status_data = broker.get_task_status(task_id)
    
    return TaskStatusResponse(**status_data)


@router.post("/{integration_id}/field-mappings", response_model=FieldMappingResponse)
def create_field_mapping(
    integration_id: UUID,
    data: FieldMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create field mapping for integration
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    from src.domain.models.integration import IntegrationFieldMapping, TransformationType
    
    mapping = IntegrationFieldMapping(
        integration_id=integration_id,
        source_field=data.source_field,
        target_field=data.target_field,
        transformation=TransformationType(data.transformation),
        is_required=data.is_required,
        default_value=data.default_value
    )
    
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    
    return mapping


@router.get("/{integration_id}/field-mappings", response_model=List[FieldMappingResponse])
def list_field_mappings(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List field mappings for integration
    """
    service = IntegrationService(db)
    integration = service.get_integration(integration_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    from src.domain.models.integration import IntegrationFieldMapping
    
    mappings = db.query(IntegrationFieldMapping).filter(
        IntegrationFieldMapping.integration_id == integration_id
    ).all()
    
    return mappings
