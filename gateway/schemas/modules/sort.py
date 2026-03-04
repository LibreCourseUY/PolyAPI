from pydantic import BaseModel, Field
from typing import Any, Literal


class SortPayload(BaseModel):
    """Payload schema for the sort module."""

    items: list[Any] = Field(..., description="Array of strings or numbers to sort")
    order: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort order: 'asc' for ascending, 'desc' for descending",
    )
