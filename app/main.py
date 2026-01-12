"""
Main application module for the Secure Link Service.

This module initializes the FastAPI application with all necessary
middleware, routers, and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import link_router

app = FastAPI(
    title="Secure Link Service",
    description=(
        "A lightweight microservice for generating and validating secure, "
        "time-limited links with encrypted payloads. Perfect for automation "
        "integrations (Telegram, WhatsApp, N8N) that need to pass authentication "
        "tokens and action data to users through links."
    ),
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(link_router.router, prefix="/links", tags=["Links"])


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Secure Link Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
