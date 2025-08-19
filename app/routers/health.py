"""
Health check router.
Provides endpoints for service health monitoring and readiness checks.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.health import HealthResponse, ReadinessResponse
from app.utils.logging import get_logger

# Create router instance
router = APIRouter(
    prefix="",
    tags=["Health"],
    responses={
        500: {"description": "Internal server error"}
    }
)

# Get logger for this module
logger = get_logger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Returns the current health status of the service with metadata"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint that returns service status information.
    
    This endpoint provides basic health information including:
    - Service status (always "healthy" for this MVP)
    - Current timestamp
    - Service version
    - Service name
    
    Returns:
        HealthResponse: Health status information
    """
    logger.debug("Health check requested")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.version,
        service=settings.app_name
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Returns the readiness status for load balancer health checks"
)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint for load balancer health checks.
    
    This endpoint indicates whether the service is ready to accept traffic.
    For this MVP, the service is always ready when it's running.
    In a more complex application, this might check database connectivity,
    external service availability, etc.
    
    Returns:
        ReadinessResponse: Readiness status information
    """
    logger.debug("Readiness check requested")
    
    # For MVP, service is ready if it's running
    # In production, you might check database connectivity, etc.
    is_ready = True
    
    return ReadinessResponse(
        ready=is_ready,
        timestamp=datetime.utcnow(),
        service=settings.app_name
    )