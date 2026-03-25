"""
Security Module - OWASP Top 10 Protection
Implements security controls for authentication, authorization, and data protection
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import re
import bleach
from functools import wraps
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import hmac

import hashlib
import secrets

# Password hashing context (using hashlib for compatibility)
def hash_password_simple(password: str) -> str:
    """Simple password hashing using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password_simple(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except:
        return False

# Alias for backward compatibility
get_password_hash = hash_password_simple
verify_password = verify_password_simple

# JWT Configuration (will be loaded from env)
SECRET_KEY = "CHANGE_ME_IN_ENV"  # Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================================================
# OWASP A01:2021 - Broken Access Control
# ============================================================================

class RBACPermission:
    """Role-Based Access Control Permissions"""
    
    # User roles
    RESEARCHER = "researcher"
    ORGANIZATION = "organization"
    STAFF = "staff"
    TRIAGE_SPECIALIST = "triage_specialist"
    FINANCE_OFFICER = "finance_officer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    # Permissions matrix
    PERMISSIONS = {
        RESEARCHER: [
            "view_programs",
            "submit_reports",
            "view_own_reports",
            "view_own_earnings",
            "update_own_profile"
        ],
        ORGANIZATION: [
            "create_programs",
            "view_own_programs",
            "view_program_reports",
            "approve_bounties",
            "manage_own_organization"
        ],
        STAFF: [
            "triage_reports",
            "assign_severity",
            "approve_payments",
            "view_all_reports"
        ],
        TRIAGE_SPECIALIST: [
            "triage_reports",
            "assign_severity",
            "view_all_reports"
        ],
        FINANCE_OFFICER: [
            "approve_payments",
            "approve_bounties",
            "view_program_reports"
        ],
        ADMIN: [
            "manage_users",
            "manage_programs",
            "view_analytics",
            "view_audit_logs",
            "manage_staff"
        ],
        SUPER_ADMIN: ["*"]  # All permissions
    }
    
    @staticmethod
    def has_permission(user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        ur = user_role.value if hasattr(user_role, "value") else str(user_role)
        if ur == RBACPermission.SUPER_ADMIN:
            return True
        
        user_permissions = RBACPermission.PERMISSIONS.get(ur, [])
        return required_permission in user_permissions


def require_permission(permission: str):
    """Decorator to enforce permission-based access control"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (injected by dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            if not RBACPermission.has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# OWASP A02:2021 - Cryptographic Failures
# ============================================================================

class PasswordSecurity:
    """Secure password handling"""
    
    # Password requirements
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        return hash_password_simple(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return verify_password_simple(plain_password, hashed_password)
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password meets security requirements
        Returns: (is_valid, error_message)
        """
        if len(password) < PasswordSecurity.MIN_LENGTH:
            return False, f"Password must be at least {PasswordSecurity.MIN_LENGTH} characters"
        
        if PasswordSecurity.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if PasswordSecurity.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if PasswordSecurity.REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if PasswordSecurity.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check against common passwords (simplified - use proper list in production)
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, ""


class TokenSecurity:
    """JWT token management"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16)  # JWT ID for token revocation
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate JWT access token

        Returns:
            Token payload if valid, None otherwise
        """
        return TokenSecurity.verify_token(token)

    @staticmethod
    def create_refresh_token() -> str:
        """Create a secure refresh token"""
        return secrets.token_urlsafe(64)

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """Hash refresh token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()


# ============================================================================
# OWASP A03:2021 - Injection
# ============================================================================

class InputSanitization:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Sanitize HTML to prevent XSS
        Allows only safe tags
        """
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'code', 'pre']
        allowed_attributes = {}
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        Remove dangerous characters
        """
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Allow only alphanumeric, dash, underscore, and dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Prevent hidden files
        if filename.startswith('.'):
            filename = '_' + filename
        
        return filename
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format and prevent SSRF"""
        # Basic URL validation
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if not re.match(pattern, url):
            return False
        
        # Prevent localhost/internal IPs (SSRF protection)
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        for blocked in blocked_hosts:
            if blocked in url.lower():
                return False
        
        return True


# ============================================================================
# OWASP A04:2021 - Insecure Design
# ============================================================================

class BusinessLogicSecurity:
    """Business logic security controls"""
    
    @staticmethod
    def validate_bounty_amount(amount: float, min_amount: float = 0, max_amount: float = 100000) -> tuple[bool, str]:
        """
        Validate bounty amount to prevent business logic flaws
        - Prevent negative amounts
        - Prevent unrealistic amounts
        - Enforce min/max limits
        """
        if amount < min_amount:
            return False, f"Amount must be at least ${min_amount}"
        
        if amount > max_amount:
            return False, f"Amount cannot exceed ${max_amount}"
        
        if amount < 0:
            return False, "Amount cannot be negative"
        
        # Check for precision (max 2 decimal places)
        if round(amount, 2) != amount:
            return False, "Amount can have maximum 2 decimal places"
        
        return True, ""
    
    @staticmethod
    def validate_report_ownership(report_user_id: str, current_user_id: str, current_user_role: str) -> bool:
        """
        Validate user can access report
        Prevents IDOR (Insecure Direct Object Reference)
        """
        # Platform roles that can access all reports
        if current_user_role in [
            RBACPermission.ADMIN,
            RBACPermission.SUPER_ADMIN,
            RBACPermission.STAFF,
            RBACPermission.TRIAGE_SPECIALIST,
        ]:
            return True
        
        # Researcher can only access own reports
        return report_user_id == current_user_id
    
    @staticmethod
    def validate_program_access(program_visibility: str, user_role: str, is_invited: bool = False) -> bool:
        """
        Validate user can access program
        - Public programs: anyone
        - Private programs: invited only
        """
        if program_visibility == "public":
            return True
        
        if program_visibility == "private":
            return is_invited or user_role in [RBACPermission.ADMIN, RBACPermission.SUPER_ADMIN]
        
        return False


# ============================================================================
# OWASP A05:2021 - Security Misconfiguration
# ============================================================================

class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Return security headers to prevent common attacks"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


# ============================================================================
# OWASP A07:2021 - Identification and Authentication Failures
# ============================================================================

class AuthenticationSecurity:
    """Authentication security controls"""
    
    # Account lockout settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = 30
    ABSOLUTE_SESSION_TIMEOUT_HOURS = 8
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token for storage (e.g., password reset tokens)"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_token_hash(token: str, token_hash: str) -> bool:
        """Verify token against stored hash"""
        return hmac.compare_digest(
            hashlib.sha256(token.encode()).hexdigest(),
            token_hash
        )


# ============================================================================
# OWASP A08:2021 - Software and Data Integrity Failures
# ============================================================================

class DataIntegrity:
    """Data integrity validation"""
    
    @staticmethod
    def calculate_checksum(data: bytes) -> str:
        """Calculate SHA-256 checksum for data integrity"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def verify_checksum(data: bytes, expected_checksum: str) -> bool:
        """Verify data integrity using checksum"""
        actual_checksum = DataIntegrity.calculate_checksum(data)
        return hmac.compare_digest(actual_checksum, expected_checksum)


# ============================================================================
# OWASP A09:2021 - Security Logging and Monitoring Failures
# ============================================================================

class SecurityAudit:
    """Security event logging"""
    
    SECURITY_EVENTS = {
        "LOGIN_SUCCESS": "User logged in successfully",
        "LOGIN_FAILURE": "Failed login attempt",
        "LOGOUT": "User logged out",
        "PASSWORD_CHANGE": "Password changed",
        "PASSWORD_RESET": "Password reset requested",
        "ACCOUNT_LOCKED": "Account locked due to failed attempts",
        "PERMISSION_DENIED": "Permission denied",
        "SUSPICIOUS_ACTIVITY": "Suspicious activity detected",
        "DATA_ACCESS": "Sensitive data accessed",
        "DATA_MODIFICATION": "Data modified",
        "ADMIN_ACTION": "Administrative action performed"
    }
    
    @staticmethod
    def log_security_event(event_type: str, user_id: Optional[str], details: Dict[str, Any], request: Request):
        """
        Log security event for monitoring
        Should be implemented with proper logging system
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": request.client.host if request else None,
            "user_agent": request.headers.get("user-agent") if request else None,
            "details": details
        }
        
        # TODO: Implement proper logging (e.g., to database, SIEM)
        print(f"[SECURITY] {log_entry}")
        
        return log_entry


# ============================================================================
# OWASP A10:2021 - Server-Side Request Forgery (SSRF)
# ============================================================================

class SSRFProtection:
    """SSRF attack prevention"""
    
    BLOCKED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '169.254.169.254',  # AWS metadata
        '10.',  # Private network
        '172.16.',  # Private network
        '192.168.'  # Private network
    ]
    
    @staticmethod
    def is_safe_url(url: str) -> bool:
        """Check if URL is safe from SSRF"""
        url_lower = url.lower()
        
        for blocked in SSRFProtection.BLOCKED_HOSTS:
            if blocked in url_lower:
                return False
        
        return True


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """Rate limiting to prevent abuse"""
    
    # In-memory storage (use Redis in production)
    _requests = {}
    
    @staticmethod
    def check_rate_limit(identifier: str, max_requests: int = 60, window_seconds: int = 60) -> tuple[bool, int]:
        """
        Check if request is within rate limit
        Returns: (is_allowed, remaining_requests)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        if identifier in RateLimiter._requests:
            RateLimiter._requests[identifier] = [
                req_time for req_time in RateLimiter._requests[identifier]
                if req_time > window_start
            ]
        else:
            RateLimiter._requests[identifier] = []
        
        # Check limit
        current_requests = len(RateLimiter._requests[identifier])
        
        if current_requests >= max_requests:
            return False, 0
        
        # Add current request
        RateLimiter._requests[identifier].append(now)
        
        remaining = max_requests - current_requests - 1
        return True, remaining


# ============================================================================
# File Upload Security
# ============================================================================

class FileUploadSecurity:
    """Secure file upload handling"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.txt', '.md'],
        'video': ['.mp4', '.webm', '.mov'],
        'archive': ['.zip']
    }
    
    # Max file sizes (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_types: list = None) -> bool:
        """Validate file extension"""
        if allowed_types is None:
            allowed_types = ['image', 'document', 'video']
        
        ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        for file_type in allowed_types:
            if ext in FileUploadSecurity.ALLOWED_EXTENSIONS.get(file_type, []):
                return True
        
        return False
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size"""
        return 0 < file_size <= FileUploadSecurity.MAX_FILE_SIZE
    
    @staticmethod
    def scan_file_content(file_content: bytes) -> bool:
        """
        Basic file content validation
        In production, integrate with antivirus/malware scanner
        """
        # Check for executable signatures
        dangerous_signatures = [
            b'MZ',  # Windows executable
            b'\x7fELF',  # Linux executable
            b'#!/',  # Script shebang
        ]
        
        for signature in dangerous_signatures:
            if file_content.startswith(signature):
                return False
        
        return True
