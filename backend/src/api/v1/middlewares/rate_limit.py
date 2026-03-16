"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.security import RateLimiter
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse
    
    Applies different limits based on endpoint:
    - Auth endpoints: 5 requests per minute
    - API endpoints: 60 requests per minute
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Get endpoint path
        path = request.url.path
        
        # Determine rate limit based on endpoint
        if '/auth/' in path:
            # Stricter limit for auth endpoints
            max_requests = 5
            window_seconds = 60
            identifier = f"auth:{client_ip}"
        else:
            # Standard limit for other endpoints
            max_requests = 60
            window_seconds = 60
            identifier = f"api:{client_ip}"
        
        # Check rate limit
        is_allowed, remaining = RateLimiter.check_rate_limit(
            identifier, 
            max_requests, 
            window_seconds
        )
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": window_seconds
                },
                headers={
                    "Retry-After": str(window_seconds),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + window_seconds)
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window_seconds)
        
        return response


def rate_limit_dependency(request: Request, max_requests: int = 60, window_seconds: int = 60):
    """
    Dependency for rate limiting specific endpoints
    
    Usage:
        @router.post("/endpoint", dependencies=[Depends(rate_limit_dependency)])
    """
    client_ip = request.client.host
    identifier = f"{request.url.path}:{client_ip}"
    
    is_allowed, remaining = RateLimiter.check_rate_limit(
        identifier,
        max_requests,
        window_seconds
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(window_seconds)}
        )
    
    return {"remaining": remaining}
