"""
Unit tests for LinkRepository.

Tests Redis operations for link storage and retrieval.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.repositories.link_repository import LinkRepository


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    with patch('app.repositories.link_repository.redis.Redis') as mock:
        client = Mock()
        client.ping.return_value = True
        client.setex.return_value = True
        client.get.return_value = None
        client.delete.return_value = 1
        client.exists.return_value = 0
        mock.return_value = client
        yield client


def test_save_link_success(mock_redis_client):
    """Test successful link save."""
    with patch.dict('os.environ', {
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'LINK_EXPIRATION_HOURS': '1'
    }):
        repository = LinkRepository()
        result = repository.save("test123", b'encrypted_data', {"test": "metadata"})
        
        assert result is True
        mock_redis_client.setex.assert_called_once()


def test_get_link_success(mock_redis_client):
    """Test successful link retrieval."""
    import json
    test_data = {
        "encrypted_data": b'encrypted_data'.hex(),
        "metadata": {"test": "metadata"}
    }
    mock_redis_client.get.return_value = json.dumps(test_data).encode('utf-8')
    
    with patch.dict('os.environ', {
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0'
    }):
        repository = LinkRepository()
        result = repository.get("test123")
        
        assert result is not None
        assert "encrypted_data" in result
        assert "metadata" in result


def test_get_link_not_found(mock_redis_client):
    """Test retrieval of non-existent link."""
    mock_redis_client.get.return_value = None
    
    with patch.dict('os.environ', {
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0'
    }):
        repository = LinkRepository()
        result = repository.get("nonexistent")
        
        assert result is None

