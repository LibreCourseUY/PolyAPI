# Creating a Module

This comprehensive guide walks you through creating a new module for PolyAPI. By the end, you'll understand the complete process from setting up your module structure to registering it with the gateway.

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Step 1: Create the Module Service](#step-1-create-the-module-service)
4. [Step 2: Implement the JSON Contract](#step-2-implement-the-json-contract)
5. [Step 3: Create Payload Schema](#step-3-create-payload-schema)
6. [Step 4: Register the Module](#step-4-register-the-module)
7. [Step 5: Test Your Module](#step-5-test-your-module)
8. [Docker Support](#docker-support)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

A PolyAPI module is a standalone microservice that:

1. Listens on a specific port
2. Exposes endpoints for processing requests
3. Implements the JSON contract for request/response
4. Provides a health check endpoint
5. Can be written in any programming language

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | For gateway configuration |
| Your choice | Any | Go, Python, Rust, Node.js, etc. |
| HTTP server | Any | Must support JSON + HTTP |

---

## Module Structure

A typical module follows this structure:

```
modules/
└── your_module/
    ├── main.go (or main.py, main.rs, etc.)
    ├── handler.go (or handlers/)
    ├── go.mod (or requirements.txt, Cargo.toml)
    ├── Dockerfile
    └── README.md (optional)
```

### Key Components

Every module must implement:

| Component | Description | Required |
|-----------|-------------|----------|
| HTTP Server | Listens for requests | Yes |
| Health Endpoint | `/health` - Returns module status | Yes |
| Processing Endpoints | Handle client requests | Yes |
| JSON Contract | Request/Response format | Yes |

---

## Step 1: Create the Module Service

You can create modules in any programming language. Here are complete examples for the most common languages.

### Option A: Go Module

This is the most performant option and follows the existing sort module pattern.

#### 1. Create the module directory

```bash
mkdir -p modules/your_module
cd modules/your_module
```

#### 2. Initialize Go module

```bash
go mod init your_module
```

#### 3. Create the main implementation

```go
// main.go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "strings"
)

// RequestEnvelope represents the incoming JSON contract request
type RequestEnvelope struct {
    RequestID string                 `json:"request_id"`
    Module    string                 `json:"module"`
    Version   string                 `json:"version"`
    Payload   map[string]interface{} `json:"payload"`
}

// Error represents error information in the response
type Error struct {
    Code    string      `json:"code"`
    Message string      `json:"message"`
    Details interface{} `json:"details,omitempty"`
}

// ResponseEnvelope represents the JSON contract response
type ResponseEnvelope struct {
    RequestID string      `json:"request_id"`
    Module    string      `json:"module"`
    Version   string      `json:"version"`
    Status    string      `json:"status"`
    Data      interface{} `json:"data,omitempty"`
    Error     *Error      `json:"error,omitempty"`
}

// HealthResponse represents the health check response
type HealthResponse struct {
    Status  string `json:"status"`
    Module  string `json:"module"`
    Version string `json:"version"`
}

// Module configuration
const (
    ModuleName    = "uppercase"
    ModuleVersion = "1.0.0"
    ModulePort    = "8082"
)

func main() {
    http.HandleFunc("/uppercase", handleRequest)
    http.HandleFunc("/health", handleHealth)
    
    log.Printf("Starting %s module on port %s", ModuleName, ModulePort)
    log.Printf("Module: %s, Version: %s", ModuleName, ModuleVersion)
    
    log.Fatal(http.ListenAndServe(":"+ModulePort, nil))
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(HealthResponse{
        Status:  "ok",
        Module:  ModuleName,
        Version: ModuleVersion,
    })
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
    var req RequestEnvelope
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        sendError(w, req.RequestID, "INVALID_JSON", "malformed json", nil)
        return
    }
    
    // Get the text from payload
    text, ok := req.Payload["text"].(string)
    if !ok || text == "" {
        sendError(w, req.RequestID, "EMPTY_INPUT", "field 'text' is required", nil)
        return
    }
    
    // Process: convert to uppercase
    result := map[string]interface{}{
        "original": text,
        "uppercase": strings.ToUpper(text),
    }
    
    // Send success response
    resp := ResponseEnvelope{
        RequestID: req.RequestID,
        Module:    ModuleName,
        Version:   ModuleVersion,
        Status:    "success",
        Data:      result,
        Error:     nil,
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}

func sendError(w http.ResponseWriter, requestID, code, message string, details interface{}) {
    resp := ResponseEnvelope{
        RequestID: requestID,
        Module:    ModuleName,
        Version:   ModuleVersion,
        Status:    "error",
        Data:      nil,
        Error:     &Error{Code: code, Message: message, Details: details},
    }
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusBadRequest)
    json.NewEncoder(w).Encode(resp)
}
```

#### 4. Build and run

```bash
go run main.go
```

The module will start on `http://localhost:8082`.

---

### Option B: Python Module

Use Flask or FastAPI for Python modules.

#### 1. Create the module directory

```bash
mkdir -p modules/your_module
cd modules/your_module
```

#### 2. Create requirements.txt

```text
flask>=2.3.0
```

#### 3. Create the main implementation

```python
# main.py
from flask import Flask, request, jsonify
from pydantic import BaseModel, Field
from typing import Optional, Any
import uuid

app = Flask(__name__)

# Request/Response Models
class RequestEnvelope(BaseModel):
    request_id: str = ""
    module: str
    version: str
    payload: dict[str, Any]

class ErrorInfo(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None

class ResponseEnvelope(BaseModel):
    request_id: str
    module: str
    version: str
    status: str
    data: Optional[Any] = None
    error: Optional[ErrorInfo] = None

# Module configuration
MODULE_NAME = "uppercase"
MODULE_VERSION = "1.0.0"
MODULE_PORT = 8082

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "module": MODULE_NAME,
        "version": MODULE_VERSION
    })

@app.route('/uppercase', methods=['POST'])
def handle_request():
    try:
        data = request.json
        
        # Parse request
        req = RequestEnvelope(**data)
        
        # Get the text from payload
        text = req.payload.get("text", "")
        if not text:
            return jsonify(create_error_response(
                req.request_id or str(uuid.uuid4()),
                "EMPTY_INPUT",
                "field 'text' is required"
            )), 400
        
        # Process: convert to uppercase
        result = {
            "original": text,
            "uppercase": text.upper()
        }
        
        # Return success response
        return jsonify(create_success_response(
            req.request_id or str(uuid.uuid4()),
            result
        ))
        
    except Exception as e:
        return jsonify(create_error_response(
            str(uuid.uuid4()),
            "PROCESSING_ERROR",
            str(e)
        )), 500

def create_success_response(request_id: str, data: Any) -> dict:
    return {
        "request_id": request_id,
        "module": MODULE_NAME,
        "version": MODULE_VERSION,
        "status": "success",
        "data": data,
        "error": None
    }

def create_error_response(request_id: str, code: str, message: str, details: dict = None) -> dict:
    return {
        "request_id": request_id,
        "module": MODULE_NAME,
        "version": MODULE_VERSION,
        "status": "error",
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }

if __name__ == '__main__':
    print(f"Starting {MODULE_NAME} module on port {MODULE_PORT}")
    print(f"Module: {MODULE_NAME}, Version: {MODULE_VERSION}")
    app.run(host="0.0.0.0", port=MODULE_PORT)
```

#### 4. Install dependencies and run

```bash
pip install -r requirements.txt
python main.py
```

The module will start on `http://localhost:8082`.

---

### Option C: Node.js Module

#### 1. Create the module directory

```bash
mkdir -p modules/your_module
cd modules/your_module
npm init -y
npm install express
```

#### 2. Create the main implementation

```javascript
// main.js
const express = require('express');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

// Module configuration
const MODULE_NAME = 'uppercase';
const MODULE_VERSION = '1.0.0';
const MODULE_PORT = 8082;

// Health endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        module: MODULE_NAME,
        version: MODULE_VERSION
    });
});

// Main endpoint
app.post('/uppercase', (req, res) => {
    const { request_id, module, version, payload } = req.body;
    
    // Get the text from payload
    const text = payload?.text;
    if (!text) {
        return res.status(400).json({
            request_id: request_id || uuidv4(),
            module: MODULE_NAME,
            version: MODULE_VERSION,
            status: 'error',
            data: null,
            error: {
                code: 'EMPTY_INPUT',
                message: "field 'text' is required"
            }
        });
    }
    
    // Process: convert to uppercase
    const result = {
        original: text,
        uppercase: text.toUpperCase()
    };
    
    // Return success response
    res.json({
        request_id: request_id || uuidv4(),
        module: MODULE_NAME,
        version: MODULE_VERSION,
        status: 'success',
        data: result,
        error: null
    });
});

app.listen(MODULE_PORT, () => {
    console.log(`Starting ${MODULE_NAME} module on port ${MODULE_PORT}`);
    console.log(`Module: ${MODULE_NAME}, Version: ${MODULE_VERSION}`);
});
```

---

## Step 2: Implement the JSON Contract

Every module must implement the JSON contract. Here's a detailed breakdown:

### Request Format

The module receives requests in this format:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "uppercase",
  "version": "1.0.0",
  "payload": {
    "text": "hello world"
  }
}
```

### Response Format

The module must return responses in this format:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "uppercase",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "original": "hello world",
    "uppercase": "HELLO WORLD"
  },
  "error": null
}
```

### Required Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns module status |
| `/{your_endpoint}` | POST | Main processing endpoint |

---

## Step 3: Create Payload Schema

The gateway validates requests against payload schemas. This provides better error messages and type safety.

### Create the Schema File

Create `gateway/schemas/modules/uppercase.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional


class UppercasePayload(BaseModel):
    """Payload schema for the uppercase module."""
    text: str = Field(..., description="The text to convert to uppercase")
    preserve_spaces: bool = Field(
        default=True, 
        description="Whether to preserve spaces in the text"
    )
```

### Register the Schema

Edit `gateway/schemas/modules/__init__.py`:

```python
from pydantic import BaseModel

from gateway.schemas.modules.sort import SortPayload
from gateway.schemas.modules.uppercase import UppercasePayload  # Add this


MODULE_PAYLOAD_SCHEMAS: dict[str, type[BaseModel]] = {
    "sort": SortPayload,
    "uppercase": UppercasePayload,  # Add this
}


def get_payload_schema(module_name: str) -> type[BaseModel] | None:
    """Get the payload schema for a module."""
    return MODULE_PAYLOAD_SCHEMAS.get(module_name)


def list_module_payload_schemas() -> dict[str, type[BaseModel]]:
    """List all available module payload schemas."""
    return MODULE_PAYLOAD_SCHEMAS.copy()
```

### Schema Field Types

Use Pydantic fields to define your schema:

| Field Type | Description | Example |
|------------|-------------|---------|
| `str` | String | `name: str` |
| `int` | Integer | `age: int` |
| `float` | Float | `price: float` |
| `bool` | Boolean | `active: bool` |
| `list[T]` | List | `items: list[str]` |
| `dict[K, V]` | Dictionary | `data: dict[str, int]` |
| `Optional[T]` | Optional | `name: Optional[str]` |
| `Literal` | Enum | `order: Literal["asc", "desc"]` |

### Field Validation

Pydantic provides built-in validation:

```python
from pydantic import BaseModel, Field, field_validator
from typing import List

class MyPayload(BaseModel):
    # Required field
    name: str = Field(..., description="User's name")
    
    # Field with default
    age: int = Field(default=0, description="User's age")
    
    # Field with constraints
    email: str = Field(..., description="User's email")
    
    # List with item type
    tags: List[str] = Field(default_factory=list, description="Tags")
    
    # Custom validation
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v
```

---

## Step 4: Register the Module

Now register the module with the gateway configuration.

### Edit Gateway Configuration

Edit `gateway/config.py`:

```python
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
    # Add your new module here
    "uppercase": ModuleDefinition(
        name="uppercase",
        language="Go",
        port="8082",
        url=os.getenv("UPPERCASE_MODULE_URL", "http://localhost:8082"),
        description="Text uppercase conversion microservice",
        version="1.0.0",
        paths=["/uppercase"],
        payload_schema=_import_payload_schema("uppercase"),
    ),
}
```

---

## Step 5: Test Your Module

### Start the Module

```bash
# For Go
cd modules/your_module
go run main.go

# For Python
cd modules/your_module
python main.py

# For Node.js
cd modules/your_module
node main.js
```

### Start the Gateway

```bash
cd gateway
uvicorn main:app --reload --port 8000
```

### Test the Endpoint

```bash
# Test successful request
curl -X POST http://localhost:8000/uppercase \
  -H "Content-Type: application/json" \
  -d '{"payload": {"text": "hello world"}}'
```

Expected response:

```json
{
  "request_id": "...",
  "module": "uppercase",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "original": "hello world",
    "uppercase": "HELLO WORLD"
  },
  "error": null
}
```

### Test Error Handling

```bash
# Test missing required field
curl -X POST http://localhost:8000/uppercase \
  -H "Content-Type: application/json" \
  -d '{"payload": {}}'
```

Expected response (from gateway validation):

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["payload", "text"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

### Test Health Check

```bash
curl http://localhost:8082/health
```

Expected response:

```json
{
  "status": "ok",
  "module": "uppercase",
  "version": "1.0.0"
}
```

---

## Docker Support

### Dockerfile for Go Module

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o server .

# Runtime stage
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8082
CMD ["./server"]
```

### Dockerfile for Python Module

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8082
CMD ["python", "main.py"]
```

### Build and Run

```bash
# Build
docker build -t polyapi/uppercase .

# Run
docker run -p 8082:8082 polyapi/uppercase
```

### Using Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  uppercase:
    build: ./modules/your_module
    ports:
      - "8082:8082"
    environment:
      - MODULE_NAME=uppercase
      - MODULE_VERSION=1.0.0
```

---

## Best Practices

### 1. Input Validation

Always validate input, even if the gateway does validation:

```go
// Go example
func validatePayload(payload map[string]interface{}) error {
    text, ok := payload["text"].(string)
    if !ok || text == "" {
        return errors.New("field 'text' is required")
    }
    if len(text) > 1000 {
        return errors.New("text exceeds maximum length of 1000 characters")
    }
    return nil
}
```

### 2. Structured Logging

Use structured logging for better debugging:

```python
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("request_processed", extra={
    "request_id": request_id,
    "module": MODULE_NAME,
    "processing_time_ms": elapsed_ms
})
```

### 3. Graceful Shutdown

Handle shutdown signals properly:

```go
// Go example
func main() {
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
        <-sigCh
        log.Println("Shutting down...")
        // Cleanup
        os.Exit(0)
    }()
    
    // Start server
}
```

### 4. Timeouts

Set appropriate timeouts:

```python
# Python example
import httpx

async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(url, json=data)
```

### 5. Rate Limiting

Consider implementing rate limiting in your module:

```go
// Go example with simple rate limiting
var requests = make(chan time.Time, 100) // 100 requests per second

func init() {
    go func() {
        for {
            <-time.Tick(time.Second / 100)
        }
    }()
}

func rateLimit(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        select {
        case requests <- time.Now():
            next(w, r)
        default:
            http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
        }
    }
}
```

---

## Troubleshooting

### Module Not Reachable

```
ERROR: Exception in ASGI application
httpx.ConnectError: [Errno 111] Connection refused
```

**Solution**: Ensure your module is running and the port is correct.

### Invalid JSON Response

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for ResponseEnvelope
```

**Solution**: Ensure your module returns valid JSON matching the ResponseEnvelope schema.

### 404 Not Found

```
INFO: 172.24.0.1:56048 - "POST /uppercase HTTP/1.1" 404 Not Found
```

**Solution**: 
1. Check that the module path matches the gateway configuration
2. Verify the module endpoint is registered correctly

### Payload Validation Error

```
Input should be a valid dictionary
```

**Solution**: Ensure the gateway payload schema is properly registered and the request format is correct.

---

## Related Documentation

- [JSON Contract](../contract/json-contract.md) - Complete contract specification
- [Error Codes](../contract/error-codes.md) - Standard error codes
- [Gateway Configuration](../gateway/configuration.md) - Configure modules
- [Modules Overview](overview.md) - Module architecture
- [Sort Module](sort.md) - Example module implementation
