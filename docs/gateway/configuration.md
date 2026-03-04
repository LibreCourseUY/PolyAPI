# Gateway Configuration

This guide explains how to configure the PolyAPI Gateway, including module definitions and payload schemas.

## Configuration Files

The gateway configuration is spread across several files:

```
gateway/
├── config.py                 # Main module configuration
├── schemas/
│   ├── __init__.py
│   ├── request.py           # Request schemas
│   └── modules/
│       ├── __init__.py       # Module registry
│       └── sort.py           # Sort module payload schema
└── contracts/
    └── models.py             # Contract models
```

## Module Configuration

### Defining a New Module

To add a new module, you need to:

1. Add the module definition to `config.py`
2. Create a payload schema in `schemas/modules/`
3. Register the schema in `schemas/modules/__init__.py`

### Step 1: Add Module Definition

Edit `gateway/config.py`:

```python
from gateway.schemas.modules.your_module import YourPayloadSchema

SERVICES = {
    "your_module": ModuleDefinition(
        name="your_module",
        language="Go",              # or "Python", "Rust", etc.
        port="8082",               # Internal port
        url="http://localhost:8082", # Module URL
        description="Your module description",
        version="1.0.0",
        paths=["/your_endpoint"],   # List of endpoint paths
        payload_schema=YourPayloadSchema, # Payload schema class
    ),
}
```

### Step 2: Create Payload Schema

Create `gateway/schemas/modules/your_module.py`:

```python
from pydantic import BaseModel, Field
from typing import Any

class YourPayloadSchema(BaseModel):
    """Payload schema for your module."""
    param1: str = Field(..., description="Description of param1")
    param2: int = Field(default=10, description="Description of param2")
    optional_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional data"
    )
```

### Step 3: Register the Schema

Edit `gateway/schemas/modules/__init__.py`:

```python
from gateway.schemas.modules.your_module import YourPayloadSchema

MODULE_PAYLOAD_SCHEMAS = {
    "sort": SortPayload,
    "your_module": YourPayloadSchema,  # Add your schema here
}

# ... rest of the file
```

## Configuration Options

### ModuleDefinition

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Unique module identifier |
| `language` | str | Yes | Programming language (Go, Python, Rust, etc.) |
| `port` | str | Yes | Internal port the module listens on |
| `url` | str | Yes | Full URL to the module |
| `description` | str | Yes | Human-readable description |
| `version` | str | Yes | Module version (semver) |
| `paths` | list[str] | Yes | List of endpoint paths |
| `payload_schema` | Type[BaseModel] | No | Pydantic schema for validation |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SORT_MODULE_URL` | `http://localhost:8081` | URL for the sort module |
| `ROOT_PATH` | `""` | Root path for the gateway |
| `LOG_LEVEL` | `INFO` | Logging level |

### Setting Environment Variables

=== "Linux/macOS"
    ```bash
    export SORT_MODULE_URL=http://localhost:8081
    ```

=== "Windows"
    ```cmd
    set SORT_MODULE_URL=http://localhost:8081
    ```

=== ".env file"
    ```bash
    SORT_MODULE_URL=http://localhost:8081
    ```

## Automatic Endpoint Generation

The gateway automatically creates endpoints based on the module configuration:

```python
# For a module defined as:
paths=["/sort", "/batch-sort"]

# These endpoints are automatically created:
POST /sort
POST /batch-sort
```

Each endpoint:
- Accepts POST requests
- Validates the payload against the module's schema
- Proxies the request to the module
- Returns the module's response

## Schema Examples

### Simple Schema

```python
from pydantic import BaseModel, Field

class FilterPayload(BaseModel):
    items: list[str] = Field(..., description="Items to filter")
    condition: str = Field(..., description="Filter condition")
```

### Schema with Nested Objects

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserPayload(BaseModel):
    user_id: str = Field(..., description="User identifier")
    metadata: dict = Field(default_factory=dict, description="User metadata")
    options: Optional[dict] = Field(None, description="Processing options")
```

### Schema with Custom Types

```python
from pydantic import BaseModel, Field
from typing import Literal

class SortPayload(BaseModel):
    items: list[int | float | str] = Field(..., description="Items to sort")
    order: Literal["asc", "desc"] = Field(default="asc", description="Sort direction")
```

## Advanced Configuration

### Multiple Endpoints per Module

```python
SERVICES = {
    "data_processor": ModuleDefinition(
        name="data_processor",
        language="Python",
        port="8083",
        url="http://localhost:8083",
        description="Data processing module",
        version="1.0.0",
        paths=["/process", "/batch", "/validate"],
        payload_schema=ProcessPayload,
    ),
}
```

### Dynamic URL Configuration

```python
import os

SERVICES = {
    "sort": ModuleDefinition(
        name="sort",
        language="Go",
        port="8081",
        url=os.getenv("SORT_MODULE_URL", "http://localhost:8081"),
        # ...
    ),
}
```

## Validation

The gateway validates:
- **Request structure**: Using Pydantic models
- **Payload schema**: Using module-specific schemas
- **Response format**: Ensuring contract compliance

## Related Documentation

- [API Reference](api.md)
- [Creating a Module](../modules/creating.md)
- [JSON Contract](../contract/json-contract.md)
