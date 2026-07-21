"""
Organization Verification Service
Handles organization verification workflow
"""
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from src.domain.models.organization import Organization
from src.domain.models.user import User
from src.services.notification_service import NotificationService
from src.domain.models.notification import NotificationType, NotificationPriority
from src.core.logging import get_logger

logger = get_logger(__name__)


class OrganizationVerificationService:
    """Service for organization verification operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    def submit_verification(
        self,
        organization_id: UUID,
        business_license_url: Optional[str] = None,
        tax_id: Optional[str] = None,
        website: Optional[str] = None
    ) -> Organization:
        """
        Submit organization for verification.
        
        Args:
            organization_id: Organization ID
            business_license_url: URL to business license document
            tax_id: Tax identification number
            website: Company website
            
        Returns:
            Updated organization
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        # Update verification details
        if business_license_url:
            org.business_license_url = business_license_url
        if tax_id:
            org.tax_id = tax_id
        if website:
            org.website = website
        
        # Set status to submitted
        org.verification_status = "submitted"
        
        self.db.commit()
        self.db.refresh(org)
        
        # Notify admins about new verification request
        self._notify_admins_new_verification(org)
        
        # Notify organization that submission was received
        self._notify_organization_submission_received(org)
        
        logger.info(f"Organization {organization_id} submitted for verification")
        
        return org
    
    def approve_verification(
        self,
        admin_id: UUID,
        organization_id: UUID,
        notes: Optional[str] = None
    ) -> Organization:
        """
        Approve organization verification.
        
        Args:
            admin_id: Admin user ID
            organization_id: Organization ID
            notes: Optional approval notes
            
        Returns:
            Updated organization
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        if org.verification_status not in ["submitted", "pending"]:
            raise ValueError(
                f"Cannot approve organization with status: {org.verification_status}"
            )
        
        # Update status to 'active' so the organization can create/publish programs
        org.verification_status = "active"
        
        self.db.commit()
        self.db.refresh(org)
        
        # Notify organization
        self._notify_organization_approved(org, notes)
        
        # Log admin action
        from src.domain.models.security_log import SecurityEvent
        event = SecurityEvent(
            user_id=admin_id,
            event_type="organization_verification_approved",
            severity="low",
            description=f"Approved verification for organization: {org.company_name}",
            is_blocked=False
        )
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Organization {organization_id} verification approved by admin {admin_id}")
        
        return org
    
    def reject_verification(
        self,
        admin_id: UUID,
        organization_id: UUID,
        reason: str
    ) -> Organization:
        """
        Reject organization verification.
        
        Args:
            admin_id: Admin user ID
            organization_id: Organization ID
            reason: Rejection reason
            
        Returns:
            Updated organization
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        if org.verification_status not in ["submitted", "pending"]:
            raise ValueError(
                f"Cannot reject organization with status: {org.verification_status}"
            )
        
        # Update status
        org.verification_status = "rejected"
        
        self.db.commit()
        self.db.refresh(org)
        
        # Notify organization
        self._notify_organization_rejected(org, reason)
        
        # Log admin action
        from src.domain.models.security_log import SecurityEvent
        event = SecurityEvent(
            user_id=admin_id,
            event_type="organization_verification_rejected",
            severity="low",
            description=f"Rejected verification for organization: {org.company_name}. Reason: {reason}",
            is_blocked=False
        )
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Organization {organization_id} verification rejected by admin {admin_id}")
        
        return org
    
    def check_verification_status(self, organization_id: UUID) -> Dict:
        """
        Check organization verification status.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Verification status details
        """
        org = self.db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not org:
            raise ValueError("Organization not found")
        
        return {
            "organization_id": str(org.id),
            "company_name": org.company_name,
            "verification_status": org.verification_status,
            "domain_verified": org.domain_verified,
            "business_license_url": org.business_license_url,
            "tax_id": org.tax_id,
            "website": org.website,
            "can_create_programs": org.verification_status == "approved"
        }
    
    def get_pending_verifications(self, limit: int = 50, offset: int = 0):
        """
        Get all organizations pending verification.
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of organizations pending verification
        """
        orgs = self.db.query(Organization).filter(
            Organization.verification_status.in_(["pending", "submitted"])
        ).order_by(Organization.created_at.desc()).limit(limit).offset(offset).all()
        
        return [
            {
                "id": str(org.id),
                "company_name": org.company_name,
                "website": org.website,
                "verification_status": org.verification_status,
                "business_license_url": org.business_license_url,
                "tax_id": org.tax_id,
                "created_at": org.created_at,
                "user_id": str(org.user_id)
            }
            for org in orgs
        ]
    
    # Notification helpers
    
    def _notify_admins_new_verification(self, org: Organization):
        """Notify admins about new verification request."""
        # Get all admin users
        admins = self.db.query(User).filter(
            User.role.in_(["admin", "super_admin"]),
            User.is_active == True
        ).all()
        
        for admin in admins:
            self.notification_service.create_notification(
                user_id=admin.id,
                notification_type=NotificationType.SYSTEM_ALERT,
                title="New Organization Verification Request",
                message=f"{org.company_name} has submitted verification documents for review.",
                priority=NotificationPriority.MEDIUM,
                action_url=f"/admin/organizations/pending-verification",
                action_text="Review Verification",
                send_email=True
            )
    
    def _notify_organization_submission_received(self, org: Organization):
        """Notify organization that submission was received."""
        user = self.db.query(User).filter(User.id == org.user_id).first()
        if user:
            self.notification_service.create_notification(
                user_id=user.id,
                notification_type=NotificationType.SYSTEM_ALERT,
                title="Verification Submitted",
                message="Your organization verification has been submitted and is under review. You'll be notified once the review is complete.",
                priority=NotificationPriority.MEDIUM,
                action_url="/organization/dashboard",
                action_text="View Dashboard",
                send_email=True
            )
    
    def _notify_organization_approved(self, org: Organization, notes: Optional[str]):
        """Notify organization that verification was approved."""
        user = self.db.query(User).filter(User.id == org.user_id).first()
        if user:
            message = "Congratulations! Your organization has been verified. You can now create and publish bug bounty programs."
            if notes:
                message += f"\n\nNotes: {notes}"
            
            self.notification_service.create_notification(
                user_id=user.id,
                notification_type=NotificationType.ACCOUNT_VERIFIED,
                title="Organization Verified",
                message=message,
                priority=NotificationPriority.HIGH,
                action_url="/organization/programs",
                action_text="Create Program",
                send_email=True
            )
    
    def _notify_organization_rejected(self, org: Organization, reason: str):
        """Notify organization that verification was rejected."""
        user = self.db.query(User).filter(User.id == org.user_id).first()
        if user:
            self.notification_service.create_notification(
                user_id=user.id,
                notification_type=NotificationType.SYSTEM_ALERT,
                title="Verification Rejected",
                message=f"Your organization verification was not approved. Reason: {reason}\n\nPlease update your information and resubmit.",
                priority=NotificationPriority.HIGH,
                action_url="/organization/dashboard",
                action_text="Update Information",
                send_email=True
            )
