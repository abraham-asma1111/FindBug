"""
Simple Registration Service - HackerOne Style
Create account immediately, send verification email for full access
"""
from datetime import datetime, timedelta
from typing import Dict
import uuid

from sqlalchemy.orm import Session

from src.core.security import PasswordSecurity, InputSanitization, SecurityAudit
from src.core.email_service import EmailService, BusinessEmailValidator
from src.domain.models.user import User, UserRole
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.researcher_repository import ResearcherRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.core.logging import get_logger

logger = get_logger(__name__)


class SimpleRegistrationService:
    """
    Simple registration service - HackerOne style
    
    Flow:
    1. User submits registration form
    2. Create user account immediately (can login)
    3. Send verification email
    4. User clicks link to verify email
    5. Full access granted
    """
    
    def __init__(
        self,
        user_repo: UserRepository,
        researcher_repo: ResearcherRepository,
        organization_repo: OrganizationRepository,
        db: Session
    ):
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
        Register researcher - create account immediately, send verification email
        """
        # Validate inputs
        if not InputSanitization.validate_email(email):
            raise ValueError("Invalid email format")
        
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Store registration data temporarily - DO NOT create user yet
        # User will only be created after email verification
        
        # Check if email already exists in main users table
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Store in pending registrations table
        from src.domain.models.pending_registration import PendingRegistration
        
        # Remove any existing pending registration for this email
        existing_pending = self.db.query(PendingRegistration).filter(
            PendingRegistration.email == email.lower()
        ).first()
        if existing_pending:
            self.db.delete(existing_pending)
            self.db.commit()
        
        # Create pending registration
        pending_registration = PendingRegistration(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            first_name=InputSanitization.sanitize_html(first_name.strip()),
            last_name=InputSanitization.sanitize_html(last_name.strip()),
            role="researcher",
            verification_token=f"verify-{uuid.uuid4()}",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.db.add(pending_registration)
        self.db.commit()
        
        # Send verification email
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=pending_registration.verification_token,
            user_type="researcher"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        return {
            "success": True,
            "message": "Registration initiated! Please check your email and click the verification link to complete your account creation.",
            "user_id": str(pending_registration.id),  # Use pending registration ID
            "email": email,
            "can_login": False,
            "email_verified": False
        }
    
    def register_organization(
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
        Register organization - create account immediately, send verification email
        """
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
        
        # Store registration data temporarily - DO NOT create user yet
        # User will only be created after email verification
        
        # Check if email already exists in main users table
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Store in pending registrations table
        from src.domain.models.pending_registration import PendingRegistration
        
        # Remove any existing pending registration for this email
        existing_pending = self.db.query(PendingRegistration).filter(
            PendingRegistration.email == email.lower()
        ).first()
        if existing_pending:
            self.db.delete(existing_pending)
            self.db.commit()
        
        # Create pending registration
        pending_registration = PendingRegistration(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            first_name=InputSanitization.sanitize_html(first_name.strip()),
            last_name=InputSanitization.sanitize_html(last_name.strip()),
            role="organization",
            company_name=InputSanitization.sanitize_html(company_name.strip()),
            phone_number=phone_number.strip(),
            country=country.strip() if country else None,
            verification_token=f"verify-{uuid.uuid4()}",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.db.add(pending_registration)
        self.db.commit()
        
        # Send verification email
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=pending_registration.verification_token,
            user_type="organization"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        return {
            "success": True,
            "message": "Registration initiated! Please check your email and click the verification link to complete your account creation.",
            "user_id": str(pending_registration.id),  # Use pending registration ID
            "email": email,
            "can_login": False,
            "email_verified": False
        }
    
    def verify_email(self, token: str, request: any = None) -> Dict[str, any]:
        """
        Verify email using token and CREATE user account from pending registration
        """
        from src.domain.models.pending_registration import PendingRegistration

        # Find pending registration by token
        pending = self.db.query(PendingRegistration).filter(
            PendingRegistration.verification_token == token
        ).first()

        if not pending:
            raise ValueError("Invalid or expired verification link.")

        # Check if token has expired
        if pending.expires_at and datetime.utcnow() > pending.expires_at:
            # Clean up expired token
            self.db.delete(pending)
            self.db.commit()
            raise ValueError("Verification link has expired. Please register again.")

        # Check if user already exists (shouldn't happen, but safety check)
        existing_user = self.user_repo.get_by_email(pending.email)
        if existing_user:
            # Clean up pending registration
            self.db.delete(pending)
            self.db.commit()
            return {
                "success": True,
                "message": "Email already verified. You can login to your account.",
                "email_verified": True,
                "can_login": True
            }

        try:
            # NOW create the actual user account
            user = User(
                id=uuid.uuid4(),
                email=pending.email,
                password_hash=pending.password_hash,
                role=UserRole.RESEARCHER if pending.role == "researcher" else UserRole.ORGANIZATION,
                is_verified=True,   # Email is verified
                is_active=True      # Account is active
            )
            user = self.user_repo.create(user)

            # Create role-specific profile
            if pending.role == "researcher":
                # Create researcher profile
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
                    kyc_status="not_started"
                )
                self.researcher_repo.create(researcher)

            elif pending.role == "organization":
                # Create organization profile
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

            # Clean up pending registration
            self.db.delete(pending)
            self.db.commit()

            # Log security event
            SecurityAudit.log_security_event(
                "EMAIL_VERIFIED_USER_CREATED",
                user.id,
                {"email": user.email, "role": pending.role},
                request
            )

            return {
                "success": True,
                "message": "Email verified successfully! Your account has been created. You can now login.",
                "email_verified": True,
                "can_login": True
            }

        except Exception as e:
            # If user creation fails, keep the pending registration
            logger.error(f"Failed to create user from pending registration: {e}")
            raise ValueError("Account creation failed. Please try again or contact support.")

        return {
            "success": False,
            "message": "Invalid or expired verification link.",
            "email_verified": False,
            "can_login": False
        }
        
    def resend_verification_email(self, email: str, request: any = None) -> Dict[str, any]:
        """
        Resend verification email for unverified user
        """
        # Find user by email
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Email not found")
        
        # Check if already verified
        if user.is_verified:
            return {
                "success": True,
                "message": "Email is already verified. You can login to your account."
            }
        
        # Generate new verification token
        verification_token = f"verify-{user.id}"
        
        # Determine user type
        user_type = "researcher" if user.role.value == "researcher" else "organization"
        
        # Send verification email
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=verification_token,
            user_type=user_type
        )
        
        if not email_sent:
            logger.warning(f"Failed to resend verification email to {email}")
            raise ValueError("Failed to send verification email. Please try again.")
        
        # Log security event
        SecurityAudit.log_security_event(
            "VERIFICATION_EMAIL_RESENT",
            user.id,
            {"email": user.email, "role": user_type},
            request
        )
        
        return {
            "success": True,
            "message": "Verification email sent! Please check your inbox and click the verification link."
        }