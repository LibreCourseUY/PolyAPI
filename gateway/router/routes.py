import uuid
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request

from gateway.config import (
    GATEWAY_CONFIG,
    SERVICES,
    get_service_url,
    get_module_payload_schema,
)
from gateway.contracts.models import (
    ModuleInfo,
    ModulesListResponse,
    RequestEnvelope,
    ResponseEnvelope,
    ResponseError,
)
from gateway.schemas.request import GeneralRequest, create_request_model

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
            name=service.name,
            version=service.version,
            url=service.url,
            status="unknown",
        )
        for service in SERVICES.values()
    ]
    return ModulesListResponse(modules=modules)


@router.get("/modules/{module_name}")
async def get_module_info(module_name: str):
    """Get detailed information about a specific module."""
    if module_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    service = SERVICES[module_name]
    return {
        "name": service.name,
        "language": service.language,
        "port": service.port,
        "url": service.url,
        "description": service.description,
        "version": service.version,
        "endpoints": service.paths,
    }


async def proxy_to_module(
    module_name: str,
    module_path: str,
    request: GeneralRequest,
) -> dict[str, Any]:
    """
    Proxy a request to a module.

    Args:
        module_name: The name of the module to call
        module_path: The endpoint path on the module
        request: The general request containing the payload

    Returns:
        The module's response as a dictionary
    """
    request_id = request.request_id or str(uuid.uuid4())
    module_url = get_service_url(module_name)

    envelope = RequestEnvelope(
        request_id=request_id,
        module=module_name,
        version=SERVICES[module_name].version,
        payload=request.payload.model_dump()
        if hasattr(request.payload, "model_dump")
        else request.payload,
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{module_url}{module_path}",
                json=envelope.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            module_response = response.json()
    except httpx.ConnectError:
        error_response = ResponseEnvelope(
            request_id=request_id,
            module=module_name,
            version=SERVICES[module_name].version,
            status="error",
            data=None,
            error=ResponseError(
                code="MODULE_UNREACHABLE",
                message=f"The {module_name} module is not reachable",
                details={"url": module_url},
            ),
        )
        return error_response.model_dump()
    except httpx.HTTPStatusError as e:
        try:
            error_data = e.response.json()
            if "error" in error_data and "code" in error_data["error"]:
                return error_data
        except Exception:
            pass
        error_response = ResponseEnvelope(
            request_id=request_id,
            module=module_name,
            version=SERVICES[module_name].version,
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


def create_module_endpoint(module_name: str, module_path: str):
    """
    Factory function to create an endpoint for a module.

    Args:
        module_name: The name of the module
        module_path: The endpoint path on the module (e.g., "/sort")

    Returns:
        An async function that handles the endpoint
    """
    payload_schema = get_module_payload_schema(module_name)
    request_model = create_request_model(module_name, payload_schema)

    async def module_endpoint(request: request_model):
        """Proxy request to the {module_name} module."""
        return await proxy_to_module(module_name, module_path, request)

    module_endpoint.__name__ = f"{module_name}_{module_path.replace('/', '_')}_endpoint"
    return module_endpoint


def register_module_routes(router: APIRouter):
    """Register all module routes automatically from config."""
    for module_name, service in SERVICES.items():
        for path in service.paths:
            endpoint = create_module_endpoint(module_name, path)
            router.add_api_route(
                path,
                endpoint,
                methods=["POST"],
                name=f"{module_name}{path}",
                description=f"Proxy request to the {module_name} module",
            )


register_module_routes(router)
