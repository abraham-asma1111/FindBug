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
            
            # Send notification to user about KYC submission
            from src.services.notification_service import NotificationService
            
            notification_service = NotificationService(self.db)
            notification_data = {
                "title": "KYC Documents Submitted",
                "message": "Your KYC documents have been submitted successfully. Pending admin review.",
                "type": "kyc_update"
            }
            
            notification_service.create_notification(
                user_id=user_id,
                notification_type="KYC_SUBMITTED",
                data=notification_data
            )
            
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
        
        # Send notification to user about KYC status
        from src.services.notification_service import NotificationService
        
        notification_service = NotificationService(self.db)
        notification_data = {
            "title": "KYC Verification Update",
            "message": f"Your KYC verification has been {kyc.status}.",
            "type": "kyc_update"
        }
        
        if approved:
            notification_service.create_notification(
                user_id=str(kyc.user_id),
                notification_type="KYC_APPROVED",
                data=notification_data
            )
        else:
            notification_service.create_notification(
                user_id=str(kyc.user_id),
                notification_type="KYC_REJECTED",
                data=notification_data
            )
        
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
 


    # ============================================
    # PERSONA INTEGRATION METHODS
    # ============================================
    
    async def start_persona_verification(
        self,
        user_id: UUID,
        user_role: str
    ) -> Dict:
        """
        Initialize Persona verification flow.
        
        Args:
            user_id: User ID
            user_role: User role (researcher, organization)
            
        Returns:
            Dict with inquiry_id and template_id
        """
        import httpx
        import os
        
        logger.info(f"start_persona_verification called for user {user_id}, role: {user_role}")
        
        # Get Persona configuration
        api_key = os.getenv("PERSONA_API_KEY")
        environment = os.getenv("PERSONA_ENVIRONMENT", "sandbox")
        
        # Normalize role to lowercase for comparison
        normalized_role = user_role.lower()
        
        # Select template based on role
        if normalized_role == "researcher":
            template_id = os.getenv("PERSONA_TEMPLATE_RESEARCHER")
        elif normalized_role == "organization":
            template_id = os.getenv("PERSONA_TEMPLATE_ORGANIZATION")
        else:
            raise ValueError(f"Invalid role for KYC: {user_role}")
        
        if not api_key or not template_id:
            raise ValueError("Persona configuration missing in environment")
        
        # Check if user already has pending verification
        existing = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id,
            KYCVerification.persona_status.in_(['created', 'pending'])
        ).first()
        
        if existing:
            logger.info(f"Found existing KYC record for user {user_id}: inquiry_id={existing.persona_inquiry_id}")
            return {
                "inquiry_id": existing.persona_inquiry_id,
                "template_id": existing.persona_template_id,
                "status": "existing"
            }
        
        logger.info(f"No existing KYC found, creating new Persona inquiry for user {user_id}")
        
        # Create inquiry via Persona API with timeout
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
                response = await client.post(
                    f"https://withpersona.com/api/v1/inquiries",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "Persona-Version": "2023-01-05"
                    },
                    json={
                        "data": {
                            "attributes": {
                                "inquiry-template-id": template_id,
                                "reference-id": str(user_id),
                                "environment": environment
                            }
                        }
                    }
                )
            
            # Check response status
            if response.status_code != 201:
                logger.error(f"Persona API error: {response.text}")
                raise Exception(f"Failed to create Persona inquiry: {response.status_code}")
            
            # Extract inquiry ID
            data = response.json()
            inquiry_id = data["data"]["id"]
            
        except httpx.ConnectTimeout:
            logger.error("Persona API connection timeout")
            raise Exception("Unable to connect to Persona verification service. Please try again later.")
        except httpx.ReadTimeout:
            logger.error("Persona API read timeout")
            raise Exception("Persona verification service is taking too long to respond. Please try again later.")
        except httpx.NetworkError as e:
            logger.error(f"Persona API network error: {str(e)}")
            raise Exception("Network error connecting to Persona. Please check your internet connection.")
        except Exception as e:
            # Re-raise if it's already our custom exception
            if "Unable to connect" in str(e) or "taking too long" in str(e) or "Network error" in str(e) or "Failed to create" in str(e):
                raise
            # Otherwise wrap it
            logger.error(f"Unexpected error creating Persona inquiry: {str(e)}")
            raise Exception(f"Failed to initialize Persona verification: {str(e)}")
        
        # Create KYC record
        kyc = KYCVerification(
            user_id=user_id,
            status="pending",
            persona_inquiry_id=inquiry_id,
            persona_template_id=template_id,
            persona_status="created"
        )
        
        self.db.add(kyc)
        self.db.commit()
        self.db.refresh(kyc)
        
        logger.info(f"Created Persona inquiry {inquiry_id} for user {user_id}, KYC ID: {kyc.id}")
        
        return {
            "inquiry_id": inquiry_id,
            "template_id": template_id,
            "status": "created",
            "kyc_id": str(kyc.id)  # Include KYC ID for debugging
        }
    
    async def verify_persona_inquiry(
        self,
        inquiry_id: str
    ) -> Dict:
        """
        Verify inquiry status with Persona API (server-side validation).
        
        Args:
            inquiry_id: Persona inquiry ID
            
        Returns:
            Dict with verification status
        """
        import httpx
        import os
        
        api_key = os.getenv("PERSONA_API_KEY")
        
        if not api_key:
            raise ValueError("Persona API key missing")
        
        # Fetch inquiry from Persona with timeout
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
                response = await client.get(
                    f"https://withpersona.com/api/v1/inquiries/{inquiry_id}",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Persona-Version": "2023-01-05"
                    }
                )
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"Persona API error: {response.text}")
                raise Exception(f"Failed to fetch inquiry: {response.status_code}")
            
            # Extract inquiry data
            data = response.json()
            inquiry_data = data["data"]
            attributes = inquiry_data["attributes"]
            
            status = attributes.get("status")
            reference_id = attributes.get("reference-id")
            
        except httpx.ConnectTimeout:
            logger.error("Persona API connection timeout during verification")
            raise Exception("Unable to connect to Persona verification service. Please try again later.")
        except httpx.ReadTimeout:
            logger.error("Persona API read timeout during verification")
            raise Exception("Persona verification service is taking too long to respond. Please try again later.")
        except httpx.NetworkError as e:
            logger.error(f"Persona API network error during verification: {str(e)}")
            raise Exception("Network error connecting to Persona. Please check your internet connection.")
        except Exception as e:
            # Re-raise if it's already our custom exception
            if "Unable to connect" in str(e) or "taking too long" in str(e) or "Network error" in str(e) or "Failed to fetch" in str(e):
                raise
            # Otherwise wrap it
            logger.error(f"Unexpected error verifying Persona inquiry: {str(e)}")
            raise Exception(f"Failed to verify Persona inquiry: {str(e)}")
        
        # Find KYC record
        logger.info(f"Looking for KYC record with inquiry_id: {inquiry_id}")
        
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.persona_inquiry_id == inquiry_id
        ).first()
        
        if not kyc:
            # Debug: Check all KYC records for this user
            all_kyc = self.db.query(KYCVerification).all()
            logger.error(f"KYC record not found for inquiry {inquiry_id}. Total KYC records in DB: {len(all_kyc)}")
            for k in all_kyc:
                logger.error(f"  - KYC ID: {k.id}, User: {k.user_id}, Inquiry: {k.persona_inquiry_id}")
            raise NotFoundException(f"KYC record not found for inquiry {inquiry_id}")
        
        logger.info(f"Found KYC record {kyc.id} for inquiry {inquiry_id}")
        
        # Update KYC status based on Persona status
        kyc.persona_status = status
        
        # Persona can return "approved" or "completed" for successful verification
        if status in ["completed", "approved"]:
            kyc.status = "approved"
            kyc.verified_at = datetime.utcnow()
            kyc.persona_verified_at = datetime.utcnow()
            kyc.expires_at = datetime.utcnow() + timedelta(days=self.expiration_days)
            logger.info(f"KYC approved for user {kyc.user_id} via Persona (status: {status})")
        elif status == "failed":
            kyc.status = "rejected"
            kyc.rejection_reason = "Persona verification failed"
            logger.info(f"KYC rejected for user {kyc.user_id} via Persona")
        
        self.db.commit()
        self.db.refresh(kyc)
        
        return {
            "inquiry_id": inquiry_id,
            "status": status,
            "kyc_status": kyc.status,
            "user_id": str(kyc.user_id)
        }
    
    async def handle_persona_webhook(
        self,
        payload: Dict,
        signature: str
    ) -> Dict:
        """
        Handle Persona webhook events.
        
        Args:
            payload: Webhook payload
            signature: Webhook signature for verification
            
        Returns:
            Dict with processing result
        """
        import hmac
        import hashlib
        import os
        
        # Verify webhook signature
        webhook_secret = os.getenv("PERSONA_WEBHOOK_SECRET")
        
        if webhook_secret:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                str(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                raise ForbiddenException("Invalid webhook signature")
        
        # Extract event data
        event_type = payload.get("type")
        inquiry_id = payload.get("data", {}).get("id")
        
        if not inquiry_id:
            logger.warning("Webhook received without inquiry_id")
            return {"status": "ignored"}
        
        # Process based on event type
        if event_type == "inquiry.completed":
            await self.verify_persona_inquiry(inquiry_id)
            return {"status": "processed", "event": "completed"}
        elif event_type == "inquiry.failed":
            await self.verify_persona_inquiry(inquiry_id)
            return {"status": "processed", "event": "failed"}
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
            return {"status": "ignored", "event": event_type}

    # ============================================
    # EMAIL VERIFICATION METHODS (replaces SMS)
    # ============================================
    
    async def send_email_verification(
        self,
        user_id: UUID,
        email_address: str
    ) -> Dict:
        """
        Send EMAIL verification code (replaces SMS).
        
        SECURITY: User can ONLY verify the email from their account registration.
        This prevents email hijacking attacks.
        
        Args:
            user_id: User ID
            email_address: Email address to verify (must match user's registered email)
            
        Returns:
            Dict with send status
        """
        from src.core.email_service import EmailService
        
        # CRITICAL SECURITY CHECK: Get the user's registered email
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User not found")
        
        # CRITICAL: User can ONLY verify their own registered email
        # This prevents email hijacking where user A tries to verify user B's email
        if email_address.lower() != user.email.lower():
            raise ForbiddenException(
                f"You can only verify your registered email address ({user.email}). "
                f"To change your email, please update your account settings first."
            )
        
        # Get or create KYC record
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id
        ).first()
        
        if not kyc:
            # Create KYC record for email verification only
            kyc = KYCVerification(
                user_id=user_id,
                status="pending"
            )
            self.db.add(kyc)
            self.db.commit()
            self.db.refresh(kyc)
        
        # CRITICAL: Validate email format FIRST before any other checks
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email_address):
            raise ValueError("Invalid email address format")
        
        # Check if already verified (AFTER format validation)
        if kyc.email_verified:
            raise ConflictException("Email already verified")
        
        # Check rate limiting (max 3 attempts per hour)
        if kyc.email_verification_attempts >= 3:
            if kyc.email_verification_code_expires:
                time_since_last = datetime.utcnow() - kyc.email_verification_code_expires
                if time_since_last < timedelta(hours=1):
                    raise ValueError("Too many verification attempts. Please try again later.")
                else:
                    # Reset attempts after 1 hour
                    kyc.email_verification_attempts = 0
        
        # Generate 6-digit verification code
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Get user info for personalization
        user = self.db.query(User).filter(User.id == user_id).first()
        user_name = "User"
        if user:
            from src.domain.models.researcher import Researcher
            researcher = self.db.query(Researcher).filter(Researcher.user_id == user_id).first()
            if researcher and researcher.first_name:
                user_name = researcher.first_name
        
        # Send email with verification code
        try:
            email_sent = EmailService.send_kyc_verification_code(
                email=email_address,
                code=code,
                user_name=user_name
            )
            
            if not email_sent:
                raise Exception("Failed to send verification email")
                
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise Exception(f"Failed to send verification email: {str(e)}")
        
        # Store verification code (hashed for security)
        import hashlib
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        kyc.email_address = email_address
        kyc.email_verification_code = code_hash
        kyc.email_verification_code_expires = datetime.utcnow() + timedelta(minutes=10)
        kyc.email_verification_attempts += 1
        
        self.db.commit()
        
        logger.info(f"Email verification code sent to {email_address} for user {user_id}")
        
        return {
            "success": True,
            "email_address": email_address,
            "expires_in_minutes": 10,
            "message": "Verification code sent to your email"
        }
    
    async def verify_email_code(
        self,
        user_id: UUID,
        code: str
    ) -> Dict:
        """
        Verify EMAIL code entered by user (replaces SMS).
        
        INDEPENDENT: Works without Persona KYC.
        
        Args:
            user_id: User ID
            code: Verification code from email
            
        Returns:
            Dict with verification status
        """
        # Get KYC record
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id
        ).first()
        
        if not kyc:
            raise NotFoundException("KYC record not found")
        
        # Check if email is already verified
        if kyc.email_verified:
            return {
                "success": True,
                "message": "Email already verified",
                "email_address": kyc.email_address
            }
        
        # Check if verification code exists
        if not kyc.email_verification_code:
            raise ValueError("No verification code found. Please request a new code.")
        
        # Check if code is expired
        if kyc.email_verification_code_expires and datetime.utcnow() > kyc.email_verification_code_expires:
            raise ValueError("Verification code expired. Please request a new code.")
        
        # Verify code
        import hashlib
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash != kyc.email_verification_code:
            raise ValueError("Invalid verification code")
        
        # Mark email as verified
        kyc.email_verified = True
        kyc.email_verified_at = datetime.utcnow()
        kyc.email_verification_code = None
        kyc.email_verification_code_expires = None
        kyc.email_verification_attempts = 0
        
        # Update KYC status only if not already set
        if not kyc.status or kyc.status == "pending":
            kyc.status = "approved"
        
        self.db.commit()
        
        logger.info(f"Email verified for user {user_id}: {kyc.email_address}")
        
        return {
            "success": True,
            "message": "Email address verified successfully",
            "email_address": kyc.email_address,
            "verified_at": kyc.email_verified_at.isoformat()
        }
    
    def get_email_verification_status(self, user_id: UUID) -> Dict:
        """
        Get email verification status for user (replaces phone/SMS).
        
        INDEPENDENT: Returns email status regardless of Persona.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with email verification status
        """
        kyc = self.db.query(KYCVerification).filter(
            KYCVerification.user_id == user_id
        ).first()
        
        if not kyc:
            return {
                "email_verified": False,
                "email_address": None,
                "can_verify_email": True  # Always allow email verification
            }
        
        # CRITICAL: Ensure email_verified is always a boolean, never None
        email_verified = bool(kyc.email_verified) if kyc.email_verified is not None else False
        
        return {
            "email_verified": email_verified,
            "email_address": kyc.email_address,
            "email_verified_at": kyc.email_verified_at.isoformat() if kyc.email_verified_at else None,
            "can_verify_email": not email_verified  # Can verify if not already verified
        }
