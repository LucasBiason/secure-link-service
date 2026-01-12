"""
Unit tests for the link_router endpoints.

This module contains tests for the link_router, ensuring that all API endpoints
behave as expected for valid and invalid input data, and that controller interactions
are performed correctly.
"""

import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.routers.link_router import router as link_api_router

client = TestClient(link_api_router)


@pytest.fixture
def mock_link_controller():
    """Fixture to patch LinkController in the router and yield the mock."""
    with patch("app.routers.link_router.LinkController", autospec=True) as mock:
        yield mock


def test_generate_link_success(mock_link_controller):
    """Tests generating a link successfully returns the short code."""
    mock_ctrl = mock_link_controller.return_value
    from app.schemas.link import LinkGenerateResponse
    from datetime import datetime, timedelta
    
    mock_response = LinkGenerateResponse(
        short_code="test123",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        created_at=datetime.utcnow()
    )
    mock_ctrl.generate_link.return_value = mock_response
    
    response = client.post(
        "/generate",
        json={"data": {"test": "data"}},
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["short_code"] == "test123"
    mock_ctrl.generate_link.assert_called_once()


def test_generate_link_missing_data(mock_link_controller):
    """Tests generating a link without data returns 422."""
    response = client.post(
        "/generate",
        json={},
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_validate_link_success(mock_link_controller):
    """Tests validating a link successfully returns decrypted data."""
    mock_ctrl = mock_link_controller.return_value
    from app.schemas.link import LinkValidationResponse
    from datetime import datetime
    
    mock_response = LinkValidationResponse(
        valid=True,
        data={"test": "data"},
        token="test_token",
        encrypted_at=datetime.utcnow()
    )
    mock_ctrl.validate_link.return_value = mock_response
    
    response = client.get("/test123/validate")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["valid"] is True
    assert response.json()["data"] == {"test": "data"}
    mock_ctrl.validate_link.assert_called_once_with("test123")


def test_validate_link_not_found(mock_link_controller):
    """Tests validating a non-existent link returns invalid response."""
    mock_ctrl = mock_link_controller.return_value
    from app.schemas.link import LinkValidationResponse
    
    mock_response = LinkValidationResponse(
        valid=False,
        error="Link not found or expired"
    )
    mock_ctrl.validate_link.return_value = mock_response
    
    response = client.get("/nonexistent/validate")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["valid"] is False
    assert "not found" in response.json()["error"].lower()

