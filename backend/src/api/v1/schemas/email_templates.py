"""
Email Template Schemas — Pydantic models for email template management (FREQ-12)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class EmailTemplateCreateRequest(BaseModel):
    """Request schema for creating email template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name (unique identifier)")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject line")
    body_html: str = Field(..., min_length=1, description="HTML email body")
    body_text: Optional[str] = Field(None, description="Plain text email body (optional)")
    variables: Optional[List[str]] = Field(None, description="List of variable names (auto-extracted if not provided)")


class EmailTemplateUpdateRequest(BaseModel):
    """Request schema for updating email template"""
    subject: Optional[str] = Field(None, min_length=1, max_length=200, description="New email subject")
    body_html: Optional[str] = Field(None, min_length=1, description="New HTML body")
    body_text: Optional[str] = Field(None, description="New text body")
    variables: Optional[List[str]] = Field(None, description="New variables list")
    is_active: Optional[bool] = Field(None, description="Active status")


class EmailTemplateResponse(BaseModel):
    """Response schema for email template"""
    template_id: str
    name: str
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    message: Optional[str] = None


class EmailTemplateListItem(BaseModel):
    """Single email template item in list"""
    template_id: str
    name: str
    subject: str
    variables: Optional[List[str]] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None


class EmailTemplateListResponse(BaseModel):
    """Response schema for email template list"""
    templates: List[EmailTemplateListItem]
    total: int
    skip: int
    limit: int


class EmailTemplateRenderRequest(BaseModel):
    """Request schema for rendering email template"""
    template_id: Optional[str] = Field(None, description="Template ID")
    template_name: Optional[str] = Field(None, description="Template name")
    variables: Optional[Dict[str, str]] = Field(None, description="Variable values to substitute")


class EmailTemplateRenderResponse(BaseModel):
    """Response schema for rendered email template"""
    template_id: str
    template_name: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    missing_variables: Optional[List[str]] = None


class EmailTemplateDeleteResponse(BaseModel):
    """Response schema for email template deletion"""
    template_id: str
    message: str
