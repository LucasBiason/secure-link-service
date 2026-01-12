"""
Controller for link generation and validation operations.

Handles business logic for creating and validating secure links.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import HTTPException, Header, status

import logging

logging.basicConfig(level=logging.INFO)

from app.services.encryption_service import EncryptionService
from app.services.hashing_service import HashingService
from app.repositories.link_repository import LinkRepository
from app.schemas.link import LinkGenerateRequest, LinkGenerateResponse, LinkValidationResponse

logger = logging.getLogger(__name__)


class LinkController:
    """
    Controller for managing secure link operations.
    """
    
    def __init__(self):
        """Initialize controller with required services."""
        self.encryption_service = EncryptionService()
        self.hashing_service = HashingService()
        self.repository = LinkRepository()
        self.expiration_hours = int(self.repository.expiration_hours)
        logger.info("LinkController initialized")
    
    def generate_link(
        self,
        request: LinkGenerateRequest,
        authorization: Optional[str] = Header(None, alias="Authorization")
    ) -> LinkGenerateResponse:
        """
        Generate a secure link from data and JWT token.
        
        Args:
            request: Link generation request with data
            authorization: JWT token from Authorization header
            
        Returns:
            Link generation response with short code
            
        Raises:
            HTTPException: If token is missing or generation fails
        """
        # Extract token from Authorization header
        token = None
        if authorization:
            if authorization.startswith("Bearer "):
                token = authorization[7:]
            else:
                token = authorization
        
        if not token:
            logger.warning("Link generation attempted without authorization token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization token is required"
            )
        
        # Prepare data for encryption (data + token + timestamp)
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.expiration_hours)
        
        data_to_encrypt = {
            "data": request.data,
            "token": token,
            "encrypted_at": now.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        # Encrypt data
        try:
            encrypted_data = self.encryption_service.encrypt(data_to_encrypt)
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to encrypt data: {str(e)}"
            )
        
        # Generate short code
        short_code = self.hashing_service.generate_short_code(encrypted_data)
        
        # Check for collisions (very unlikely, but handle it)
        max_attempts = 5
        attempt = 0
        while self.repository.exists(short_code) and attempt < max_attempts:
            # Add timestamp to make it unique
            encrypted_data_with_timestamp = encrypted_data + str(now.timestamp()).encode()
            short_code = self.hashing_service.generate_short_code(encrypted_data_with_timestamp)
            attempt += 1
        
        if attempt >= max_attempts:
            logger.error("Failed to generate unique short code after multiple attempts")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate unique short code"
            )
        
        # Save to Redis
        metadata = {
            "encrypted_at": now.isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        try:
            self.repository.save(short_code, encrypted_data, metadata)
            logger.info(f"Link generated successfully: {short_code}")
        except Exception as e:
            logger.error(f"Failed to save link: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save link: {str(e)}"
            )
        
        return LinkGenerateResponse(
            short_code=short_code,
            expires_at=expires_at,
            created_at=now
        )
    
    def validate_link(self, short_code: str) -> LinkValidationResponse:
        """
        Validate a secure link and return decrypted data.
        
        Args:
            short_code: Short code to validate
            
        Returns:
            Link validation response with decrypted data or error
        """
        # Retrieve from Redis
        link_data = self.repository.get(short_code)
        
        if not link_data:
            logger.warning(f"Link validation failed: not found - {short_code}")
            return LinkValidationResponse(
                valid=False,
                error="Link not found or expired"
            )
        
        # Decrypt data
        encrypted_data = link_data["encrypted_data"]
        decrypted_data = self.encryption_service.decrypt(encrypted_data)
        
        if not decrypted_data:
            logger.warning(f"Link validation failed: decryption error - {short_code}")
            return LinkValidationResponse(
                valid=False,
                error="Link data is corrupted or invalid"
            )
        
        # Check expiration
        expires_at_str = decrypted_data.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.utcnow() > expires_at:
                logger.warning(f"Link validation failed: expired - {short_code}")
                return LinkValidationResponse(
                    valid=False,
                    error="Link has expired"
                )
        
        # Return valid response
        encrypted_at_str = decrypted_data.get("encrypted_at")
        encrypted_at = None
        if encrypted_at_str:
            encrypted_at = datetime.fromisoformat(encrypted_at_str)
        
        logger.info(f"Link validated successfully: {short_code}")
        return LinkValidationResponse(
            valid=True,
            data=decrypted_data.get("data"),
            token=decrypted_data.get("token"),
            encrypted_at=encrypted_at
        )

