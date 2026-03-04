from typing import Type
from pydantic import BaseModel

from gateway.schemas.modules.sort import SortPayload


MODULE_PAYLOAD_SCHEMAS: dict[str, Type[BaseModel]] = {
    "sort": SortPayload,
}


def get_payload_schema(module_name: str) -> Type[BaseModel] | None:
    """Get the payload schema for a module."""
    return MODULE_PAYLOAD_SCHEMAS.get(module_name)


def list_module_payload_schemas() -> dict[str, Type[BaseModel]]:
    """List all available module payload schemas."""
    return MODULE_PAYLOAD_SCHEMAS.copy()
