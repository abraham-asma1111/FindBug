"""File Upload API Endpoints - FREQ-21."""
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.file_storage_service import FileStorageService

# File upload constants
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/files", tags=["files"])


class FileUploadResponse:
    def __init__(self, filename, file_path, size, content_type, uploaded_at):
        self.filename = filename
        self.file_path = file_path
        self.size = size
        self.content_type = content_type
        self.uploaded_at = uploaded_at


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    report_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload file with proper validation and storage
    """
    try:
        # Validate file
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Store file
        storage_service = FileStorageService()
        file_path = storage_service.save_file(
            file_content,
            user_id=user_id,
            subfolder=f"uploads/{datetime.utcnow().strftime('%Y/%m/%d')}"
        )
        
        return FileUploadResponse(
            filename=file.filename,
            file_path=file_path["storage_path"],
            size=len(file_content),
            content_type=file.content_type,
            uploaded_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{file_id}", status_code=status.HTTP_200_OK)
def get_file_info(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get file information - FREQ-21.
    """
    service = FileStorageService(db)
    
    try:
        file_record = service.get_file_by_id(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return {
            "file_id": str(file_record.id),
            "filename": file_record.filename,
            "original_filename": file_record.original_filename,
            "file_type": file_record.file_type,
            "file_size": file_record.file_size,
            "file_url": file_record.file_url,
            "uploaded_by": str(file_record.uploaded_by_user_id),
            "uploaded_at": file_record.uploaded_at,
            "description": file_record.description
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete file - FREQ-21.
    
    Only file owner or admin can delete files.
    """
    service = FileStorageService(db)
    
    try:
        file_record = service.get_file_by_id(file_id)
        
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check permission
        if file_record.uploaded_by_user_id != current_user.id and current_user.role not in ["admin", "staff"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file"
            )
        
        service.delete_file(file_id)
        
        return {
            "message": "File deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
