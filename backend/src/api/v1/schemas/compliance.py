"""
Compliance Schemas — Pydantic models for compliance management (FREQ-22)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ComplianceReportRequest(BaseModel):
    """Request schema for compliance report generation"""
    report_type: str = Field(..., description="Type of compliance report")
    period_start: str = Field(..., description="Report period start date (ISO format)")
    period_end: str = Field(..., description="Report period end date (ISO format)")


class ComplianceReportResponse(BaseModel):
    """Response schema for compliance report"""
    report_id: str
    report_type: str
    period_start: str
    period_end: str
    data: Optional[Dict] = None
    file_path: Optional[str] = None
    generated_at: str
    generated_by: Optional[str] = None
    message: Optional[str] = None


class ComplianceReportListItem(BaseModel):
    """Single compliance report item in list"""
    report_id: str
    report_type: str
    period_start: str
    period_end: str
    generated_at: str
    generated_by: Optional[str] = None


class ComplianceReportListResponse(BaseModel):
    """Response schema for compliance report list"""
    reports: List[ComplianceReportListItem]
    total: int
    skip: int
    limit: int


class ComplianceReportDeleteResponse(BaseModel):
    """Response schema for compliance report deletion"""
    report_id: str
    message: str


class ComplianceReportTypesResponse(BaseModel):
    """Response schema for supported report types"""
    report_types: List[str]
    total: int
