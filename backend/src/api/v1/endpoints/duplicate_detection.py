"""
Duplicate Detection API Endpoints - Fix for missing 404 endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID

from src.core.database import get_db
from src.services.report_service import ReportService
from ..schemas.report import DuplicateCheckResponse

router = APIRouter(prefix="/duplicate-detection", tags=["Duplicate Detection"])

@router.post("/check", response_model=DuplicateCheckResponse)
async def check_duplicate_report(
    report_data: Dict,
    db: Session = Depends(get_db)
):
    """Check if report is duplicate"""
    try:
        service = ReportService(db)
        duplicate_info = service.check_duplicate(
            title=report_data.get("title"),
            description=report_data.get("description"),
            program_id=report_data.get("program_id"),
            user_id=report_data.get("user_id")
        )
        return DuplicateCheckResponse.from_dict(duplicate_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/program/{program_id}")
async def get_program_duplicates(
    program_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all duplicate reports for a program"""
    try:
        service = ReportService(db)
        duplicates = service.get_program_duplicates(str(program_id))
        return {
            "program_id": str(program_id),
            "duplicate_groups": duplicates,
            "total_duplicate_reports": sum(len(group["reports"]) for group in duplicates)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/report/{report_id}")
async def get_report_duplicate_status(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """Get duplicate status of a specific report"""
    try:
        service = ReportService(db)
        status = service.get_duplicate_status(str(report_id))
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        return status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/resolve/{duplicate_group_id}")
async def resolve_duplicate_group(
    duplicate_group_id: str,
    resolution_data: Dict,
    db: Session = Depends(get_db)
):
    """Resolve duplicate report group"""
    try:
        service = ReportService(db)
        success = service.resolve_duplicate_group(
            duplicate_group_id,
            resolution_data.get("primary_report_id"),
            resolution_data.get("resolution_notes")
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Duplicate group not found"
            )
        return {"message": "Duplicate group resolved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
