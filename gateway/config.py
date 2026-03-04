"""
Centralized configuration for PolyAPI services.

This module contains all service definitions and their configurations.
Each service is defined as a dictionary with the following keys:
- name: Service identifier used in the API
- language: Programming language of the service
- port: Internal port the service listens on
- url: Full URL to the service (including protocol and host)
- description: Human-readable description of what the service does
- version: Current version of the service
- paths: List of endpoint paths (e.g., ["/sort"])
- payload_schema: The Pydantic schema class for the module's payload
"""

import os
from typing import Any, Type

from pydantic import BaseModel


class ModuleDefinition:
    """Definition of a module including its configuration and payload schema."""

    def __init__(
        self,
        name: str,
        language: str,
        port: str,
        url: str,
        description: str,
        version: str,
        paths: list[str],
        payload_schema: Type[BaseModel] | None = None,
    ):
        self.name = name
        self.language = language
        self.port = port
        self.url = url
        self.description = description
        self.version = version
        self.paths = paths
        self.payload_schema = payload_schema

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "language": self.language,
            "port": self.port,
            "url": self.url,
            "description": self.description,
            "version": self.version,
            "paths": self.paths,
        }

    @property
    def endpoints(self) -> list[str]:
        """Get list of endpoint paths."""
        return self.paths


def _import_payload_schema(module_name: str) -> Type[BaseModel] | None:
    """Dynamically import the payload schema for a module."""
    try:
        from gateway.schemas.modules import get_payload_schema

        return get_payload_schema(module_name)
    except ImportError:
        return None


SERVICES: dict[str, ModuleDefinition] = {
    "sort": ModuleDefinition(
        name="sort",
        language="Go",
        port="8081",
        url=os.getenv("SORT_MODULE_URL", "http://localhost:8081"),
        description="String and number sorting microservice",
        version="1.0.0",
        paths=["/sort"],
        payload_schema=_import_payload_schema("sort"),
    ),
}


def get_all_services() -> list[dict[str, Any]]:
    """Return list of all services including gateway."""
    from gateway.config import GATEWAY_CONFIG, _check_service_health

    return [
        {
            **GATEWAY_CONFIG,
            "url": "http://localhost:8000",
            "status": "healthy"
            if _check_service_health(GATEWAY_CONFIG["port"])
            else "unhealthy",
        },
        *[{**service.to_dict(), "status": "unknown"} for service in SERVICES.values()],
    ]


def _check_service_health(port: str) -> bool:
    """Check if a service is healthy (placeholder for actual health check)."""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", int(port)))
        sock.close()
        return result == 0
    except Exception:
        return False


def get_service_url(service_name: str) -> str:
    """Get the URL for a specific service."""
    if service_name in SERVICES:
        return SERVICES[service_name].url
    raise ValueError(f"Service '{service_name}' not found")


def get_service_definition(service_name: str) -> ModuleDefinition | None:
    """Get the full module definition for a service."""
    return SERVICES.get(service_name)


def get_module_paths(module_name: str) -> list[str]:
    """Get the endpoint paths for a module."""
    if module_name in SERVICES:
        return SERVICES[module_name].paths
    return []


def get_module_payload_schema(module_name: str) -> Type[BaseModel] | None:
    """Get the payload schema for a module."""
    if module_name in SERVICES:
        return SERVICES[module_name].payload_schema
    return None


def list_service_names() -> list[str]:
    """Get list of all available service names."""
    return list(SERVICES.keys())


def list_modules() -> list[dict[str, Any]]:
    """Get list of all modules with their configurations."""
    return [service.to_dict() for service in SERVICES.values()]


GATEWAY_CONFIG = {
    "name": "gateway",
    "language": "Python",
    "port": "8000",
    "description": "FastAPI orchestration layer",
    "version": "1.0.0",
}
