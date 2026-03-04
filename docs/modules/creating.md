# Creating a Module

This guide walks you through creating a new module for PolyAPI.

## Overview

To create a new module, you need to:

1. Create the module service (any language)
2. Add configuration to the gateway
3. Create payload schema for validation

## Step 1: Create the Module Service

### Option A: Go Module

Create `modules/your_module/`:

```go
// main.go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type RequestEnvelope struct {
    RequestID string `json:"request_id"`
    Module    string `json:"module"`
    Version   string `json:"version"`
    Payload   map[string]interface{} `json:"payload"`
}

type ResponseEnvelope struct {
    RequestID string      `json:"request_id"`
    Module    string      `json:"module"`
    Version   string      `json:"version"`
    Status    string      `json:"status"`
    Data      interface{} `json:"data"`
    Error     *ErrorInfo  `json:"error"`
}

type ErrorInfo struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details interface{} `json:"details"`
}

func main() {
    http.HandleFunc("/your_endpoint", handleRequest)
    http.HandleFunc("/health", handleHealth)
    log.Fatal(http.ListenAndServe(":8082", nil))
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(map[string]string{
        "status": "ok",
        "module": "your_module",
        "version": "1.0.0",
    })
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
    var req RequestEnvelope
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        sendError(w, req.RequestID, "INVALID_JSON", "malformed json", nil)
        return
    }
    
    // Process the request
    result := processData(req.Payload)
    
    // Send success response
    resp := ResponseEnvelope{
        RequestID: req.RequestID,
        Module:    "your_module",
        Version:   "1.0.0",
        Status:    "success",
        Data:      result,
        Error:     nil,
    }
    json.NewEncoder(w).Encode(resp)
}

func processData(payload map[string]interface{}) interface{} {
    // Your processing logic here
    return map[string]interface{}{"result": "processed"}
}

func sendError(w http.ResponseWriter, requestID, code, message string, details interface{}) {
    resp := ResponseEnvelope{
        RequestID: requestID,
        Module:    "your_module",
        Version:   "1.0.0",
        Status:    "error",
        Data:      nil,
        Error:     &ErrorInfo{Code: code, Message: message, Details: details},
    }
    w.WriteHeader(http.StatusBadRequest)
    json.NewEncoder(w).Encode(resp)
}
```

### Option B: Python Module

```python
# main.py
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "module": "your_module",
        "version": "1.0.0"
    })

@app.route('/your_endpoint', methods=['POST'])
def handle_request():
    data = request.json
    
    # Process the request
    result = process_data(data.get('payload', {}))
    
    return jsonify({
        "request_id": data.get('request_id', str(uuid.uuid4())),
        "module": "your_module",
        "version": "1.0.0",
        "status": "success",
        "data": result,
        "error": None
    })

def process_data(payload):
    # Your processing logic here
    return {"result": "processed"}

if __name__ == '__main__':
    app.run(port=8082)
```

## Step 2: Add Gateway Configuration

### Create Payload Schema

Create `gateway/schemas/modules/your_module.py`:

```python
from pydantic import BaseModel, Field
from typing import Any

class YourModulePayload(BaseModel):
    """Payload schema for your_module."""
    param1: str = Field(..., description="First parameter")
    param2: int = Field(default=10, description="Second parameter")
    extra_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional data"
    )
```

### Register the Schema

Edit `gateway/schemas/modules/__init__.py`:

```python
from gateway.schemas.modules.sort import SortPayload
from gateway.schemas.modules.your_module import YourModulePayload  # Add this

MODULE_PAYLOAD_SCHEMAS = {
    "sort": SortPayload,
    "your_module": YourModulePayload,  # Add this
}
```

### Add Module Configuration

Edit `gateway/config.py`:

```python
from gateway.schemas.modules.your_module import YourModulePayload

SERVICES = {
    "sort": ModuleDefinition(
        name="sort",
        language="Go",
        port="8081",
        url=os.getenv("SORT_MODULE_URL", "http://localhost:8081"),
        description="String and number sorting microservice",
        version="1.0.0",
        paths=["/sort"],
        payload_schema=SortPayload,
    ),
    "your_module": ModuleDefinition(
        name="your_module",
        language="Go",  # or "Python", "Rust", etc.
        port="8082",
        url=os.getenv("YOUR_MODULE_URL", "http://localhost:8082"),
        description="Your module description",
        version="1.0.0",
        paths=["/your_endpoint"],
        payload_schema=YourModulePayload,
    ),
}
```

## Step 3: Test Your Module

### Start Your Module

```bash
cd modules/your_module
go run main.go
```

### Test the Endpoint

```bash
curl -X POST http://localhost:8000/your_endpoint \
  -H "Content-Type: application/json" \
  -d '{"payload": {"param1": "hello", "param2": 5}}'
```

Expected response:

```json
{
  "request_id": "...",
  "module": "your_module",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "result": "processed"
  },
  "error": null
}
```

## Required Endpoints

Every module must implement:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns module status |
| `/{endpoint}` | POST | Main processing endpoint |

## Health Check Response

```json
{
  "status": "ok",
  "module": "your_module",
  "version": "1.0.0"
}
```

## Error Handling

Always return proper error responses:

```json
{
  "request_id": "uuid-v4",
  "module": "your_module",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `INVALID_INPUT` | Request payload failed validation |
| `EMPTY_INPUT` | Required input is empty |
| `INVALID_TYPE` | Wrong data type |
| `PROCESSING_ERROR` | Internal processing error |

## Docker Support

Add a Dockerfile to your module:

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o server .

FROM alpine
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8082
CMD ["./server"]
```

## Best Practices

1. **Validate Input**: Always validate incoming data
2. **Return Errors**: Return proper error responses
3. **Health Check**: Implement `/health` endpoint
4. **Logging**: Add logging for debugging
5. **Versioning**: Use semantic versioning
6. **Documentation**: Document your module's API

## Related Documentation

- [Modules Overview](overview.md)
- [Sort Module](sort.md)
- [JSON Contract](../contract/json-contract.md)
- [Error Codes](../contract/error-codes.md)
- [Gateway Configuration](../gateway/configuration.md)
