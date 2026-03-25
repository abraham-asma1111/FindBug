"""
KYC Service — Document verification and admin review (FREQ-01)
"""
from typing import Dict, List, Optional, Type
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from uuid import UUID

from src.domain.models.kyc import KYCVerification
from src.domain.models.user import User
from src.core.file_storage import FileStorageService
from src.core.exceptions import NotFoundException, ForbiddenException, ConflictException
from src.core.logging import get_logger

logger = get_logger(__name__)


class KYCService:
    """Service for KYC verification management"""
    
    def __init__(self, db: Session, file_storage: Optional[FileStorageService] = None):
        self.db = db
        self.file_storage = file_storage or FileStorageService(base_path="data/uploads/kyc")
        
        # Allowed document types
        self.allowed_document_types = [
            "passport",
            "national_id",
            "drivers_license",
            "residence_permit"
        ]
        
        # KYC expiration period (2 years)
        self.expiration_days = 730
    
    def submit_kyc(
        self,
        user_id: str,
        document_type: str,
        document_number: str,
        document_front,
        document_back=None,
        selfie_photo=None
    ) -> Dict:
        """
        Submit KYC documents for verification.
        
        Args:
            user_id: User ID
            document_type: Type of document (passport, national_id, etc.)
            document_number: Document identification number
            document_front: Front side of document (UploadFile)
            document_back: Back side of document (UploadFile, optional)
            selfie_photo: Selfie photo (UploadFile, optional)
            
        Returns:
            KYC verification details
        """
        # Validate user exists
        user = self.db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            raise NotFoundException("User not found.")
        
        # Validate document type
        if document_type not in self.allowed_document_types:
            raise ValueError(f"Invalid document type. Allowed: {', '.join(self.allowed_document_types)}")
        
        # Check if user already has pending or approved KYC
        existing_kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == UUID(user_id),
            KYCVerification.status.in_(["pending", "approved"])
        ).first()
        
        if existing_kyc:
            raise ConflictException(f"KYC verification already {existing_kyc.status}.")
        
        # Upload documents
        document_front_path = None
        document_back_path = None
        selfie_path = None
        
        try:
            # Upload front document
            if document_front:
                front_metadata = self.file_storage.save_file(
                    document_front,
                    UUID(user_id),
                    subfolder="kyc/documents"
                )
                document_front_path = front_metadata["storage_path"]
            
            # Upload back document (if provided)
            if document_back:
                back_metadata = self.file_storage.save_file(
                    document_back,
                    UUID(user_id),
                    subfolder="kyc/documents"
                )
                document_back_path = back_metadata["storage_path"]
            
            # Upload selfie (if provided)
            if selfie_photo:
                selfie_metadata = self.file_storage.save_file(
                    selfie_photo,
                    UUID(user_id),
                    subfolder="kyc/selfies"
                )
                selfie_path = selfie_metadata["storage_path"]
            
            # Create KYC verification record
            kyc = KYCVerification(
                user_id=UUID(user_id),
                status="pending",
                document_type=document_type,
                document_number=document_number,
                document_front=document_front_path,
                document_back=document_back_path,
                selfie_photo=selfie_path,
                expires_at=datetime.utcnow() + timedelta(days=self.expiration_days)
            )
            
            self.db.add(kyc)
            self.db.commit()
            self.db.refresh(kyc)
            
            logger.info("KYC submitted", extra={"user_id": user_id, "kyc_id": str(kyc.id)})
            
            return {
                "kyc_id": str(kyc.id),
                "status": kyc.status,
                "document_type": kyc.document_type,
                "submitted_at": kyc.created_at.isoformat(),
                "message": "KYC documents submitted successfully. Pending admin review."
            }
            
        except Exception as e:
            # Cleanup uploaded files on error
            if document_front_path:
                self.file_storage.delete_file(document_front_path)
            if document_back_path:
                self.file_storage.delete_file(document_back_path)
            if selfie_path:
                self.file_storage.delete_file(selfie_path)
            
            logger.error("KYC submission failed", extra={"user_id": user_id, "error": str(e)})
            raise
    
    def get_kyc_status(self, user_id: str) -> Dict:
        """
        Get KYC verification status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            KYC status details
        """
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == UUID(user_id)
        ).order_by(KYCVerification.created_at.desc()).first()
        
        if not kyc:
            return {
                "status": "not_submitted",
                "message": "No KYC verification found."
            }
        
        return {
            "kyc_id": str(kyc.id),
            "status": kyc.status,
            "document_type": kyc.document_type,
            "submitted_at": kyc.created_at.isoformat() if kyc.created_at else None,
            "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None,
            "expires_at": kyc.expires_at.isoformat() if kyc.expires_at else None,
            "rejection_reason": kyc.rejection_reason,
            "message": f"KYC status: {kyc.status}"
        }
    
    def get_pending_kyc(self, skip: int = 0, limit: int = 20) -> Dict:
        """
        Get pending KYC verifications for admin review.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of pending KYC verifications
        """
        query = self.db.query(KYCVerification).filter(
            KYCVerification.status == "pending"
        ).order_by(KYCVerification.created_at.asc())
        
        total = query.count()
        kyc_list = query.offset(skip).limit(limit).all()
        
        return {
            "kyc_verifications": [
                {
                    "kyc_id": str(kyc.id),
                    "user_id": str(kyc.user_id),
                    "user_email": kyc.user.email if kyc.user else None,
                    "document_type": kyc.document_type,
                    "document_number": kyc.document_number,
                    "submitted_at": kyc.created_at.isoformat() if kyc.created_at else None,
                    "document_front": kyc.document_front,
                    "document_back": kyc.document_back,
                    "selfie_photo": kyc.selfie_photo
                }
                for kyc in kyc_list
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def review_kyc(
        self,
        kyc_id: str,
        reviewer_id: str,
        approved: bool,
        rejection_reason: Optional[str] = None
    ) -> Dict:
        """
        Admin review of KYC verification.
        
        Args:
            kyc_id: KYC verification ID
            reviewer_id: Admin user ID
            approved: Whether to approve or reject
            rejection_reason: Reason for rejection (required if not approved)
            
        Returns:
            Updated KYC verification details
        """
        # Validate reviewer is admin
        reviewer = self.db.query(User).filter(User.id == UUID(reviewer_id)).first()
        if not reviewer or reviewer.role not in ["admin", "staff"]:
            raise ForbiddenException("Only admins can review KYC verifications.")
        
        # Get KYC verification
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.id == UUID(kyc_id)
        ).first()
        
        if not kyc:
            raise NotFoundException("KYC verification not found.")
        
        if kyc.status != "pending":
            raise ConflictException(f"KYC verification already {kyc.status}.")
        
        # Update KYC status
        if approved:
            kyc.status = "approved"
            kyc.verified_by = UUID(reviewer_id)
            kyc.verified_at = datetime.utcnow()
            kyc.rejection_reason = None
            message = "KYC verification approved."
        else:
            if not rejection_reason:
                raise ValueError("Rejection reason is required when rejecting KYC.")
            
            kyc.status = "rejected"
            kyc.verified_by = UUID(reviewer_id)
            kyc.verified_at = datetime.utcnow()
            kyc.rejection_reason = rejection_reason
            message = "KYC verification rejected."
        
        self.db.commit()
        self.db.refresh(kyc)
        
        logger.info("KYC reviewed", extra={
            "kyc_id": kyc_id,
            "reviewer_id": reviewer_id,
            "approved": approved
        })
        
        # TODO: Send notification to user about KYC status
        
        return {
            "kyc_id": str(kyc.id),
            "user_id": str(kyc.user_id),
            "status": kyc.status,
            "verified_by": str(kyc.verified_by) if kyc.verified_by else None,
            "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None,
            "rejection_reason": kyc.rejection_reason,
            "message": message
        }
    
    def get_kyc_history(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """
        Get KYC verification history (admin only).
        
        Args:
            user_id: Filter by user ID (optional)
            status: Filter by status (optional)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of KYC verifications
        """
        query = self.db.query(KYCVerification)
        
        if user_id:
            query = query.filter(KYCVerification.user_id == UUID(user_id))
        
        if status:
            query = query.filter(KYCVerification.status == status)
        
        query = query.order_by(KYCVerification.created_at.desc())
        
        total = query.count()
        kyc_list = query.offset(skip).limit(limit).all()
        
        return {
            "kyc_verifications": [
                {
                    "kyc_id": str(kyc.id),
                    "user_id": str(kyc.user_id),
                    "user_email": kyc.user.email if kyc.user else None,
                    "status": kyc.status,
                    "document_type": kyc.document_type,
                    "submitted_at": kyc.created_at.isoformat() if kyc.created_at else None,
                    "verified_at": kyc.verified_at.isoformat() if kyc.verified_at else None,
                    "verified_by": str(kyc.verified_by) if kyc.verified_by else None,
                    "rejection_reason": kyc.rejection_reason,
                    "expires_at": kyc.expires_at.isoformat() if kyc.expires_at else None
                }
                for kyc in kyc_list
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def update_kyc_status(self, kyc_id: str, status: str) -> Dict:
        """
        Update KYC verification status (admin only).
        
        Args:
            kyc_id: KYC verification ID
            status: New status
            
        Returns:
            Updated KYC verification details
        """
        allowed_statuses = ["pending", "approved", "rejected", "expired"]
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status. Allowed: {', '.join(allowed_statuses)}")
        
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.id == UUID(kyc_id)
        ).first()
        
        if not kyc:
            raise NotFoundException("KYC verification not found.")
        
        kyc.status = status
        self.db.commit()
        self.db.refresh(kyc)
        
        logger.info("KYC status updated", extra={"kyc_id": kyc_id, "status": status})
        
        return {
            "kyc_id": str(kyc.id),
            "status": kyc.status,
            "message": f"KYC status updated to {status}."
        }
 