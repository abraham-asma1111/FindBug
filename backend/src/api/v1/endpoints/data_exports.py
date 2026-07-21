"""
Data Export Endpoints — API routes for data export management (FREQ-15)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path

from src.core.database import get_db
from src.core.security import SecurityAudit
from src.services.data_export_service import DataExportService
from src.domain.models.user import User
from src.core.dependencies import get_current_user
from src.api.v1.schemas.data_exports import (
    DataExportRequest,
    DataExportResponse,
    DataExportListResponse,
    DataExportDownloadResponse,
    DataExportDeleteResponse,
    DataExportTypesResponse
)

router = APIRouter(prefix="/exports", tags=["Data Exports"])


def get_data_export_service(db: Session = Depends(get_db)) -> DataExportService:
    """Dependency to get DataExportService instance"""
    return DataExportService(db)


@router.post(
    "/request",
    response_model=DataExportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request Data Export",
    description="Request a data export"
)
async def request_export(
    data: DataExportRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Request a data export.
    
    Supported export types:
    - reports, payments, analytics, audit_logs
    - program_data, researcher_data, organization_data
    - ptaas_data, code_review_data, live_event_data
    
    Supported formats:
    - csv, json, pdf, xlsx
    
    Export will be processed in background and available for 7 days.
    """
    try:
        result = export_service.request_export(
            user_id=str(current_user.id),
            export_type=data.export_type,
            format=data.format,
            filters=data.filters
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "DATA_EXPORT_REQUESTED",
            str(current_user.id),
            {"export_id": result["export_id"], "export_type": data.export_type},
            request
        )
        
        return DataExportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request export: {str(e)}"
        )


@router.get(
    "/list",
    response_model=DataExportListResponse,
    summary="List Data Exports",
    description="List all data exports for current user"
)
async def list_exports(
    export_status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    List all data exports for current user.
    
    Optional filters:
    - status: Filter by status (pending, processing, completed, failed, expired)
    """
    try:
        result = export_service.list_exports(
            user_id=str(current_user.id),
            status=export_status,
            skip=skip,
            limit=limit
        )
        
        return DataExportListResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list exports: {str(e)}"
        )


@router.get(
    "/{export_id}",
    response_model=DataExportResponse,
    summary="Get Export Details",
    description="Get data export details"
)
async def get_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Get data export details.
    """
    try:
        result = export_service.get_export(
            export_id=export_id,
            user_id=str(current_user.id)
        )
        
        return DataExportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export: {str(e)}"
        )


@router.post(
    "/{export_id}/cancel",
    response_model=DataExportResponse,
    summary="Cancel Export",
    description="Cancel a pending or processing export"
)
async def cancel_export(
    export_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Cancel a pending or processing export.
    """
    try:
        result = export_service.cancel_export(
            export_id=export_id,
            user_id=str(current_user.id)
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "DATA_EXPORT_CANCELLED",
            str(current_user.id),
            {"export_id": export_id},
            request
        )
        
        return DataExportResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel export: {str(e)}"
        )


@router.delete(
    "/{export_id}",
    response_model=DataExportDeleteResponse,
    summary="Delete Export",
    description="Delete a data export"
)
async def delete_export(
    export_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Delete a data export.
    """
    try:
        result = export_service.delete_export(
            export_id=export_id,
            user_id=str(current_user.id)
        )
        
        # Log security event
        SecurityAudit.log_security_event(
            "DATA_EXPORT_DELETED",
            str(current_user.id),
            {"export_id": export_id},
            request
        )
        
        return DataExportDeleteResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete export: {str(e)}"
        )


@router.get(
    "/{export_id}/download-url",
    response_model=DataExportDownloadResponse,
    summary="Get Download URL",
    description="Get download URL for completed export"
)
async def get_download_url(
    export_id: str,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Get download URL for completed export.
    """
    try:
        result = export_service.get_download_url(
            export_id=export_id,
            user_id=str(current_user.id)
        )
        
        return DataExportDownloadResponse(**result)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get download URL: {str(e)}"
        )


@router.get(
    "/{export_id}/download",
    summary="Download Export File",
    description="Download export file"
)
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Download export file.
    """
    try:
        # Get export details
        export_data = export_service.get_export(
            export_id=export_id,
            user_id=str(current_user.id)
        )
        
        if export_data["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export is not ready. Status: {export_data['status']}"
            )
        
        # Get file path
        file_path = Path(export_service.export_dir) / export_data["file_path"]
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found."
            )
        
        return FileResponse(
            path=str(file_path),
            filename=export_data["file_path"],
            media_type="application/octet-stream"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download export: {str(e)}"
        )


@router.get(
    "/types/supported",
    response_model=DataExportTypesResponse,
    summary="Get Supported Export Types",
    description="Get list of supported export types and formats"
)
async def get_supported_types(
    export_service: DataExportService = Depends(get_data_export_service)
):
    """
    Get list of supported export types and formats.
    """
    return DataExportTypesResponse(
        export_types=export_service.export_types,
        formats=export_service.formats
    )
