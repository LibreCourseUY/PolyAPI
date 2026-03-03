import uuid
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

from gateway.config import GATEWAY_CONFIG, SERVICES, get_service_url
from gateway.contracts.models import (
    ModuleInfo,
    ModulesListResponse,
    RequestEnvelope,
    ResponseEnvelope,
    ResponseError,
)
from gateway.schemas.request import GeneralRequest

router = APIRouter()


@router.get("/health")
async def health_check():
    """Gateway health check endpoint."""
    return {
        "status": "ok",
        "gateway": GATEWAY_CONFIG["name"],
        "version": GATEWAY_CONFIG["version"],
    }


@router.get("/modules")
async def list_modules():
    """List all registered modules and their status."""
    modules = [
        ModuleInfo(
            name=service["name"],
            version=service["version"],
            url=service["url"],
            status="unknown",
        )
        for service in SERVICES.values()
    ]
    return ModulesListResponse(modules=modules)

@router.post("/sort")
async def sort_items(request: GeneralRequest):
    """Proxy request to the Go sort module."""
    request_id = str(uuid.uuid4())
    sort_url = get_service_url("sort")

    envelope = RequestEnvelope(
        request_id=request_id,
        module="sort",
        version="1.0.0",
        payload=request.payload,
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{sort_url}/sort",
                json=envelope.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            module_response = response.json()
    except httpx.ConnectError:
        error_response = ResponseEnvelope(
            request_id=request_id,
            module="sort",
            version="1.0.0",
            status="error",
            data=None,
            error=ResponseError(
                code="MODULE_UNREACHABLE",
                message="The sort module is not reachable",
                details={"url": sort_url},
            ),
        )
        return error_response.model_dump()
    except httpx.HTTPStatusError as e:
        error_response = ResponseEnvelope(
            request_id=request_id,
            module="sort",
            version="1.0.0",
            status="error",
            data=None,
            error=ResponseError(
                code="MODULE_ERROR",
                message=f"Module returned error: {str(e)}",
                details={"status_code": e.response.status_code},
            ),
        )
        return error_response.model_dump()

    return module_response