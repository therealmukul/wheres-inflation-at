"""
Tests for health check endpoints.
"""

import pytest
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from app.config import settings


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    def test_health_check_success(self, client: TestClient):
        """Test successful health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "service" in data
        
        assert data["status"] == "healthy"
        assert data["version"] == settings.version
        assert data["service"] == settings.app_name
        
        # Verify timestamp is a valid ISO format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
    
    def test_health_check_response_structure(self, client: TestClient):
        """Test health check response has correct structure."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_keys = {"status", "timestamp", "version", "service"}
        assert set(data.keys()) == expected_keys
        
        # Verify data types
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["service"], str)
    
    def test_readiness_check_success(self, client: TestClient):
        """Test successful readiness check endpoint."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "ready" in data
        assert "timestamp" in data
        assert "service" in data
        
        assert data["ready"] is True
        assert data["service"] == settings.app_name
        
        # Verify timestamp is a valid ISO format
        timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)
    
    def test_readiness_check_response_structure(self, client: TestClient):
        """Test readiness check response has correct structure."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_keys = {"ready", "timestamp", "service"}
        assert set(data.keys()) == expected_keys
        
        # Verify data types
        assert isinstance(data["ready"], bool)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["service"], str)
    
    def test_health_endpoints_content_type(self, client: TestClient):
        """Test that health endpoints return JSON content type."""
        health_response = client.get("/health")
        ready_response = client.get("/health/ready")
        
        assert health_response.headers["content-type"] == "application/json"
        assert ready_response.headers["content-type"] == "application/json"
    
    def test_health_endpoints_multiple_calls(self, client: TestClient):
        """Test that health endpoints work consistently across multiple calls."""
        # Make multiple calls to ensure consistency
        for _ in range(3):
            health_response = client.get("/health")
            ready_response = client.get("/health/ready")
            
            assert health_response.status_code == status.HTTP_200_OK
            assert ready_response.status_code == status.HTTP_200_OK
            
            health_data = health_response.json()
            ready_data = ready_response.json()
            
            assert health_data["status"] == "healthy"
            assert ready_data["ready"] is True
    
    def test_health_check_with_mock_datetime(self, client: TestClient, mock_datetime):
        """Test health check with mocked datetime for consistent testing."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_timestamp = mock_datetime.isoformat()
        assert data["timestamp"] == expected_timestamp
    
    def test_readiness_check_with_mock_datetime(self, client: TestClient, mock_datetime):
        """Test readiness check with mocked datetime for consistent testing."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        expected_timestamp = mock_datetime.isoformat()
        assert data["timestamp"] == expected_timestamp


class TestHealthEndpointsIntegration:
    """Integration tests for health endpoints."""
    
    def test_health_endpoints_in_openapi_schema(self, client: TestClient):
        """Test that health endpoints are included in OpenAPI schema."""
        response = client.get("/openapi.json")
        
        if response.status_code == status.HTTP_200_OK:
            openapi_schema = response.json()
            paths = openapi_schema.get("paths", {})
            
            assert "/health" in paths
            assert "/health/ready" in paths
            
            # Check that GET method is defined for both endpoints
            assert "get" in paths["/health"]
            assert "get" in paths["/health/ready"]
    
    def test_health_endpoints_tags(self, client: TestClient):
        """Test that health endpoints have correct tags in OpenAPI."""
        response = client.get("/openapi.json")
        
        if response.status_code == status.HTTP_200_OK:
            openapi_schema = response.json()
            paths = openapi_schema.get("paths", {})
            
            health_tags = paths["/health"]["get"].get("tags", [])
            ready_tags = paths["/health/ready"]["get"].get("tags", [])
            
            assert "Health" in health_tags
            assert "Health" in ready_tags