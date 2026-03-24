"""
Custom HTTP exceptions for FindBug Platform
Provides consistent error response shapes across all endpoints.
"""
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """404 – Resource not found."""
    def __init__(self, detail: str = "Resource not found."):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenException(HTTPException):
    """403 – Access denied."""
    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedException(HTTPException):
    """401 – Authentication required."""
    def __init__(self, detail: str = "Authentication required."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ConflictException(HTTPException):
    """409 – Conflict (duplicate resource)."""
    def __init__(self, detail: str = "Resource already exists."):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(HTTPException):
    """422 – Validation error (business rule violation)."""
    def __init__(self, detail: str = "Validation failed."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class BadRequestException(HTTPException):
    """400 – Malformed request."""
    def __init__(self, detail: str = "Bad request."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class RateLimitException(HTTPException):
    """429 – Too many requests."""
    def __init__(self, detail: str = "Too many requests. Please try again later."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail
        )


class ServiceUnavailableException(HTTPException):
    """503 – Downstream service unavailable."""
    def __init__(self, detail: str = "Service temporarily unavailable."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail
        )


class InternalServerException(HTTPException):
    """500 – Unexpected server error."""
    def __init__(self, detail: str = "An unexpected error occurred."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class PaymentException(HTTPException):
    """402 – Payment processing error."""
    def __init__(self, detail: str = "Payment processing failed."):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail
        )
