"""File Upload API Endpoints - FREQ-21."""
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from src.core.database import get_db
from src.api.v1.middlewares.auth import get_current_user
from src.domain.models.user import User
from src.services.file_storage_service import FileStorageService

# File upload constants
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.mp4', '.mov', '.avi', '.webm', '.log'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/serve/{file_path:path}")
async def serve_file(
    file_path: str,
    db: Session = Depends(get_db)
):
    """
    Serve uploaded files by proxying them from MinIO/S3 or local storage.
    This endpoint streams file content through the backend.
    """
    try:
        storage_service = FileStorageService(db)
        
        # Try S3/MinIO first
        if storage_service.s3_client:
            try:
                from src.core.config import settings
                bucket_name = getattr(settings, 'MINIO_BUCKET', 'bugbounty-files')
                
                response = storage_service.s3_client.get_object(
                    Bucket=bucket_name,
                    Key=file_path
                )
                
                content_type = response.get('ContentType', 'application/octet-stream')
                
                return StreamingResponse(
                    io.BytesIO(response['Body'].read()),
                    media_type=content_type,
                    headers={
                        'Content-Disposition': f'inline; filename="{file_path.split("/")[-1]}"',
                        'Cache-Control': 'public, max-age=3600'
                    }
                )
            except Exception as s3_error:
                # Fall through to local storage
                pass
        
        # Try local storage as fallback
        from src.core.config import settings
        local_storage_path = getattr(settings, 'LOCAL_STORAGE_PATH', 'uploads')
        local_file_path = os.path.join(local_storage_path, file_path)
        
        if os.path.exists(local_file_path):
            # Determine content type from extension
            import mimetypes
            content_type, _ = mimetypes.guess_type(local_file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Read and stream the file
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type=content_type,
                headers={
                    'Content-Disposition': f'inline; filename="{file_path.split("/")[-1]}"',
                    'Cache-Control': 'public, max-age=3600'
                }
            )
        
        # File not found in either location
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found in storage"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    report_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
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
        
        # Check file size by reading content
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Reset file pointer for upload
        await file.seek(0)
        
        # Store file using FileStorageService
        storage_service = FileStorageService(db)
        file_metadata = await storage_service.upload_file(
            file=file,
            user_id=current_user.id,
            file_type="evidence"
        )
        
        return {
            "filename": file_metadata["filename"],
            "file_path": file_metadata["storage_key"],
            "file_id": file_metadata["id"],
            "size": file_metadata["size"],
            "content_type": file_metadata["mime_type"],
            "uploaded_at": file_metadata["uploaded_at"]
        }
        
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
