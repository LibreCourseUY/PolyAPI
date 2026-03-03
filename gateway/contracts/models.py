from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class RequestEnvelope(BaseModel):
    """Request envelope following the JSON contract standard."""
    request_id: str = Field(default="", description="UUID v4 string, auto-generated if not provided")
    module: str = Field(default="", description="Module identifier")
    version: str = Field(default="", description="Module version in semver format")
    payload: dict[str, Any] = Field(default_factory=dict, description="Module-specific payload")


class ResponseError(BaseModel):
    """Error details in the response envelope."""
    code: str = Field(..., description="Error code from the registry")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")


class SortPayload(BaseModel):
    """Payload for the sort endpoint."""
    items: list[Any] = Field(..., description="Array of strings or numbers to sort")
    order: Literal["asc", "desc"] = Field(default="asc", description="Sort order")


class SortResponseData(BaseModel):
    """Response data for successful sort operations."""
    sorted: list[Any] = Field(..., description="Sorted array")
    item_type: Literal["string", "number"] = Field(..., description="Type of items in the array")
    count: int = Field(..., description="Number of items sorted")


class ResponseEnvelope(BaseModel):
    """Response envelope following the JSON contract standard."""
    request_id: str = Field(..., description="UUID v4 string matching the request")
    module: str = Field(..., description="Module identifier")
    version: str = Field(..., description="Module version in semver format")
    status: Literal["success", "error"] = Field(..., description="Operation status")
    data: Optional[SortResponseData] = Field(default=None, description="Response data on success")
    error: Optional[ResponseError] = Field(default=None, description="Error details on failure")


class ModuleInfo(BaseModel):
    """Information about a registered module."""
    name: str = Field(..., description="Module name")
    version: str = Field(..., description="Module version")
    url: str = Field(..., description="Module URL")
    status: Literal["healthy", "unhealthy", "unknown"] = Field(default="unknown", description="Module health status")


class ModulesListResponse(BaseModel):
    """Response containing list of registered modules."""
    modules: list[ModuleInfo] = Field(..., description="List of registered modules")
