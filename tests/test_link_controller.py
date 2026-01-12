"""
Unit tests for LinkController.

Tests link generation and validation logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from fastapi import HTTPException

from app.controllers.link_controller import LinkController
from app.schemas.link import LinkGenerateRequest


@pytest.fixture
def mock_encryption_service():
    """Mock encryption service."""
    with patch('app.controllers.link_controller.EncryptionService') as mock:
        instance = Mock()
        instance.encrypt.return_value = b'encrypted_data'
        instance.decrypt.return_value = {
            "data": {"test": "data"},
            "token": "test_token",
            "encrypted_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_hashing_service():
    """Mock hashing service."""
    with patch('app.controllers.link_controller.HashingService') as mock:
        instance = Mock()
        instance.generate_short_code.return_value = "test123"
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_repository():
    """Mock link repository."""
    with patch('app.controllers.link_controller.LinkRepository') as mock:
        instance = Mock()
        instance.exists.return_value = False
        instance.save.return_value = True
        instance.get.return_value = {
            "encrypted_data": b'encrypted_data',
            "metadata": {
                "encrypted_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        }
        instance.expiration_hours = 1
        mock.return_value = instance
        yield instance


def test_generate_link_success(mock_encryption_service, mock_hashing_service, mock_repository):
    """Test successful link generation."""
    controller = LinkController()
    request = LinkGenerateRequest(data={"test": "data"})
    
    result = controller.generate_link(request, authorization="Bearer test_token")
    
    assert result.short_code == "test123"
    assert result.expires_at > datetime.utcnow()
    mock_encryption_service.encrypt.assert_called_once()
    mock_repository.save.assert_called_once()


def test_generate_link_missing_token(mock_encryption_service, mock_hashing_service, mock_repository):
    """Test link generation without token."""
    controller = LinkController()
    request = LinkGenerateRequest(data={"test": "data"})
    
    with pytest.raises(HTTPException) as exc_info:
        controller.generate_link(request, authorization=None)
    
    assert exc_info.value.status_code == 401
    assert "token is required" in exc_info.value.detail.lower()


def test_validate_link_success(mock_encryption_service, mock_hashing_service, mock_repository):
    """Test successful link validation."""
    controller = LinkController()
    
    result = controller.validate_link("test123")
    
    assert result.valid is True
    assert result.data == {"test": "data"}
    assert result.token == "test_token"


def test_validate_link_not_found(mock_encryption_service, mock_hashing_service, mock_repository):
    """Test validation of non-existent link."""
    mock_repository.get.return_value = None
    controller = LinkController()
    
    result = controller.validate_link("nonexistent")
    
    assert result.valid is False
    assert "not found" in result.error.lower()


def test_validate_link_expired(mock_encryption_service, mock_hashing_service, mock_repository):
    """Test validation of expired link."""
    expired_time = datetime.utcnow() - timedelta(hours=2)
    mock_encryption_service.decrypt.return_value = {
        "data": {"test": "data"},
        "token": "test_token",
        "encrypted_at": expired_time.isoformat(),
        "expires_at": (expired_time + timedelta(hours=1)).isoformat()
    }
    controller = LinkController()
    
    result = controller.validate_link("expired")
    
    assert result.valid is False
    assert "expired" in result.error.lower()

