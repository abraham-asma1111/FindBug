"""
CSRF Protection Middleware
Protects against Cross-Site Request Forgery attacks for state-changing operations
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta


class CSRFProtection:
    """CSRF Token Management"""
    
    # Store tokens in memory (in production, use Redis)
    _tokens = {}
    
    @staticmethod
    def generate_csrf_token(session_id: str) -> str:
        """Generate a CSRF token for a session"""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store with expiration (1 hour)
        CSRFProtection._tokens[session_id] = {
            "token_hash": token_hash,
            "expires_at": datetime.utcnow() + timedelta(hours=1)
        }
        
        return token
    
    @staticmethod
    def verify_csrf_token(session_id: str, token: str) -> bool:
        """Verify CSRF token"""
        if session_id not in CSRFProtection._tokens:
            return False
        
        stored = CSRFProtection._tokens[session_id]
        
        # Check expiration
        if stored["expires_at"] < datetime.utcnow():
            del CSRFProtection._tokens[session_id]
            return False
        
        # Verify token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash == stored["token_hash"]
    
    @staticmethod
    def cleanup_expired_tokens():
        """Remove expired tokens"""
        now = datetime.utcnow()
        expired = [
            sid for sid, data in CSRFProtection._tokens.items()
            if data["expires_at"] < now
        ]
        for sid in expired:
            del CSRFProtection._tokens[sid]


async def csrf_protect(request: Request, call_next):
    """
    CSRF Protection Middleware
    
    Protects PUT, POST, PATCH, DELETE requests from CSRF attacks
    """
    # Skip CSRF check for safe methods
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        response = await call_next(request)
        return response
    
    # Skip CSRF check for certain paths (like webhooks)
    skip_paths = ["/api/v1/auth/kyc/webhook", "/health", "/docs", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        response = await call_next(request)
        return response
    
    # For now, we'll use a simple approach:
    # 1. Check for CSRF token in header
    # 2. If using JWT, the token itself provides some CSRF protection
    
    # Get CSRF token from header
    csrf_token = request.headers.get("X-CSRF-Token")
    
    # Get session ID (from cookie or JWT)
    session_id = request.headers.get("Authorization", "")
    
    # For JWT-based auth, the token itself provides CSRF protection
    # because attackers can't read it from another domain
    if session_id.startswith("Bearer "):
        # JWT provides implicit CSRF protection
        response = await call_next(request)
        return response
    
    # If no JWT and no CSRF token, reject
    if not csrf_token:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "CSRF token missing"}
        )
    
    # Verify CSRF token
    if not CSRFProtection.verify_csrf_token(session_id, csrf_token):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Invalid CSRF token"}
        )
    
    response = await call_next(request)
    return response


def get_csrf_token(request: Request) -> str:
    """Get CSRF token for current session"""
    session_id = request.headers.get("Authorization", "")
    if not session_id:
        session_id = secrets.token_urlsafe(16)
    
    return CSRFProtection.generate_csrf_token(session_id)
