"""
FastAPI application entry point.
Configures the main application instance with middleware, exception handlers, and routers.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import settings
from app.utils.logging import setup_logging, get_logger
from app.utils.exceptions import BaseAPIException, create_error_response
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    setup_logging(settings.log_level, settings.environment)
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="A Python web service template built with FastAPI",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Get logger for this module
logger = get_logger(__name__)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = request.state.start_time = request.headers.get("x-request-start")
    
    # Log request
    logger.info(
        f"Request started",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    logger.info(
        f"Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    return response


# Global exception handlers
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions."""
    logger.warning(
        f"API exception: {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            detail=exc.detail,
            error_code=exc.error_code,
            timestamp=exc.timestamp
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "url": str(request.url),
            "method": request.method,
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(detail=exc.detail)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "url": str(request.url),
            "method": request.method,
            "validation_errors": exc.errors(),
        }
    )
    
    # Format validation errors for better readability
    formatted_errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            detail="Validation failed",
            error_code="VALIDATION_ERROR"
        ) | {"validation_errors": formatted_errors}
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic model validation errors."""
    logger.warning(
        f"Pydantic validation error: {exc.errors()}",
        extra={
            "url": str(request.url),
            "method": request.method,
            "validation_errors": exc.errors(),
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            detail="Data validation failed",
            error_code="PYDANTIC_VALIDATION_ERROR"
        ) | {"validation_errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
        },
        exc_info=True
    )
    
    # Don't expose internal error details in production
    detail = str(exc) if settings.debug else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR"
        )
    )


# Include routers
app.include_router(health.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint returning basic application information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else None
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )