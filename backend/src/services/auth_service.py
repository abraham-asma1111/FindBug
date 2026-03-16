"""
Authentication Service - Business logic for user authentication
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import uuid

from src.core.security import (
    PasswordSecurity,
    TokenSecurity,
    AuthenticationSecurity,
    InputSanitization,
    SecurityAudit
)
from src.core.email_service import EmailService, BusinessEmailValidator
from src.core.ninja_service import NinjaEmailService, SkillsService
from src.domain.models.user import User, UserRole
from src.domain.models.researcher import Researcher
from src.domain.models.organization import Organization
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.researcher_repository import ResearcherRepository
from src.domain.repositories.organization_repository import OrganizationRepository


class AuthService:
    """Authentication service"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        researcher_repo: ResearcherRepository,
        organization_repo: OrganizationRepository
    ):
        self.user_repo = user_repo
        self.researcher_repo = researcher_repo
        self.organization_repo = organization_repo
    
    def register_researcher(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        username: str,
        bio: Optional[str] = None,
        website: Optional[str] = None,
        github: Optional[str] = None,
        twitter: Optional[str] = None,
        linkedin: Optional[str] = None,
        skills: Optional[list[str]] = None
    ) -> Dict[str, any]:
        """Register a new researcher - Bugcrowd 2026 Enhanced"""
        
        # Validate email format
        if not InputSanitization.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate password strength
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Validate username
        if not username or len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be 3-50 characters")
        
        # Check if username already exists
        existing_researcher = self.researcher_repo.get_by_username(username)
        if existing_researcher:
            raise ValueError("Username already taken")
        
        # Validate skills if provided
        if skills:
            skill_validation = SkillsService.validate_skills(skills)
            if not skill_validation["valid"]:
                raise ValueError(skill_validation["message"])
        
        # Sanitize inputs
        first_name = InputSanitization.sanitize_html(first_name.strip())
        last_name = InputSanitization.sanitize_html(last_name.strip())
        username = InputSanitization.sanitize_html(username.strip())
        
        if bio:
            bio = InputSanitization.sanitize_html(bio)
        if website and not InputSanitization.validate_url(website):
            raise ValueError("Invalid website URL")
        if linkedin and not InputSanitization.validate_url(linkedin):
            raise ValueError("Invalid LinkedIn URL")
        
        # Generate email verification token
        verification_token = EmailService.generate_verification_token()
        token_hash = EmailService.hash_token(verification_token)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            role=UserRole.RESEARCHER,
            is_verified=False,
            is_active=True,
            email_verification_token=token_hash,
            email_verification_token_expires=token_expires
        )
        user = self.user_repo.create(user)
        
        # Generate ninja email alias
        ninja_email = NinjaEmailService.generate_ninja_email(username, str(user.id))
        
        # Convert skills list to JSON string
        skills_json = None
        if skills:
            import json
            skills_json = json.dumps(skills)
        
        # Create researcher profile (Bugcrowd 2026 Enhanced)
        researcher = Researcher(
            id=uuid.uuid4(),
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            ninja_email=ninja_email,
            bio=bio,
            website=website,
            github=github,
            twitter=twitter,
            linkedin=linkedin,
            skills=skills_json,
            kyc_status="pending"
        )
        researcher = self.researcher_repo.create(researcher)
        
        # Send verification email
        EmailService.send_verification_email(email, verification_token, "researcher")
        
        return {
            "user_id": str(user.id),
            "researcher_id": str(researcher.id),
            "email": user.email,
            "username": username,
            "ninja_email": ninja_email,
            "message": "Registration successful. Please check your email to verify your account. MFA setup will be required after verification."
        }
    
    def register_organization(
        self,
        email: str,
        password: str,
        company_name: str,
        industry: Optional[str] = None,
        website: Optional[str] = None,
        subscription_type: Optional[str] = None,
        tax_id: Optional[str] = None,
        business_license_url: Optional[str] = None
    ) -> Dict[str, any]:
        """Register a new organization - Bugcrowd 2026 Enhanced"""
        
        # Validate email format
        if not InputSanitization.validate_email(email):
            raise ValueError("Invalid email format")
        
        # Validate business email (no personal emails like Gmail, Yahoo)
        is_business, error_msg = BusinessEmailValidator.is_business_email(email)
        if not is_business:
            raise ValueError(error_msg)
        
        # Validate password strength
        is_valid, error = PasswordSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Sanitize inputs
        company_name = InputSanitization.sanitize_html(company_name)
        if website and not InputSanitization.validate_url(website):
            raise ValueError("Invalid website URL")
        if business_license_url and not InputSanitization.validate_url(business_license_url):
            raise ValueError("Invalid business license URL")
        
        # Generate email verification token
        verification_token = EmailService.generate_verification_token()
        token_hash = EmailService.hash_token(verification_token)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            password_hash=PasswordSecurity.hash_password(password),
            role=UserRole.ORGANIZATION,
            is_verified=False,
            is_active=True,
            email_verification_token=token_hash,
            email_verification_token_expires=token_expires
        )
        user = self.user_repo.create(user)
        
        # Create organization profile (Bugcrowd 2026 Enhanced)
        organization = Organization(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name=company_name,
            industry=industry,
            website=website,
            subscription_type=subscription_type,
            tax_id=tax_id,
            business_license_url=business_license_url,
            verification_status="pending",
            domain_verified=False
        )
        organization = self.organization_repo.create(organization)
        
        # Send verification email
        EmailService.send_verification_email(email, verification_token, "organization")
        
        return {
            "user_id": str(user.id),
            "organization_id": str(organization.id),
            "email": user.email,
            "message": "Registration successful. Please check your email to verify your account. Domain verification will be required for full access."
        }
    
    def login(self, email: str, password: str, request: any = None) -> Dict[str, any]:
        """User login"""
        
        # Get user
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            # Log failed attempt
            if request:
                SecurityAudit.log_security_event(
                    "LOGIN_FAILURE",
                    None,
                    {"email": email, "reason": "user_not_found"},
                    request
                )
            raise ValueError("Invalid credentials")
        
        # Check if account is locked
        if user.is_locked:
            if user.locked_until and datetime.utcnow() < user.locked_until:
                remaining = (user.locked_until - datetime.utcnow()).seconds // 60
                raise ValueError(f"Account locked. Try again in {remaining} minutes.")
            else:
                # Unlock account
                user = self.user_repo.reset_failed_login(user)
        
        # Check if account is active
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Verify password
        if not PasswordSecurity.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user = self.user_repo.increment_failed_login(user)
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= AuthenticationSecurity.MAX_LOGIN_ATTEMPTS:
                locked_until = datetime.utcnow() + timedelta(
                    minutes=AuthenticationSecurity.LOCKOUT_DURATION_MINUTES
                )
                user = self.user_repo.lock_account(user, locked_until)
                
                # Log account lockout
                if request:
                    SecurityAudit.log_security_event(
                        "ACCOUNT_LOCKED",
                        str(user.id),
                        {"reason": "max_failed_attempts"},
                        request
                    )
                
                raise ValueError(
                    f"Account locked due to {AuthenticationSecurity.MAX_LOGIN_ATTEMPTS} "
                    f"failed login attempts. Try again in "
                    f"{AuthenticationSecurity.LOCKOUT_DURATION_MINUTES} minutes."
                )
            
            # Log failed attempt
            if request:
                SecurityAudit.log_security_event(
                    "LOGIN_FAILURE",
                    str(user.id),
                    {
                        "email": email,
                        "reason": "invalid_password",
                        "failed_attempts": user.failed_login_attempts
                    },
                    request
                )
            
            raise ValueError("Invalid credentials")
        
        # Reset failed login attempts
        if user.failed_login_attempts > 0:
            user = self.user_repo.reset_failed_login(user)
        
        # Update last login
        user = self.user_repo.update_last_login(user)
        
        # Generate JWT token
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "role": user.role.value
        }
        access_token = TokenSecurity.create_access_token(token_data)
        
        # Log successful login
        if request:
            SecurityAudit.log_security_event(
                "LOGIN_SUCCESS",
                str(user.id),
                {"email": user.email, "role": user.role.value},
                request
            )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value
        }

    def verify_email(self, token: str) -> Dict[str, any]:
        """Verify user email with token"""
        
        # Hash the token to compare with stored hash
        token_hash = EmailService.hash_token(token)
        
        # Find user with this token
        user = self.user_repo.get_by_verification_token(token_hash)
        if not user:
            raise ValueError("Invalid or expired verification token")
        
        # Check if token is expired
        if user.email_verification_token_expires and datetime.utcnow() > user.email_verification_token_expires:
            raise ValueError("Verification token has expired. Please request a new one.")
        
        # Check if already verified
        if user.is_verified:
            return {
                "message": "Email already verified",
                "email": user.email
            }
        
        # Mark as verified
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        user.email_verification_token = None
        user.email_verification_token_expires = None
        self.user_repo.update(user)
        
        return {
            "message": "Email verified successfully",
            "email": user.email
        }
    
    def resend_verification_email(self, email: str) -> Dict[str, any]:
        """Resend verification email"""
        
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            raise ValueError("User not found")
        
        if user.is_verified:
            raise ValueError("Email already verified")
        
        # Generate new token
        verification_token = EmailService.generate_verification_token()
        token_hash = EmailService.hash_token(verification_token)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user
        user.email_verification_token = token_hash
        user.email_verification_token_expires = token_expires
        self.user_repo.update(user)
        
        # Send email
        user_type = "researcher" if user.role == UserRole.RESEARCHER else "organization"
        EmailService.send_verification_email(email, verification_token, user_type)
        
        return {
            "message": "Verification email sent. Please check your inbox."
        }
    
    def enable_mfa(self, user_id: str) -> Dict[str, any]:
        """Enable MFA for user"""
        import pyotp
        import json
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.mfa_enabled:
            raise ValueError("MFA is already enabled")
        
        # Generate MFA secret
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [AuthenticationSecurity.generate_secure_token(8) for _ in range(10)]
        
        # Store in database (not enabled yet - user must verify first)
        user.mfa_secret = secret
        user.mfa_backup_codes = json.dumps(backup_codes)
        self.user_repo.update(user)
        
        # Generate QR code URI
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="Bug Bounty Platform"
        )
        
        return {
            "secret": secret,
            "qr_uri": qr_uri,
            "backup_codes": backup_codes,
            "message": "Scan the QR code with your authenticator app and verify to enable MFA"
        }
    
    def verify_mfa_setup(self, user_id: str, code: str) -> Dict[str, any]:
        """Verify MFA setup with code"""
        import pyotp
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.mfa_secret:
            raise ValueError("MFA not initialized. Please enable MFA first.")
        
        # Verify code
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(code, valid_window=1):
            raise ValueError("Invalid MFA code")
        
        # Enable MFA
        user.mfa_enabled = True
        self.user_repo.update(user)
        
        return {
            "message": "MFA enabled successfully",
            "mfa_enabled": True
        }
    
    def verify_mfa_login(self, user_id: str, code: str) -> bool:
        """Verify MFA code during login"""
        import pyotp
        import json
        
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.mfa_enabled:
            return False
        
        # Try TOTP code
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(code, valid_window=1):
            return True
        
        # Try backup codes
        if user.mfa_backup_codes:
            backup_codes = json.loads(user.mfa_backup_codes)
            if code in backup_codes:
                # Remove used backup code
                backup_codes.remove(code)
                user.mfa_backup_codes = json.dumps(backup_codes)
                self.user_repo.update(user)
                return True
        
        return False
    
    def disable_mfa(self, user_id: str, password: str) -> Dict[str, any]:
        """Disable MFA (requires password confirmation)"""
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not PasswordSecurity.verify_password(password, user.password_hash):
            raise ValueError("Invalid password")
        
        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        self.user_repo.update(user)
        
        return {
            "message": "MFA disabled successfully",
            "mfa_enabled": False
        }
