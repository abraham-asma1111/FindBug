"""
Authentication Service - Business logic for user authentication
Enhanced with SecurityEvent and LoginHistory integration (FREQ-02, FREQ-17)
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import uuid

from sqlalchemy.orm import Session

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
from src.domain.models.security_log import SecurityEvent, LoginHistory
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.researcher_repository import ResearcherRepository
from src.domain.repositories.organization_repository import OrganizationRepository
from src.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Authentication service with comprehensive security logging.
    
    Features:
    - User registration (researcher, organization)
    - Login with MFA support
    - Email verification
    - Password reset
    - SecurityEvent logging for suspicious activity
    - LoginHistory tracking for all login attempts
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
    
    # ═══════════════════════════════════════════════════════════════════════
    # SECURITY LOGGING HELPERS
    # ═══════════════════════════════════════════════════════════════════════
    
    def _log_security_event(
        self,
        event_type: str,
        user_id: Optional[uuid.UUID],
        description: str,
        severity: str = "medium",
        ip_address: Optional[str] = None,
        is_blocked: bool = False
    ) -> SecurityEvent:
        """
        Log security event.
        
        Args:
            event_type: Event type (brute_force, account_lockout, etc.)
            user_id: User ID (optional)
            description: Event description
            severity: Severity level (low, medium, high, critical)
            ip_address: IP address (optional)
            is_blocked: Whether action was blocked
            
        Returns:
            SecurityEvent
        """
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            is_blocked=is_blocked
        )
        
        self.db.add(event)
        self.db.commit()
        
        logger.info(f"Security event logged: {event_type}", extra={
            "user_id": str(user_id) if user_id else None,
            "severity": severity,
            "event_type": event_type
        })
        
        return event
    
    def _log_login_attempt(
        self,
        user_id: uuid.UUID,
        is_successful: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        mfa_used: bool = False
    ) -> LoginHistory:
        """
        Log login attempt.
        
        Args:
            user_id: User ID
            is_successful: Whether login was successful
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
            failure_reason: Failure reason if unsuccessful
            mfa_used: Whether MFA was used
            
        Returns:
            LoginHistory
        """
        login_record = LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_successful=is_successful,
            failure_reason=failure_reason,
            mfa_used=mfa_used
        )
        
        self.db.add(login_record)
        self.db.commit()
        
        logger.info(f"Login attempt logged: {'success' if is_successful else 'failure'}", extra={
            "user_id": str(user_id),
            "is_successful": is_successful,
            "failure_reason": failure_reason
        })
        
        return login_record
    
    def _extract_request_info(self, request: any) -> tuple[Optional[str], Optional[str]]:
        """
        Extract IP address and user agent from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (ip_address, user_agent)
        """
        if not request:
            return None, None
        
        # Extract IP address
        ip_address = None
        if hasattr(request, 'client') and request.client:
            ip_address = request.client.host
        
        # Extract user agent
        user_agent = None
        if hasattr(request, 'headers'):
            user_agent = request.headers.get('user-agent')
        
        return ip_address, user_agent
    
    # ═══════════════════════════════════════════════════════════════════════
    # REGISTRATION METHODS
    # ═══════════════════════════════════════════════════════════════════════
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
        Register a new researcher - matches frontend form.
        Enhanced with security event logging.
        Username auto-generated from email.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
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
        
        # Auto-generate username from email
        username = email.split('@')[0]
        # Clean username
        username = ''.join(c for c in username if c.isalnum() or c in '_-')
        # Ensure minimum length
        if len(username) < 3:
            username = username + str(uuid.uuid4())[:4]
        # Ensure maximum length
        if len(username) > 50:
            username = username[:50]
        
        # Check if username already exists, if so append random suffix
        existing_researcher = self.researcher_repo.get_by_username(username)
        if existing_researcher:
            username = username[:45] + str(uuid.uuid4())[:5]
        
        # Sanitize inputs
        first_name = InputSanitization.sanitize_html(first_name.strip())
        last_name = InputSanitization.sanitize_html(last_name.strip())
        username = InputSanitization.sanitize_html(username.strip())
        
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
        
        # Create researcher profile
        researcher = Researcher(
            id=uuid.uuid4(),
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            ninja_email=ninja_email,
            kyc_status="pending"
        )
        researcher = self.researcher_repo.create(researcher)
        
        # Send verification email
        EmailService.send_verification_email(email, verification_token, "researcher")
        
        # Log user registration security event
        self._log_security_event(
            event_type="user_registration",
            user_id=user.id,
            description=f"New researcher registered: {username}",
            severity="low",
            ip_address=ip_address
        )
        
        logger.info("Researcher registered successfully", extra={
            "user_id": str(user.id),
            "username": username,
            "email": email
        })
        
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
        first_name: str,
        last_name: str,
        company_name: str,
        phone_number: Optional[str] = None,
        request: any = None
    ) -> Dict[str, any]:
        """
        Register a new organization - matches frontend form.
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
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
        first_name = InputSanitization.sanitize_html(first_name.strip())
        last_name = InputSanitization.sanitize_html(last_name.strip())
        company_name = InputSanitization.sanitize_html(company_name)
        if phone_number:
            phone_number = InputSanitization.sanitize_html(phone_number.strip())
        
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
        
        # Create organization profile
        organization = Organization(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name=company_name,
            verification_status="pending",
            domain_verified=False
        )
        organization = self.organization_repo.create(organization)
        
        # Send verification email
        EmailService.send_verification_email(email, verification_token, "organization")
        
        # Log organization registration security event
        phone_info = f", Phone: {phone_number}" if phone_number else ""
        self._log_security_event(
            event_type="user_registration",
            user_id=user.id,
            description=f"New organization registered: {company_name} (Contact: {first_name} {last_name}{phone_info})",
            severity="low",
            ip_address=ip_address
        )
        
        logger.info("Organization registered successfully", extra={
            "user_id": str(user.id),
            "company_name": company_name,
            "email": email,
            "contact_name": f"{first_name} {last_name}",
            "phone_number": phone_number or "not provided"
        })
        
        return {
            "user_id": str(user.id),
            "organization_id": str(organization.id),
            "email": user.email,
            "message": "Registration successful. Please check your email to verify your account. Domain verification will be required for full access."
        }
    
    def login(self, email: str, password: str, mfa_code: Optional[str] = None, request: any = None) -> Dict[str, any]:
        """
        User login with optional MFA verification.
        Enhanced with SecurityEvent and LoginHistory logging.
        """
        
        # Extract request info
        ip_address, user_agent = self._extract_request_info(request)
        
        # Get user
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            # Log security event for non-existent user
            self._log_security_event(
                event_type="login_attempt_unknown_user",
                user_id=None,
                description=f"Login attempt for non-existent email: {email}",
                severity="low",
                ip_address=ip_address,
                is_blocked=False
            )
            
            # Log failed attempt via SecurityAudit (for backward compatibility)
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
                
                # Log login attempt for locked account
                self._log_login_attempt(
                    user_id=user.id,
                    is_successful=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="account_locked"
                )
                
                raise ValueError(f"Account locked. Try again in {remaining} minutes.")
            else:
                # Unlock account
                user = self.user_repo.reset_failed_login(user)
        
        # Check if account is active
        if not user.is_active:
            # Log login attempt for inactive account
            self._log_login_attempt(
                user_id=user.id,
                is_successful=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="account_inactive"
            )
            raise ValueError("Account is inactive")
        
        # Verify password
        if not PasswordSecurity.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user = self.user_repo.increment_failed_login(user)
            
            # Log failed login attempt
            self._log_login_attempt(
                user_id=user.id,
                is_successful=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="invalid_password"
            )
            
            # Lock account if max attempts reached
            if user.failed_login_attempts and user.failed_login_attempts >= AuthenticationSecurity.MAX_LOGIN_ATTEMPTS:
                locked_until = datetime.utcnow() + timedelta(
                    minutes=AuthenticationSecurity.LOCKOUT_DURATION_MINUTES
                )
                user = self.user_repo.lock_account(user, locked_until)
                
                # Log account lockout security event
                self._log_security_event(
                    event_type="account_lockout",
                    user_id=user.id,
                    description=f"Account locked after {AuthenticationSecurity.MAX_LOGIN_ATTEMPTS} failed login attempts",
                    severity="high",
                    ip_address=ip_address,
                    is_blocked=True
                )
                
                # Log via SecurityAudit (for backward compatibility)
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
            
            # Log brute force attempt if multiple failures
            if user.failed_login_attempts and user.failed_login_attempts >= 3:
                self._log_security_event(
                    event_type="brute_force",
                    user_id=user.id,
                    description=f"Multiple failed login attempts detected ({user.failed_login_attempts} attempts)",
                    severity="medium",
                    ip_address=ip_address,
                    is_blocked=False
                )
            
            # Log via SecurityAudit (for backward compatibility)
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
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            if not mfa_code:
                # MFA required but not provided
                return {
                    "access_token": "",
                    "token_type": "bearer",
                    "user_id": str(user.id),
                    "email": user.email,
                    "role": user.role if isinstance(user.role, str) else user.role.value,
                    "mfa_required": True,
                    "mfa_enabled": True
                }
            
            # Verify MFA code
            if not self.verify_mfa_login(str(user.id), mfa_code):
                # Log failed MFA attempt
                self._log_login_attempt(
                    user_id=user.id,
                    is_successful=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="mfa_failed",
                    mfa_used=True
                )
                
                # Log MFA bypass attempt security event
                self._log_security_event(
                    event_type="mfa_bypass_attempt",
                    user_id=user.id,
                    description="Failed MFA verification attempt",
                    severity="high",
                    ip_address=ip_address,
                    is_blocked=True
                )
                
                # Log via SecurityAudit (for backward compatibility)
                if request:
                    SecurityAudit.log_security_event(
                        "MFA_FAILURE",
                        str(user.id),
                        {"email": email},
                        request
                    )
                raise ValueError("Invalid MFA code")
        
        # Reset failed login attempts
        if user.failed_login_attempts and user.failed_login_attempts > 0:
            user = self.user_repo.reset_failed_login(user)
        
        # Update last login
        user = self.user_repo.update_last_login(user)
        
        # Generate JWT access token
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "role": user.role if isinstance(user.role, str) else user.role.value
        }
        access_token = TokenSecurity.create_access_token(token_data)
        
        # Generate refresh token
        refresh_token = TokenSecurity.create_refresh_token()
        refresh_token_hash = TokenSecurity.hash_refresh_token(refresh_token)
        refresh_expires = datetime.utcnow() + timedelta(days=30)
        
        # Store refresh token
        user.refresh_token = refresh_token_hash
        user.refresh_token_expires = refresh_expires
        self.user_repo.update(user)
        
        # Log successful login
        self._log_login_attempt(
            user_id=user.id,
            is_successful=True,
            ip_address=ip_address,
            user_agent=user_agent,
            mfa_used=user.mfa_enabled
        )
        
        # Log via SecurityAudit (for backward compatibility)
        if request:
            SecurityAudit.log_security_event(
                "LOGIN_SUCCESS",
                str(user.id),
                {"email": user.email, "role": user.role if isinstance(user.role, str) else user.role.value, "mfa_used": user.mfa_enabled},
                request
            )
        
        logger.info("User logged in successfully", extra={
            "user_id": str(user.id),
            "email": user.email,
            "mfa_used": user.mfa_enabled
        })
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role if isinstance(user.role, str) else user.role.value,
            "mfa_required": False,
            "mfa_enabled": user.mfa_enabled
        }

    def verify_email(self, token: str, request: any = None) -> Dict[str, any]:
        """
        Verify user email with token.
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
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
        
        # Log email verification security event
        self._log_security_event(
            event_type="email_verified",
            user_id=user.id,
            description="Email verified successfully",
            severity="low",
            ip_address=ip_address
        )
        
        logger.info("Email verified successfully", extra={
            "user_id": str(user.id),
            "email": user.email
        })
        
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
    
    def enable_mfa(self, user_id: str, request: any = None) -> Dict[str, any]:
        """
        Enable MFA for user.
        Enhanced with security event logging.
        """
        import pyotp
        import json
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
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
        
        # Log security event
        self._log_security_event(
            event_type="mfa_setup_initiated",
            user_id=user.id,
            description="MFA setup initiated - awaiting verification",
            severity="low",
            ip_address=ip_address
        )
        
        # Generate QR code URI
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="FindBug Platform"
        )
        
        logger.info("MFA setup initiated", extra={"user_id": str(user.id)})
        
        return {
            "secret": secret,
            "qr_uri": qr_uri,
            "backup_codes": backup_codes,
            "message": "Scan the QR code with your authenticator app and verify to enable MFA"
        }
    
    def verify_mfa_setup(self, user_id: str, code: str, request: any = None) -> Dict[str, any]:
        """
        Verify MFA setup with code.
        Enhanced with security event logging.
        """
        import pyotp
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.mfa_secret:
            raise ValueError("MFA not initialized. Please enable MFA first.")
        
        # Verify code
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(code, valid_window=1):
            # Log failed MFA setup
            self._log_security_event(
                event_type="mfa_setup_failed",
                user_id=user.id,
                description="Failed MFA setup verification - invalid code",
                severity="low",
                ip_address=ip_address
            )
            raise ValueError("Invalid MFA code")
        
        # Enable MFA
        user.mfa_enabled = True
        self.user_repo.update(user)
        
        # Log successful MFA enablement
        self._log_security_event(
            event_type="mfa_enabled",
            user_id=user.id,
            description="MFA successfully enabled",
            severity="low",
            ip_address=ip_address
        )
        
        logger.info("MFA enabled successfully", extra={"user_id": str(user.id)})
        
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
    
    def disable_mfa(self, user_id: str, password: str, request: any = None) -> Dict[str, any]:
        """
        Disable MFA (requires password confirmation).
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        if not PasswordSecurity.verify_password(password, user.password_hash):
            # Log failed MFA disable attempt
            self._log_security_event(
                event_type="mfa_disable_failed",
                user_id=user.id,
                description="Failed MFA disable attempt - invalid password",
                severity="medium",
                ip_address=ip_address
            )
            raise ValueError("Invalid password")
        
        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        self.user_repo.update(user)
        
        # Log MFA disabled security event
        self._log_security_event(
            event_type="mfa_disabled",
            user_id=user.id,
            description="MFA disabled by user",
            severity="medium",
            ip_address=ip_address
        )
        
        logger.info("MFA disabled", extra={"user_id": str(user.id)})
        
        return {
            "message": "MFA disabled successfully",
            "mfa_enabled": False
        }

    def refresh_access_token(self, refresh_token: str) -> Dict[str, any]:
        """Refresh access token using refresh token"""
        
        # Hash the refresh token
        token_hash = TokenSecurity.hash_refresh_token(refresh_token)
        
        # Find user with this refresh token
        user = self.user_repo.get_by_refresh_token(token_hash)
        if not user:
            raise ValueError("Invalid refresh token")
        
        # Check if token is expired
        if user.refresh_token_expires and datetime.utcnow() > user.refresh_token_expires:
            raise ValueError("Refresh token expired. Please login again.")
        
        # Generate new access token
        token_data = {
            "sub": user.email,
            "user_id": str(user.id),
            "role": user.role if isinstance(user.role, str) else user.role.value
        }
        access_token = TokenSecurity.create_access_token(token_data)
        
        # Generate new refresh token
        new_refresh_token = TokenSecurity.create_refresh_token()
        new_refresh_token_hash = TokenSecurity.hash_refresh_token(new_refresh_token)
        new_refresh_expires = datetime.utcnow() + timedelta(days=30)
        
        # Update user with new refresh token
        user.refresh_token = new_refresh_token_hash
        user.refresh_token_expires = new_refresh_expires
        self.user_repo.update(user)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    
    def forgot_password(self, email: str) -> Dict[str, any]:
        """Initiate password reset flow"""
        
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            # Don't reveal if email exists
            return {
                "message": "If the email exists, a password reset link has been sent."
            }
        
        # Generate password reset token
        reset_token = EmailService.generate_verification_token()
        token_hash = EmailService.hash_token(reset_token)
        token_expires = datetime.utcnow() + timedelta(minutes=15)
        
        # Update user
        user.password_reset_token = token_hash
        user.password_reset_token_expires = token_expires
        self.user_repo.update(user)
        
        # Send password reset email
        EmailService.send_password_reset_email(email, reset_token)
        
        return {
            "message": "If the email exists, a password reset link has been sent."
        }
    
    def reset_password(self, token: str, new_password: str, request: any = None) -> Dict[str, any]:
        """
        Reset password using reset token.
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
        # Validate password strength
        is_valid, error = PasswordSecurity.validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error)
        
        # Hash the token
        token_hash = EmailService.hash_token(token)
        
        # Find user with this token
        user = self.user_repo.get_by_password_reset_token(token_hash)
        if not user:
            raise ValueError("Invalid or expired reset token")
        
        # Check if token is expired
        if user.password_reset_token_expires and datetime.utcnow() > user.password_reset_token_expires:
            raise ValueError("Reset token has expired. Please request a new one.")
        
        # Update password
        user.password_hash = PasswordSecurity.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_token_expires = None
        user.password_changed_at = datetime.utcnow()
        
        # Invalidate all refresh tokens (force re-login)
        user.refresh_token = None
        user.refresh_token_expires = None
        
        self.user_repo.update(user)
        
        # Log password reset security event
        self._log_security_event(
            event_type="password_reset",
            user_id=user.id,
            description="Password reset successfully via reset token",
            severity="medium",
            ip_address=ip_address
        )
        
        logger.info("Password reset successfully", extra={"user_id": str(user.id)})
        
        return {
            "message": "Password reset successfully. Please login with your new password."
        }
    
    def change_password(self, user_id: str, current_password: str, new_password: str, request: any = None) -> Dict[str, any]:
        """
        Change password (requires current password).
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not PasswordSecurity.verify_password(current_password, user.password_hash):
            # Log failed password change attempt
            self._log_security_event(
                event_type="password_change_failed",
                user_id=user.id,
                description="Failed password change attempt - invalid current password",
                severity="medium",
                ip_address=ip_address
            )
            raise ValueError("Current password is incorrect")
        
        # Validate new password strength
        is_valid, error = PasswordSecurity.validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if new password is same as current
        if PasswordSecurity.verify_password(new_password, user.password_hash):
            raise ValueError("New password must be different from current password")
        
        # Update password
        user.password_hash = PasswordSecurity.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        
        # Invalidate all refresh tokens (force re-login on other devices)
        user.refresh_token = None
        user.refresh_token_expires = None
        
        self.user_repo.update(user)
        
        # Log password change security event
        self._log_security_event(
            event_type="password_changed",
            user_id=user.id,
            description="Password changed successfully",
            severity="medium",
            ip_address=ip_address
        )
        
        logger.info("Password changed successfully", extra={"user_id": str(user.id)})
        
        return {
            "message": "Password changed successfully. Please login again."
        }
    
    def logout(self, user_id: str, request: any = None) -> Dict[str, any]:
        """
        Logout user (invalidate refresh token).
        Enhanced with security event logging.
        """
        
        # Extract request info
        ip_address, _ = self._extract_request_info(request)
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Invalidate refresh token
        user.refresh_token = None
        user.refresh_token_expires = None
        self.user_repo.update(user)
        
        # Log logout security event
        self._log_security_event(
            event_type="logout",
            user_id=user.id,
            description="User logged out successfully",
            severity="low",
            ip_address=ip_address
        )
        
        logger.info("User logged out", extra={"user_id": str(user.id)})
        
        return {
            "message": "Logged out successfully"
        }
