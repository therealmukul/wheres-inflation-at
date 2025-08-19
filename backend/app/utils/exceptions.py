"""
Custom exceptions and error handling utilities.
Provides consistent error responses across the application.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception class for API errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()


class ItemNotFoundError(BaseAPIException):
    """Raised when an item is not found."""
    
    def __init__(self, item_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
            error_code="ITEM_NOT_FOUND"
        )


class ItemValidationError(BaseAPIException):
    """Raised when item validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="ITEM_VALIDATION_ERROR"
        )


class ServiceUnavailableError(BaseAPIException):
    """Raised when a service dependency is unavailable."""
    
    def __init__(self, service_name: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service {service_name} is currently unavailable",
            error_code="SERVICE_UNAVAILABLE"
        )


def create_error_response(
    detail: str,
    error_code: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        detail: Human-readable error message
        error_code: Machine-readable error code
        timestamp: When the error occurred
        
    Returns:
        Dictionary containing error response data
    """
    return {
        "detail": detail,
        "error_code": error_code,
        "timestamp": (timestamp or datetime.utcnow()).isoformat() + "Z"
    }