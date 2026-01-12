"""
Pydantic schemas for link generation and validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LinkGenerateRequest(BaseModel):
    """Request schema for generating a secure link."""
    
    data: Dict[str, Any] = Field(
        ...,
        description="Any JSON data to encrypt and store in the link"
    )


class LinkGenerateResponse(BaseModel):
    """Response schema for link generation."""
    
    short_code: str = Field(..., description="Short code for the link")
    expires_at: datetime = Field(..., description="Expiration datetime")
    created_at: datetime = Field(..., description="Creation datetime")


class LinkValidationResponse(BaseModel):
    """Response schema for link validation."""
    
    valid: bool = Field(..., description="Whether the link is valid")
    data: Optional[Dict[str, Any]] = Field(None, description="Decrypted data if valid")
    token: Optional[str] = Field(None, description="JWT token from header if valid")
    encrypted_at: Optional[datetime] = Field(None, description="Encryption timestamp if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")

