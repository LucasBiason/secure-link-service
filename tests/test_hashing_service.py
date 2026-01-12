"""
Unit tests for HashingService.

Tests short code generation.
"""

import pytest
from app.services.hashing_service import HashingService


def test_generate_short_code():
    """Test short code generation."""
    test_data = b"test_encrypted_data"
    short_code = HashingService.generate_short_code(test_data)
    
    assert short_code is not None
    assert isinstance(short_code, str)
    assert len(short_code) <= 8


def test_generate_short_code_deterministic():
    """Test that same input produces same output."""
    test_data = b"test_encrypted_data"
    code1 = HashingService.generate_short_code(test_data)
    code2 = HashingService.generate_short_code(test_data)
    
    assert code1 == code2


def test_generate_short_code_different_inputs():
    """Test that different inputs produce different outputs."""
    data1 = b"test_data_1"
    data2 = b"test_data_2"
    
    code1 = HashingService.generate_short_code(data1)
    code2 = HashingService.generate_short_code(data2)
    
    assert code1 != code2

