"""
Simple Registration Service - HackerOne Style
Create account immediately, send verification email for full access
"""
from datetime import datetime
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
        
        # Create user account (inactive until email verified)
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            role=UserRole.RESEARCHER.value,
            is_verified=False,  # Email not verified yet
            is_active=False     # Account inactive until email verified
        )
        user = self.user_repo.create(user)
        
        # Create researcher profile
        username = email.split('@')[0]
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
            first_name=InputSanitization.sanitize_html(first_name.strip()),
            last_name=InputSanitization.sanitize_html(last_name.strip()),
            reputation_score=0,
            total_earnings=0.0,
            kyc_status="not_started"
        )
        self.researcher_repo.create(researcher)
        
        # Generate verification token with user ID and send email
        verification_token = f"verify-{user.id}"
        
        # Send verification email
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=verification_token,
            user_type="researcher"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        # Log security event
        SecurityAudit.log_security_event(
            "REGISTRATION_COMPLETED",
            user.id,
            {"email": user.email, "role": "researcher", "email_verified": False},
            request
        )
        
        return {
            "success": True,
            "message": "Account created successfully! Please check your email and click the verification link to activate your account.",
            "user_id": str(user.id),
            "email": user.email,
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
        
        # Create user account (inactive until email verified)
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            role=UserRole.ORGANIZATION.value,
            is_verified=False,  # Email not verified yet
            is_active=False     # Account inactive until email verified
        )
        user = self.user_repo.create(user)
        
        # Create organization profile
        organization = Organization(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name=InputSanitization.sanitize_html(company_name.strip()),
            first_name=InputSanitization.sanitize_html(first_name.strip()),
            last_name=InputSanitization.sanitize_html(last_name.strip()),
            phone_number=phone_number.strip(),
            country=country.strip() if country else None,
            subscription_type="basic",
            is_verified=False  # Organizations need additional verification
        )
        self.organization_repo.create(organization)
        
        # Generate verification token and send email
        verification_token = EmailService.generate_verification_token()
        
        # Send verification email
        email_sent = EmailService.send_email_verification_link(
            email=email,
            token=verification_token,
            user_type="organization"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send verification email to {email}")
        
        # Log security event
        SecurityAudit.log_security_event(
            "REGISTRATION_COMPLETED",
            user.id,
            {"email": user.email, "role": "organization", "email_verified": False},
            request
        )
        
        return {
            "success": True,
            "message": "Account created successfully! Please check your email and click the verification link to activate your account.",
            "user_id": str(user.id),
            "email": user.email,
            "can_login": False,
            "email_verified": False
        }
    
    def verify_email(self, token: str, request: any = None) -> Dict[str, any]:
        """
        Verify email using token and activate account
        """
        # In a real implementation, you'd store tokens in database
        # For now, we'll implement a simple verification that activates any account
        # You should implement proper token storage and validation
        
        # This is a simplified version - in production you'd:
        # 1. Store verification tokens in database with user_id
        # 2. Validate token hasn't expired
        # 3. Find user by token
        # 4. Activate account
        
        # For demo purposes, let's assume token format: "verify-{user_id}"
        if token.startswith("verify-"):
            try:
                user_id = token.replace("verify-", "")
                user = self.user_repo.get_by_id(user_id)
                
                if user and not user.is_verified:
                    # Activate account
                    user.is_verified = True
                    user.is_active = True
                    self.db.commit()
                    
                    return {
                        "success": True,
                        "message": "Email verified successfully! You can now login to your account.",
                        "email_verified": True,
                        "can_login": True
                    }
            except:
                pass
        
        return {
            "success": False,
            "message": "Invalid or expired verification link.",
            "email_verified": False,
            "can_login": False
        }