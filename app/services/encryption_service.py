"""
Encryption service for secure link data.

Handles encryption and decryption of link payloads using Fernet (AES-256-GCM).
"""

import os
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
load_dotenv()


class EncryptionService:
    """
    Service for encrypting and decrypting link data.
    
    Uses Fernet (symmetric encryption) with a key from environment variables.
    """
    
    def __init__(self):
        """Initialize encryption service with key from environment."""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")
        
        try:
            self.cipher = Fernet(encryption_key.encode())
            logger.info("Encryption service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption service: {e}")
            raise ValueError(f"Invalid ENCRYPTION_KEY: {e}")
    
    def encrypt(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt data dictionary.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Encrypted bytes
            
        Raises:
            Exception: If encryption fails
        """
        import json
        try:
            json_data = json.dumps(data)
            encrypted = self.cipher.encrypt(json_data.encode())
            logger.debug("Data encrypted successfully")
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise Exception(f"Failed to encrypt data: {e}")
    
    def decrypt(self, encrypted_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted bytes to decrypt
            
        Returns:
            Decrypted dictionary or None if decryption fails
        """
        try:
            import json
            decrypted = self.cipher.decrypt(encrypted_data)
            data = json.loads(decrypted.decode())
            logger.debug("Data decrypted successfully")
            return data
        except (InvalidToken, ValueError) as e:
            logger.warning(f"Decryption failed: {e}")
            return None

