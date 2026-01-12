"""
Link router definitions for the Link Service application.

This module provides the FastAPI routes for generating and validating secure links.
"""

from fastapi import APIRouter, status, Header
from typing import Optional

from app.controllers.link_controller import LinkController
from app.schemas.link import LinkGenerateRequest, LinkGenerateResponse, LinkValidationResponse

router = APIRouter(prefix="/links", tags=["Links"])


@router.post(
    "/generate",
    response_model=LinkGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar link seguro",
    description=(
        "Gera um link seguro com tempo de expiração configurável. "
        "Requer token JWT no header Authorization. Retorna um código curto "
        "que pode ser usado para validar e recuperar os dados encriptados."
    )
)
async def generate_link_route(
    request: LinkGenerateRequest,
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> LinkGenerateResponse:
    """
    Gera um link seguro a partir de dados e token JWT.
    
    Args:
        request: Requisição de geração de link com dados para encriptar
        authorization: Token JWT do header Authorization
        
    Returns:
        Resposta de geração de link com código curto e informações de expiração
    """
    controller = LinkController()
    return controller.generate_link(request, authorization)


@router.get(
    "/{short_code}/validate",
    response_model=LinkValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validar link seguro",
    description=(
        "Valida um link seguro pelo código curto. Retorna dados descriptografados "
        "se o link for válido e não estiver expirado. Retorna erro se o link "
        "não for encontrado, estiver expirado ou corrompido."
    )
)
async def validate_link_route(short_code: str) -> LinkValidationResponse:
    """
    Valida um link seguro e retorna dados descriptografados.
    
    Args:
        short_code: Código curto identificador do link
        
    Returns:
        Resposta de validação de link com dados descriptografados ou erro
    """
    controller = LinkController()
    return controller.validate_link(short_code)

