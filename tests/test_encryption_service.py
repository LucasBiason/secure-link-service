"""
Unit tests for EncryptionService.

Tests encryption and decryption operations.
"""

import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet

from app.services.encryption_service import EncryptionService


@pytest.fixture
def encryption_key():
    """Generate a test encryption key."""
    return Fernet.generate_key().decode()


def test_encrypt_decrypt_success(encryption_key):
    """Test successful encryption and decryption."""
    with patch.dict('os.environ', {'ENCRYPTION_KEY': encryption_key}):
        service = EncryptionService()
        test_data = {"test": "data", "number": 123}
        
        encrypted = service.encrypt(test_data)
        assert encrypted is not None
        assert isinstance(encrypted, bytes)
        
        decrypted = service.decrypt(encrypted)
        assert decrypted == test_data


def test_decrypt_invalid_data(encryption_key):
    """Test decryption of invalid data."""
    with patch.dict('os.environ', {'ENCRYPTION_KEY': encryption_key}):
        service = EncryptionService()
        
        result = service.decrypt(b'invalid_encrypted_data')
        assert result is None


def test_missing_encryption_key():
    """Test initialization without encryption key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            EncryptionService()
        assert "ENCRYPTION_KEY" in str(exc_info.value)

