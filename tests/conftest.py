"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    from unittest.mock import patch
    from datetime import datetime
    
    fixed_datetime = datetime(2024, 1, 1, 12, 0, 0)
    
    with patch('app.routers.health.datetime') as mock_dt:
        mock_dt.utcnow.return_value = fixed_datetime
        yield fixed_datetime