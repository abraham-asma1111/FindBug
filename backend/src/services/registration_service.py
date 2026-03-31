"""
Registration Service - Handle email-first registration with OTP verification
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid

from sqlalchemy.orm import Session

from src.core.security import PasswordSecurity, InputSanitization, SecurityAudit
from src.core.email_service import EmailService, BusinessEmailValidator
from src.domain.models.pending_registration import PendingRegistration, RegistrationType
from src.domain.models.user import User, UserRole
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.repositories.pending_registration_repository import PendingRegistrationRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.researcher_repository import ResearcherRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.core.logging import get_logger

logger = get_logger(__name__)


class RegistrationService:
    """
    Registration service with email-first verification flow.
    
    Flow:
    1. User submits registration form
    2. Validate data and check if email exists
    3. Store registration data in pending_registrations table
    4. Send verification email with OTP + backup link
    5. User enters OTP or clicks link
    6. Create actual user account
    7. Clean up pending registration
    """
    
    def __init__(
        self,
        pending_repo: PendingRegistrationRepository,
        user_repo: UserRepository,
        researcher_repo: ResearcherRepository,
        organization_repo: OrganizationRepository,
        db: Session
    ):
        self.pending_repo = pending_repo
        self.user_repo = user_repo
        self.researcher_repo = researcher_repo
        self.organization_repo = organization_repo
        self.db = db
    
    def register_researcher(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        request: any = None
    ) -> Dict[str, any]:
        """
        Register researcher - send verification email before account activation
        """
        # Extract request info
        ip_address = None
        user_agent = None
        if request:
            ip_address = getattr(request.client, 'host', None)
            user_agent = request.headers.get('user-agent', '')
        
        # Validate inputs
        if not InputSanitization.validate_email(email):
            raise ValueError("Invalid email format")
        
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if email already exists in users table
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if there's already a pending registration
        existing_pending = self.pending_repo.get_by_email(email)
        if existing_pending and not existing_pending.is_expired:
            # Update existing pending registration
            pending_registration = existing_pending
            pending_registration.password_hash = PasswordSecurity.hash_password(password)
            pending_registration.first_name = InputSanitization.sanitize_html(first_name.strip())
            pending_registration.last_name = InputSanitization.sanitize_html(last_name.strip())
            pending_registration.created_at = datetime.utcnow()
            pending_registration.expires_at = datetime.utcnow() + timedelta(hours=24)
            pending_registration.is_verified = False
            pending_registration.verified_at = None
        else:
            # Delete expired pending registration if exists
            if existing_pending:
                self.pending_repo.delete(existing_pending.id)
            
            # Create new pending registration
            pending_registration = PendingRegistration(
                email=email.lower(),
                password_hash=PasswordSecurity.hash_password(password),
                registration_type=RegistrationType.RESEARCHER,
                first_name=InputSanitization.sanitize_html(first_name.strip()),
                last_name=InputSanitization.sanitize_html(last_name.strip()),
                verification_token=EmailService.generate_verification_token(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            pending_registration = self.pending_repo.create(pending_registration)
        
        # Send verification email with link (no OTP)
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=pending_registration.verification_token,
            user_type="researcher"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        # Log security event
        SecurityAudit.log_security_event(
            "REGISTRATION_INITIATED",
            None,
            {"email": email, "role": "researcher", "method": "email_link"},
            request
        )
        
        return {
            "success": True,
            "message": "Registration initiated. Please check your email and click the verification link.",
            "email": email,
            "verification_method": "email_link",
            "expires_in_hours": 24
        }
    
    def initiate_organization_registration(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        company_name: str,
        phone_number: str,
        country: str = None,
        request: any = None
    ) -> Dict[str, any]:
        """
        Initiate organization registration - send verification email first
        """
        # Extract request info
        ip_address = None
        user_agent = None
        if request:
            ip_address = getattr(request.client, 'host', None)
            user_agent = request.headers.get('user-agent', '')
        
        # Validate inputs
        if not InputSanitization.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate business email for organizations
        is_business, error = BusinessEmailValidator.is_business_email(email)
        if not is_business:
            raise ValueError(error)
        
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        if len(company_name.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if there's already a pending registration
        existing_pending = self.pending_repo.get_by_email(email)
        if existing_pending and not existing_pending.is_expired:
            # Update existing pending registration
            pending_registration = existing_pending
            pending_registration.password_hash = PasswordSecurity.hash_password(password)
            pending_registration.first_name = InputSanitization.sanitize_html(first_name.strip())
            pending_registration.last_name = InputSanitization.sanitize_html(last_name.strip())
            pending_registration.company_name = InputSanitization.sanitize_html(company_name.strip())
            pending_registration.phone_number = phone_number.strip()
            pending_registration.country = country.strip() if country else None
            pending_registration.created_at = datetime.utcnow()
            pending_registration.expires_at = datetime.utcnow() + timedelta(hours=24)
            pending_registration.is_verified = False
            pending_registration.verified_at = None
        else:
            # Delete expired pending registration if exists
            if existing_pending:
                self.pending_repo.delete(existing_pending.id)
            
            # Create new pending registration
            pending_registration = PendingRegistration(
                email=email.lower(),
                password_hash=PasswordSecurity.hash_password(password),
                registration_type=RegistrationType.ORGANIZATION,
                first_name=InputSanitization.sanitize_html(first_name.strip()),
                last_name=InputSanitization.sanitize_html(last_name.strip()),
                company_name=InputSanitization.sanitize_html(company_name.strip()),
                phone_number=phone_number.strip(),
                country=country.strip() if country else None,
                verification_token=EmailService.generate_verification_token(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            pending_registration = self.pending_repo.create(pending_registration)
        
        # Send verification email with link (no OTP)
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=pending_registration.verification_token,
            user_type="organization"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        # Log security event
        SecurityAudit.log_security_event(
            "REGISTRATION_INITIATED",
            None,
            {"email": email, "role": "organization", "method": "otp"},
            request
        )
        
        return {
            "success": True,
            "message": "Registration successful! Please check your email and click the verification link to activate your account.",
            "email": email
        }
    
    def verify_registration_otp(
        self,
        email: str,
        otp: str,
        request: any = None
    ) -> Dict[str, any]:
        """
        Verify registration using OTP and create user account
        
        Args:
            email: User email
            otp: 6-digit OTP code
            request: HTTP request object
            
        Returns:
            Dict with verification result and user data
        """
        # Find pending registration
        pending = self.pending_repo.get_by_otp(email, otp)
        if not pending:
            raise ValueError("Invalid or expired verification code")
        
        if pending.is_expired:
            raise ValueError("Registration has expired. Please register again.")
        
        if pending.otp_is_expired:
            raise ValueError("Verification code has expired. Please request a new one.")
        
        # Create user account
        user_data = self._create_user_from_pending(pending, request)
        
        # Mark as verified and delete pending registration
        self.pending_repo.delete(pending.id)
        
        return user_data
    
    def verify_registration_token(
        self,
        token: str,
        request: any = None
    ) -> Dict[str, any]:
        """
        Verify registration using token (backup method) and create user account
        """
        # Find pending registration
        pending = self.pending_repo.get_by_token(token)
        if not pending:
            raise ValueError("Invalid or expired verification link")
        
        if pending.is_expired:
            raise ValueError("Registration has expired. Please register again.")
        
        # Create user account
        user_data = self._create_user_from_pending(pending, request)
        
        # Delete pending registration
        self.pending_repo.delete(pending.id)
        
        return user_data
    
    def resend_verification_otp(
        self,
        email: str,
        request: any = None
    ) -> Dict[str, any]:
        """
        Resend verification OTP for pending registration
        """
        # Find pending registration
        pending = self.pending_repo.get_by_email(email)
        if not pending:
            raise ValueError("No pending registration found for this email")
        
        if pending.is_expired:
            raise ValueError("Registration has expired. Please register again.")
        
        # Generate new OTP
        otp = EmailService.generate_otp()
        pending.verification_otp = otp
        pending.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
        self.db.commit()
        
        # Send verification email
        email_sent = EmailService.send_registration_verification_email(
            email=email,
            otp=otp,
            token=pending.verification_token,
            user_type=pending.registration_type.value
        )
        
        if not email_sent:
            logger.warning(f"Failed to resend verification email to {email}")
        
        return {
            "success": True,
            "message": "Verification code sent. Please check your email.",
            "expires_in_minutes": 10
        }
    
    def _create_user_from_pending(
        self,
        pending: PendingRegistration,
        request: any = None
    ) -> Dict[str, any]:
        """
        Create user account from pending registration data
        """
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=pending.email,
            password_hash=pending.password_hash,
            role=UserRole.RESEARCHER if pending.registration_type == RegistrationType.RESEARCHER else UserRole.ORGANIZATION,
            is_verified=True,  # Already verified via OTP
            is_active=True
        )
        user = self.user_repo.create(user)
        
        # Create profile based on type
        if pending.registration_type == RegistrationType.RESEARCHER:
            # Auto-generate username from email
            username = pending.email.split('@')[0]
            username = ''.join(c for c in username if c.isalnum() or c in '_-')
            if len(username) < 3:
                username = username + str(uuid.uuid4())[:4]
            if len(username) > 50:
                username = username[:50]
            
            # Ensure unique username
            existing_researcher = self.researcher_repo.get_by_username(username)
            if existing_researcher:
                username = username[:45] + str(uuid.uuid4())[:5]
            
            researcher = Researcher(
                id=uuid.uuid4(),
                user_id=user.id,
                username=username,
                first_name=pending.first_name,
                last_name=pending.last_name,
                reputation_score=0,
                total_bounties_earned=0.0,
                kyc_status="not_started"
            )
            self.researcher_repo.create(researcher)
            
        else:  # Organization
            organization = Organization(
                id=uuid.uuid4(),
                user_id=user.id,
                company_name=pending.company_name,
                first_name=pending.first_name,
                last_name=pending.last_name,
                phone_number=pending.phone_number,
                country=pending.country,
                subscription_type="basic",
                is_verified=False  # Organizations need additional verification
            )
            self.organization_repo.create(organization)
        
        # Log security event
        SecurityAudit.log_security_event(
            "REGISTRATION_COMPLETED",
            user.id,
            {"email": user.email, "role": user.role.value, "method": "otp_verification"},
            request
        )
        
        return {
            "success": True,
            "message": "Registration completed successfully. You can now log in.",
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified
        }
    
    def cleanup_expired_registrations(self) -> int:
        """
        Clean up expired pending registrations
        
        Returns:
            Number of cleaned up registrations
        """
        return self.pending_repo.cleanup_expired()