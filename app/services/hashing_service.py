"""
Hashing service for generating short codes from encrypted data.

Generates unique, short hash codes (6-8 characters) for use as link identifiers.
"""

import hashlib
import base64
from typing import Optional

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class HashingService:
    """
    Service for generating short hash codes from encrypted data.
    
    Uses SHA-256 + Base64 URL-safe encoding to create short, unique identifiers.
    """
    
    @staticmethod
    def generate_short_code(encrypted_data: bytes, max_length: int = 8) -> str:
        """
        Generate a short code from encrypted data.
        
        Args:
            encrypted_data: Encrypted bytes to hash
            max_length: Maximum length of the short code (default: 8)
            
        Returns:
            Short code string (6-8 characters)
        """
        try:
            # Generate SHA-256 hash
            hash_obj = hashlib.sha256(encrypted_data)
            hash_bytes = hash_obj.digest()
            
            # Use first bytes for shorter code
            hash_bytes = hash_bytes[:max_length]
            
            # Base64 URL-safe encoding, remove padding
            encoded = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')
            
            # Take first max_length characters
            short_code = encoded[:max_length]
            logger.debug(f"Generated short code: {short_code}")
            return short_code
        except Exception as e:
            logger.error(f"Failed to generate short code: {e}")
            raise Exception(f"Failed to generate short code: {e}")
    
    @staticmethod
    def generate_from_data(data: bytes) -> str:
        """
        Generate short code directly from data bytes.
        
        Args:
            data: Data bytes to hash
            
        Returns:
            Short code string
        """
        return HashingService.generate_short_code(data)

