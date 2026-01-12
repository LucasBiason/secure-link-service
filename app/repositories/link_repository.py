"""
Repository for link data storage in Redis.

Handles storing and retrieving encrypted link data with TTL.
"""

import os
import json
from typing import Optional, Dict, Any

import redis
from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
load_dotenv()


class LinkRepository:
    """
    Repository for managing link data in Redis.
    
    Stores encrypted data with TTL (Time To Live) for automatic expiration.
    """
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        self.expiration_hours = int(os.getenv("LINK_EXPIRATION_HOURS", 1))
        self.final_expiration_hours = int(os.getenv("LINK_FINAL_EXPIRATION_HOURS", 2))
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password if self.redis_password else None,
                decode_responses=False  # We need bytes for encrypted data
            )
            self.redis_client.ping()
            logger.info(f"Redis connected at {self.redis_host}:{self.redis_port}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    def save(
        self,
        short_code: str,
        encrypted_data: bytes,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Save encrypted link data to Redis.
        
        Args:
            short_code: Short code identifier
            encrypted_data: Encrypted data bytes
            metadata: Metadata dictionary (encrypted_at, expires_at, etc.)
            
        Returns:
            True if saved successfully
            
        Raises:
            Exception: If save operation fails
        """
        try:
            # Store encrypted data with metadata
            data_to_store = {
                "encrypted_data": encrypted_data.hex(),  # Convert bytes to hex string
                "metadata": metadata
            }
            
            # Convert to JSON for storage
            json_data = json.dumps(data_to_store)
            
            # Save with TTL (expiration in seconds)
            expiration_seconds = self.expiration_hours * 3600
            self.redis_client.setex(
                f"link:{short_code}",
                expiration_seconds,
                json_data
            )
            logger.debug(f"Link saved to Redis: {short_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to save link data: {e}")
            raise Exception(f"Failed to save link data: {e}")
    
    def get(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve link data from Redis.
        
        Args:
            short_code: Short code identifier
            
        Returns:
            Dictionary with encrypted_data (bytes) and metadata, or None if not found
        """
        try:
            data = self.redis_client.get(f"link:{short_code}")
            if not data:
                logger.debug(f"Link not found in Redis: {short_code}")
                return None
            
            # Parse JSON
            parsed = json.loads(data.decode('utf-8'))
            
            # Convert hex string back to bytes
            encrypted_data = bytes.fromhex(parsed["encrypted_data"])
            
            logger.debug(f"Link retrieved from Redis: {short_code}")
            return {
                "encrypted_data": encrypted_data,
                "metadata": parsed["metadata"]
            }
        except Exception as e:
            logger.error(f"Failed to retrieve link data: {e}")
            return None
    
    def delete(self, short_code: str) -> bool:
        """
        Delete link data from Redis.
        
        Args:
            short_code: Short code identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            result = self.redis_client.delete(f"link:{short_code}")
            deleted = result > 0
            if deleted:
                logger.debug(f"Link deleted from Redis: {short_code}")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete link: {e}")
            return False
    
    def exists(self, short_code: str) -> bool:
        """
        Check if link exists in Redis.
        
        Args:
            short_code: Short code identifier
            
        Returns:
            True if exists, False otherwise
        """
        try:
            exists = self.redis_client.exists(f"link:{short_code}") > 0
            return exists
        except Exception as e:
            logger.error(f"Failed to check link existence: {e}")
            return False

