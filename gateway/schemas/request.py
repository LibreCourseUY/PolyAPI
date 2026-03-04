from pydantic import BaseModel, Field
from typing import Any, Optional, Type, Union


class GeneralRequest(BaseModel):
    """
    General request schema that wraps module-specific payloads.

    The payload field accepts any valid JSON value. For type safety,
    use the module-specific payload schemas from gateway.schemas.modules.
    """

    payload: Any = Field(..., description="Module-specific payload data")
    request_id: Optional[str] = Field(
        default=None, description="UUID v4 string, auto-generated if not provided"
    )


def create_request_model(
    module_name: str, payload_schema: Optional[Type[BaseModel]] = None
) -> Type[BaseModel]:
    """
    Factory function to create a request model for a specific module.

    Args:
        module_name: The name of the module
        payload_schema: Optional payload schema for the module

    Returns:
        A request model class configured for the module
    """
    if payload_schema is None:
        return GeneralRequest

    payload_field = Field(..., description="Module-specific payload data")

    class RequestWithSchema(BaseModel):
        payload: Any = payload_field
        request_id: Optional[str] = Field(
            default=None, description="UUID v4 string, auto-generated if not provided"
        )

        model_config = {"strict": False}

    RequestWithSchema.__name__ = f"{module_name.title()}Request"
    return RequestWithSchema
