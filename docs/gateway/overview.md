# Gateway Overview

The PolyAPI Gateway is a FastAPI-based orchestration layer that handles all incoming client requests and routes them to the appropriate module.

## What is the Gateway?

The gateway serves as the **single entry point** for all client requests. It provides:

- **API Abstraction**: Clients interact with a single API regardless of how many modules exist
- **Request Validation**: Ensures all requests follow the JSON contract format
- **Request Routing**: Directs requests to the correct module based on endpoint path
- **Response Normalization**: Ensures all responses follow the contract format
- **Auto-Documentation**: Generates interactive API documentation automatically

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gateway (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Health     │    │   Modules    │    │   Proxy      │  │
│  │   Endpoint   │    │   Endpoints  │    │   Routes     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Configuration & Schemas                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Responsibilities

### 1. Request Handling

The gateway receives client requests and:

1. Validates the request structure
2. Extracts the module name and payload
3. Creates a request envelope with:
   - Auto-generated `request_id` (if not provided)
   - Module name and version
   - Client payload

### 2. Module Proxying

For each configured module, the gateway:

1. Forwards the request to the module's HTTP endpoint
2. Waits for the module's response
3. Returns the response to the client

### 3. Error Handling

When a module returns an error:

1. The gateway parses the error response
2. Preserves the original error code and message
3. Returns a properly formatted error response to the client

## Configuration System

The gateway uses a configuration-driven approach:

### Module Definition

Modules are defined in `config.py`:

```python
SERVICES = {
    "sort": ModuleDefinition(
        name="sort",
        language="Go",
        port="8081",
        url="http://localhost:8081",
        description="String and number sorting microservice",
        version="1.0.0",
        paths=["/sort"],
        payload_schema=SortPayload,
    ),
}
```

### Payload Schemas

Payload schemas are defined in `schemas/modules/`:

```python
# schemas/modules/sort.py
from pydantic import BaseModel, Field
from typing import Any, Literal

class SortPayload(BaseModel):
    items: list[Any] = Field(..., description="Array to sort")
    order: Literal["asc", "desc"] = Field(default="asc")
```

## Request Flow

```
Client Request
      │
      ▼
┌─────────────┐
│  Validate   │
└─────────────┘
      │
      ▼
┌─────────────┐
│   Route     │────▶ /sort ──▶ Sort Module
└─────────────┘
      │
      ▼
┌─────────────┐
│   Proxy     │
└─────────────┘
      │
      ▼
┌─────────────┐
│   Response  │
└─────────────┘
      │
      ▼
Client Response
```

## Benefits

| Benefit | Description |
|---------|-------------|
| **Simplicity** | Clients interact with one API |
| **Flexibility** | Add modules without changing client code |
| **Type Safety** | Pydantic validation on all requests |
| **Documentation** | Auto-generated Swagger UI |
| **Observability** | Centralized logging and error handling |

## Related Documentation

- [Configuration Guide](configuration.md)
- [API Reference](api.md)
- [Creating a Module](../modules/creating.md)
- [JSON Contract](../contract/json-contract.md)
