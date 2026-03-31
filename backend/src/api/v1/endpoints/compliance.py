"""
Compliance Endpoints — API routes for compliance management (FREQ-22)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pathlib import Path

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.compliance_service import ComplianceService
from src.domain.models.user import User
from src.core.dependencies import get_current_user, require_admin
from src.api.v1.schemas.compliance import (
    ComplianceReportRequest,
    ComplianceReportResponse,
    ComplianceReportListResponse,
    ComplianceReportDeleteResponse,
    ComplianceReportTypesResponse
)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


def get_compliance_service(db: Session = Depends(get_db)) -> ComplianceService:
    """Dependency to get ComplianceService instance"""
    return ComplianceService(db)


@router.post(
    "/reports/generate",
    response_model=ComplianceReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Compliance Report",
    description="Generate a compliance report (Admin only)"
)
async def generate_report(
    data: ComplianceReportRequest,
    request: Request,
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    Generate a compliance report.
    
    Supported report types:
    - pci_dss: Payment Card Industry Data Security Standard
    - iso_27001: Information Security Management
    - soc2: Service Organization Control 2
    - hipaa: Health Insurance Portability and Accountability Act
    - gdpr: General Data Protection Regulation
    - platform_audit: General platform audit
    - security_audit: Security-focused audit
    - data_privacy: Data privacy compliance
    - vulnerability_disclosure: Vulnerability disclosure compliance
    """
    try:
        # Parse dates
        period_start = datetime.fromisoformat(data.period_start)
        period_end = datetime.fromisoformat(data.period_end)
        
        result = compliance_service.generate_report(
            report_type=data.report_type,
            period_start=period_start,
            period_end=period_end,
            generated_by=str(current_user.id)
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "COMPLIANCE_REPORT_GENERATED",
            str(current_user.id),
            {
                "report_id": result["report_id"],
                "report_type": data.report_type
            },
            request
        )
        
        return ComplianceReportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {str(e)}"
        )


@router.get(
    "/reports",
    response_model=ComplianceReportListResponse,
    summary="List Compliance Reports",
    description="List all compliance reports (Admin only)"
)
async def list_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    List all compliance reports.
    
    Optional filters:
    - report_type: Filter by report type
    """
    try:
        result = compliance_service.list_reports(
            report_type=report_type,
            skip=skip,
            limit=limit
        )
        
        return ComplianceReportListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list compliance reports: {str(e)}"
        )


@router.get(
    "/reports/{report_id}",
    response_model=ComplianceReportResponse,
    summary="Get Compliance Report",
    description="Get compliance report details (Admin only)"
)
async def get_report(
    report_id: str,
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    Get compliance report details.
    """
    try:
        result = compliance_service.get_report(report_id=report_id)
        return ComplianceReportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance report: {str(e)}"
        )


@router.delete(
    "/reports/{report_id}",
    response_model=ComplianceReportDeleteResponse,
    summary="Delete Compliance Report",
    description="Delete a compliance report (Admin only)"
)
async def delete_report(
    report_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    Delete a compliance report.
    """
    try:
        result = compliance_service.delete_report(report_id=report_id)
        
        # Log security event
        SecurityAudit.log_security_event(
            "COMPLIANCE_REPORT_DELETED",
            str(current_user.id),
            {"report_id": report_id},
            request
        )
        
        return ComplianceReportDeleteResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete compliance report: {str(e)}"
        )


@router.get(
    "/reports/{report_id}/download",
    summary="Download Compliance Report",
    description="Download compliance report file (Admin only)"
)
async def download_report(
    report_id: str,
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    Download compliance report file.
    """
    try:
        # Get report details
        report_data = compliance_service.get_report(report_id=report_id)
        
        if not report_data.get("file_path"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not found."
            )
        
        file_path = Path(report_data["file_path"])
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not found."
            )
        
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/json"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download compliance report: {str(e)}"
        )


@router.get(
    "/types/supported",
    response_model=ComplianceReportTypesResponse,
    summary="Get Supported Report Types",
    description="Get list of supported compliance report types (Admin only)"
)
async def get_supported_types(
    current_user: User = Depends(require_admin),
    compliance_service: ComplianceService = Depends(get_compliance_service)
):
    """
    Get list of supported compliance report types.
    """
    return ComplianceReportTypesResponse(
        report_types=compliance_service.report_types,
        total=len(compliance_service.report_types)
    )
