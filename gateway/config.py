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
"""

import os

SERVICES = {
    "sort": {
        "name": "sort",
        "language": "Go",
        "port": "8081",
        "url": os.getenv("SORT_MODULE_URL", "http://sort:8081"),
        "description": "String and number sorting microservice",
        "version": "1.0.0",
    },
}

GATEWAY_CONFIG = {
    "name": "gateway",
    "language": "Python",
    "port": "8000",
    "description": "FastAPI orchestration layer",
    "version": "1.0.0",
}


def get_all_services():
    """Return list of all services including gateway."""
    return [
        {
            **GATEWAY_CONFIG,
            "url": "http://localhost:8000",
            "status": "healthy" if _check_service_health(GATEWAY_CONFIG["port"]) else "unhealthy",
        },
        *[
            {**service, "status": "unknown"}
            for service in SERVICES.values()
        ],
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
        return SERVICES[service_name]["url"]
    raise ValueError(f"Service '{service_name}' not found")


def list_service_names() -> list[str]:
    """Get list of all available service names."""
    return list(SERVICES.keys())
