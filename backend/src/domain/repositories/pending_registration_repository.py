"""
Pending Registration Repository
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domain.models.pending_registration import PendingRegistration
from src.domain.repositories.base import BaseRepository


class PendingRegistrationRepository(BaseRepository[PendingRegistration]):
    """Repository for pending registrations"""
    
    def __init__(self, db: Session):
        super().__init__(db, PendingRegistration)
    
    def create(self, data):
        """
        Create a new pending registration.
        Accepts either a dict or a PendingRegistration object.
        """
        if isinstance(data, PendingRegistration):
            # If it's already an object, add it directly
            self.db.add(data)
            self.db.commit()
            self.db.refresh(data)
            return data
        else:
            # If it's a dict, use parent's create method
            return super().create(data)
    
    def get_by_email(self, email: str) -> Optional[PendingRegistration]:
        """Get pending registration by email"""
        return self.db.query(PendingRegistration).filter(
            PendingRegistration.email == email.lower()
        ).first()
    
    def get_by_token(self, token: str) -> Optional[PendingRegistration]:
        """Get pending registration by verification token"""
        return self.db.query(PendingRegistration).filter(
            PendingRegistration.verification_token == token
        ).first()
    
    def get_by_otp(self, email: str, otp: str) -> Optional[PendingRegistration]:
        """Get pending registration by email and OTP"""
        return self.db.query(PendingRegistration).filter(
            and_(
                PendingRegistration.email == email.lower(),
                PendingRegistration.verification_otp == otp,
                PendingRegistration.otp_expires_at > datetime.utcnow()
            )
        ).first()
    
    def get_expired(self) -> List[PendingRegistration]:
        """Get all expired pending registrations"""
        return self.db.query(PendingRegistration).filter(
            PendingRegistration.expires_at < datetime.utcnow()
        ).all()
    
    def cleanup_expired(self) -> int:
        """Delete expired pending registrations"""
        expired_count = self.db.query(PendingRegistration).filter(
            PendingRegistration.expires_at < datetime.utcnow()
        ).count()
        
        self.db.query(PendingRegistration).filter(
            PendingRegistration.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return expired_count
    
    def delete_by_email(self, email: str) -> bool:
        """Delete pending registration by email"""
        deleted = self.db.query(PendingRegistration).filter(
            PendingRegistration.email == email.lower()
        ).delete()
        
        self.db.commit()
        return deleted > 0