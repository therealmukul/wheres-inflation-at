"""
Health check response models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Response model for health check endpoints."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="Service version")
    service: str = Field(..., description="Service name")


class ReadinessResponse(BaseModel):
    """Response model for readiness check endpoint."""
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    ready: bool = Field(..., description="Service readiness status")
    timestamp: datetime = Field(..., description="Current timestamp")
    service: str = Field(..., description="Service name")