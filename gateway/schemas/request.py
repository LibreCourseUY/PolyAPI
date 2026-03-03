from pydantic import BaseModel, Field
from typing import Any

class GeneralRequest(BaseModel):
    payload: Any