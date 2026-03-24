"""
Email Template Endpoints — API routes for email template management (FREQ-12)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.email_template_service import EmailTemplateService
from src.domain.models.user import User
from src.api.v1.middlewares import get_current_user, require_admin
from src.api.v1.schemas.email_templates import (
    EmailTemplateCreateRequest,
    EmailTemplateUpdateRequest,
    EmailTemplateResponse,
    EmailTemplateListResponse,
    EmailTemplateRenderRequest,
    EmailTemplateRenderResponse,
    EmailTemplateDeleteResponse
)

router = APIRouter(prefix="/email-templates", tags=["Email Templates"])


def get_email_template_service(db: Session = Depends(get_db)) -> EmailTemplateService:
    """Dependency to get EmailTemplateService instance"""
    return EmailTemplateService(db)


@router.post(
    "/create",
    response_model=EmailTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Email Template",
    description="Create a new email template (Admin only)"
)
async def create_template(
    data: EmailTemplateCreateRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Create a new email template.
    
    Variables in templates use {{variable_name}} syntax.
    
    Example:
    - Subject: "Welcome {{user_name}}!"
    - Body: "Hello {{user_name}}, your account is ready."
    
    Variables are automatically extracted if not provided.
    """
    try:
        result = template_service.create_template(
            name=data.name,
            subject=data.subject,
            body_html=data.body_html,
            body_text=data.body_text,
            variables=data.variables
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "EMAIL_TEMPLATE_CREATED",
            str(current_user.id),
            {"template_id": result["template_id"], "name": data.name},
            request
        )
        
        return EmailTemplateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email template: {str(e)}"
        )


@router.get(
    "/list",
    response_model=EmailTemplateListResponse,
    summary="List Email Templates",
    description="List all email templates (Admin only)"
)
async def list_templates(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    List all email templates.
    
    Optional filters:
    - is_active: Filter by active status
    """
    try:
        result = template_service.list_templates(
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        return EmailTemplateListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list email templates: {str(e)}"
        )


@router.get(
    "/{template_id}",
    response_model=EmailTemplateResponse,
    summary="Get Email Template",
    description="Get email template details (Admin only)"
)
async def get_template(
    template_id: str,
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Get email template details by ID.
    """
    try:
        result = template_service.get_template(template_id=template_id)
        return EmailTemplateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email template: {str(e)}"
        )


@router.get(
    "/name/{template_name}",
    response_model=EmailTemplateResponse,
    summary="Get Email Template by Name",
    description="Get email template details by name (Admin only)"
)
async def get_template_by_name(
    template_name: str,
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Get email template details by name.
    """
    try:
        result = template_service.get_template(name=template_name)
        return EmailTemplateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get email template: {str(e)}"
        )


@router.put(
    "/{template_id}",
    response_model=EmailTemplateResponse,
    summary="Update Email Template",
    description="Update email template (Admin only)"
)
async def update_template(
    template_id: str,
    data: EmailTemplateUpdateRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Update email template.
    
    Can update:
    - Subject
    - HTML body
    - Text body
    - Variables list
    - Active status
    """
    try:
        result = template_service.update_template(
            template_id=template_id,
            subject=data.subject,
            body_html=data.body_html,
            body_text=data.body_text,
            variables=data.variables,
            is_active=data.is_active
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "EMAIL_TEMPLATE_UPDATED",
            str(current_user.id),
            {"template_id": template_id},
            request
        )
        
        return EmailTemplateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update email template: {str(e)}"
        )


@router.delete(
    "/{template_id}",
    response_model=EmailTemplateDeleteResponse,
    summary="Delete Email Template",
    description="Delete email template (Admin only)"
)
async def delete_template(
    template_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Delete email template.
    """
    try:
        result = template_service.delete_template(template_id=template_id)
        
        # Log security event
        SecurityAudit.log_security_event(
            "EMAIL_TEMPLATE_DELETED",
            str(current_user.id),
            {"template_id": template_id},
            request
        )
        
        return EmailTemplateDeleteResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete email template: {str(e)}"
        )


@router.post(
    "/render",
    response_model=EmailTemplateRenderResponse,
    summary="Render Email Template",
    description="Render email template with variables"
)
async def render_template(
    data: EmailTemplateRenderRequest,
    current_user: User = Depends(get_current_user),
    template_service: EmailTemplateService = Depends(get_email_template_service)
):
    """
    Render email template with variable substitution.
    
    Provide either template_id or template_name.
    
    Variables should be provided as key-value pairs:
    {
      "user_name": "John Doe",
      "amount": "100.00"
    }
    """
    try:
        result = template_service.render_template(
            template_id=data.template_id,
            name=data.template_name,
            variables=data.variables
        )
        
        return EmailTemplateRenderResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render email template: {str(e)}"
        )
