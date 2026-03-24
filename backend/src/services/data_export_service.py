"""
Data Export Service — Data export request management and generation (FREQ-15)
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID
import csv
import json
import io
from pathlib import Path

from src.domain.models.ops import DataExport
from src.domain.models.user import User
from src.core.exceptions import NotFoundException, ForbiddenException
from src.core.logging import get_logger

logger = get_logger(__name__)


class DataExportService:
    """Service for data export request management and generation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.export_dir = Path("data/exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported export types
        self.export_types = [
            "reports",
            "payments",
            "analytics",
            "audit_logs",
            "program_data",
            "researcher_data",
            "organization_data",
            "ptaas_data",
            "code_review_data",
            "live_event_data"
        ]
        
        # Supported formats
        self.formats = ["csv", "json", "pdf", "xlsx"]
        
        # Export expiration (7 days)
        self.expiration_days = 7
    
    def request_export(
        self,
        user_id: str,
        export_type: str,
        format: str = "csv",
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Request a data export.
        
        Args:
            user_id: User ID
            export_type: Type of data to export
            format: Export format (csv, json, pdf, xlsx)
            filters: Optional filters for the export
            
        Returns:
            Export request details
        """
        # Validate user exists
        user = self.db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            raise NotFoundException("User not found.")
        
        # Validate export type
        if export_type not in self.export_types:
            raise ValueError(f"Invalid export type. Allowed: {', '.join(self.export_types)}")
        
        # Validate format
        if format not in self.formats:
            raise ValueError(f"Invalid format. Allowed: {', '.join(self.formats)}")
        
        # Create export request
        export = DataExport(
            user_id=UUID(user_id),
            export_type=export_type,
            format=format,
            filters=filters or {},
            status="pending",
            expires_at=datetime.utcnow() + timedelta(days=self.expiration_days)
        )
        
        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)
        
        logger.info("Data export requested", extra={
            "export_id": str(export.id),
            "user_id": user_id,
            "export_type": export_type
        })
        
        # TODO: Trigger background job to process export (Celery task)
        
        return {
            "export_id": str(export.id),
            "export_type": export.export_type,
            "format": export.format,
            "status": export.status,
            "expires_at": export.expires_at.isoformat(),
            "created_at": export.created_at.isoformat(),
            "message": "Export request created. Processing will begin shortly."
        }
    
    def list_exports(
        self,
        user_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """
        List data exports for a user.
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of data exports
        """
        query = self.db.query(DataExport).filter(
            DataExport.user_id == UUID(user_id)
        )
        
        if status:
            query = query.filter(DataExport.status == status)
        
        query = query.order_by(DataExport.created_at.desc())
        
        total = query.count()
        exports = query.offset(skip).limit(limit).all()
        
        return {
            "exports": [
                {
                    "export_id": str(e.id),
                    "export_type": e.export_type,
                    "format": e.format,
                    "status": e.status,
                    "file_size": e.file_size,
                    "created_at": e.created_at.isoformat(),
                    "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                    "expires_at": e.expires_at.isoformat() if e.expires_at else None
                }
                for e in exports
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def get_export(self, export_id: str, user_id: str) -> Dict:
        """
        Get export details.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
            
        Returns:
            Export details
        """
        export = self.db.query(DataExport).filter(
            DataExport.id == UUID(export_id)
        ).first()
        
        if not export:
            raise NotFoundException("Export not found.")
        
        # Verify ownership
        if str(export.user_id) != user_id:
            raise ForbiddenException("You don't have access to this export.")
        
        # Check if expired
        if export.expires_at and export.expires_at < datetime.utcnow():
            if export.status == "completed":
                export.status = "expired"
                self.db.commit()
        
        return {
            "export_id": str(export.id),
            "export_type": export.export_type,
            "format": export.format,
            "filters": export.filters,
            "status": export.status,
            "file_path": export.file_path,
            "file_size": export.file_size,
            "created_at": export.created_at.isoformat(),
            "completed_at": export.completed_at.isoformat() if export.completed_at else None,
            "expires_at": export.expires_at.isoformat() if export.expires_at else None
        }
    
    def cancel_export(self, export_id: str, user_id: str) -> Dict:
        """
        Cancel a pending export.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
            
        Returns:
            Cancellation confirmation
        """
        export = self.db.query(DataExport).filter(
            DataExport.id == UUID(export_id)
        ).first()
        
        if not export:
            raise NotFoundException("Export not found.")
        
        # Verify ownership
        if str(export.user_id) != user_id:
            raise ForbiddenException("You don't have access to this export.")
        
        # Can only cancel pending or processing exports
        if export.status not in ["pending", "processing"]:
            raise ValueError(f"Cannot cancel export with status: {export.status}")
        
        export.status = "failed"
        self.db.commit()
        
        logger.info("Data export cancelled", extra={
            "export_id": export_id,
            "user_id": user_id
        })
        
        return {
            "export_id": export_id,
            "status": "failed",
            "message": "Export cancelled successfully."
        }
    
    def delete_export(self, export_id: str, user_id: str) -> Dict:
        """
        Delete an export.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
            
        Returns:
            Deletion confirmation
        """
        export = self.db.query(DataExport).filter(
            DataExport.id == UUID(export_id)
        ).first()
        
        if not export:
            raise NotFoundException("Export not found.")
        
        # Verify ownership
        if str(export.user_id) != user_id:
            raise ForbiddenException("You don't have access to this export.")
        
        # Delete file if exists
        if export.file_path:
            file_path = self.export_dir / export.file_path
            if file_path.exists():
                file_path.unlink()
        
        self.db.delete(export)
        self.db.commit()
        
        logger.info("Data export deleted", extra={
            "export_id": export_id,
            "user_id": user_id
        })
        
        return {
            "export_id": export_id,
            "message": "Export deleted successfully."
        }
    
    def generate_csv_export(self, data: List[Dict], columns: List[str]) -> str:
        """
        Generate CSV export from data.
        
        Args:
            data: List of data dictionaries
            columns: Column names
            
        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        
        writer.writeheader()
        for row in data:
            writer.writerow({col: row.get(col, "") for col in columns})
        
        return output.getvalue()
    
    def generate_json_export(self, data: List[Dict]) -> str:
        """
        Generate JSON export from data.
        
        Args:
            data: List of data dictionaries
            
        Returns:
            JSON content as string
        """
        return json.dumps(data, indent=2, default=str)
    
    def process_export(self, export_id: str) -> Dict:
        """
        Process export request (to be called by background job).
        
        Args:
            export_id: Export ID
            
        Returns:
            Processing result
        """
        export = self.db.query(DataExport).filter(
            DataExport.id == UUID(export_id)
        ).first()
        
        if not export:
            raise NotFoundException("Export not found.")
        
        try:
            # Update status to processing
            export.status = "processing"
            self.db.commit()
            
            # TODO: Fetch data based on export_type and filters
            # This is a placeholder - actual implementation would query relevant tables
            data = []
            
            # Generate export file
            if export.format == "csv":
                content = self.generate_csv_export(data, columns=["id", "name", "value"])
            elif export.format == "json":
                content = self.generate_json_export(data)
            else:
                raise ValueError(f"Format {export.format} not yet implemented")
            
            # Save file
            filename = f"{export.export_type}_{export.id}.{export.format}"
            file_path = self.export_dir / filename
            
            with open(file_path, "w") as f:
                f.write(content)
            
            # Update export record
            export.status = "completed"
            export.file_path = filename
            export.file_size = file_path.stat().st_size
            export.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info("Data export completed", extra={
                "export_id": export_id,
                "file_size": export.file_size
            })
            
            return {
                "export_id": export_id,
                "status": "completed",
                "file_path": filename,
                "file_size": export.file_size
            }
        
        except Exception as e:
            # Update status to failed
            export.status = "failed"
            self.db.commit()
            
            logger.error("Data export failed", extra={
                "export_id": export_id,
                "error": str(e)
            })
            
            raise
    
    def get_download_url(self, export_id: str, user_id: str) -> Dict:
        """
        Get download URL for completed export.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
            
        Returns:
            Download URL
        """
        export = self.db.query(DataExport).filter(
            DataExport.id == UUID(export_id)
        ).first()
        
        if not export:
            raise NotFoundException("Export not found.")
        
        # Verify ownership
        if str(export.user_id) != user_id:
            raise ForbiddenException("You don't have access to this export.")
        
        # Check status
        if export.status != "completed":
            raise ValueError(f"Export is not ready. Status: {export.status}")
        
        # Check expiration
        if export.expires_at and export.expires_at < datetime.utcnow():
            export.status = "expired"
            self.db.commit()
            raise ValueError("Export has expired.")
        
        # Generate download URL
        download_url = f"/api/v1/exports/{export_id}/download"
        
        return {
            "export_id": export_id,
            "download_url": download_url,
            "file_size": export.file_size,
            "expires_at": export.expires_at.isoformat() if export.expires_at else None
        }
