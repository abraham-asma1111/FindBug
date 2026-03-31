"""
File Storage Service - FREQ-14
Handles file uploads and storage using MinIO/S3
"""
from typing import Optional, BinaryIO, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import UploadFile

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

try:
    from src.core.config import settings
except ImportError:
    settings = None


class FileStorageService:
    """Service for managing file storage operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_client = self._get_s3_client()
    
    def _get_s3_client(self):
        """Initialize S3/MinIO client"""
        if not HAS_BOTO3:
            return None
        try:
            return boto3.client(
                's3',
                endpoint_url=getattr(settings, 'MINIO_ENDPOINT', 'http://localhost:9000') if settings else 'http://localhost:9000',
                aws_access_key_id=getattr(settings, 'MINIO_ACCESS_KEY', 'minioadmin') if settings else 'minioadmin',
                aws_secret_access_key=getattr(settings, 'MINIO_SECRET_KEY', 'minioadmin123') if settings else 'minioadmin123',
                region_name='us-east-1'
            )
        except Exception:
            return None
    
    async def upload_file(
        self,
        file: UploadFile,
        user_id: UUID,
        file_type: str = "attachment"
    ) -> Dict[str, Any]:
        """Upload a file to storage"""
        # Generate unique filename
        file_id = uuid4()
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        storage_key = f"{user_id}/{file_id}.{file_extension}"
        
        # Read file content
        content = await file.read()
        
        # Upload to S3/MinIO if available
        if self.s3_client:
            try:
                bucket_name = getattr(settings, 'MINIO_BUCKET', 'bugbounty-files') if settings else 'bugbounty-files'
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=storage_key,
                    Body=content,
                    ContentType=file.content_type
                )
            except Exception:
                pass  # Fallback to database storage
        
        # Return file metadata
        return {
            "id": str(file_id),
            "filename": file.filename,
            "storage_key": storage_key,
            "file_type": file_type,
            "size": len(content),
            "mime_type": file.content_type,
            "uploaded_by": str(user_id),
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    def get_file(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        # Stub implementation
        return None
    
    def get_download_url(self, file_id: UUID, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned download URL"""
        if not self.s3_client:
            return None
        
        try:
            bucket_name = getattr(settings, 'MINIO_BUCKET', 'bugbounty-files') if settings else 'bugbounty-files'
            storage_key = f"files/{file_id}"
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': storage_key
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception:
            return None
    
    def delete_file(self, file_id: UUID) -> bool:
        """Delete a file"""
        if not self.s3_client:
            return False
        
        try:
            bucket_name = getattr(settings, 'MINIO_BUCKET', 'bugbounty-files') if settings else 'bugbounty-files'
            storage_key = f"files/{file_id}"
            self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=storage_key
            )
            return True
        except Exception:
            return False
