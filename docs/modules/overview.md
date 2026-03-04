# Modules Overview

Modules are the core building blocks of PolyAPI. Each module is an independent microservice that performs a specific task, written in any programming language that supports HTTP and JSON.

## Table of Contents

1. [What is a Module?](#what-is-a-module)
2. [Module Architecture](#module-architecture)
3. [Current Modules](#current-modules)
4. [Anatomy of a Module](#anatomy-of-a-module)
5. [Module Requirements](#module-requirements)
6. [Request/Response Contract](#requestresponse-contract)
7. [Module Communication](#module-communication)
8. [Adding a New Module](#adding-a-new-module)
9. [Best Practices](#best-practices)

---

## What is a Module?

A module in PolyAPI is:

- **Independent**: Runs as its own process/service
- **Language Agnostic**: Can be written in any language (Go, Python, Rust, Node.js, etc.)
- **Contract-Compliant**: Uses the JSON contract format for communication
- **Self-Contained**: Has its own logic, data, and dependencies
- **Discovered**: Registered with the gateway for automatic routing
- **Versioned**: Follows semantic versioning

### Why Modules?

Modules enable a polyglot microservices architecture where:

1. Each service can use the best tool for its specific job
2. Teams can work in their preferred programming languages
3. Services can be developed, deployed, and scaled independently
4. New features can be added without modifying existing code

---

## Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Gateway                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │   Validation │  │    Routing    │  │  Discovery    │        │
│  └───────────────┘  └───────────────┘  └───────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │   Sort   │ │ Filter   │ │  Upper   │
             │  Module  │ │  Module  │ │  Module  │
             └──────────┘ └──────────┘ └──────────┘
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Entry Point** | Main function that starts the HTTP server |
| **Request Handler** | Processes incoming requests |
| **Response Handler** | Formats and sends responses |
| **Health Check** | Returns module status |
| **Error Handler** | Manages error cases |

---

## Current Modules

### Sort Module

| Property | Value |
|----------|-------|
| Name | sort |
| Language | Go |
| Version | 1.0.0 |
| Port | 8081 |
| Endpoint | `/sort` |
| Description | String and number sorting microservice |

**Features:**
- Sort strings alphabetically (ascending/descending)
- Sort numbers (ascending/descending)
- Automatic type detection (string vs number)
- Input validation
- Comprehensive error handling

**Payload Schema:**
```python
class SortPayload(BaseModel):
    items: list[Any]  # List of strings or numbers to sort
    order: Literal["asc", "desc"] = "asc"  # Sort order
```

**Example Request:**
```json
{
  "payload": {
    "items": [5, 2, 8, 1],
    "order": "desc"
  }
}
```

**Example Response:**
```json
{
  "request_id": "...",
  "module": "sort",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "sorted": [8, 5, 2, 1],
    "item_type": "number",
    "count": 4
  },
  "error": null
}
```

---

## Anatomy of a Module

### Directory Structure

```
modules/
└── your_module/
    ├── main.go           # Entry point and server setup
    ├── handler.go        # Request handlers
    ├── go.mod            # Go module dependencies
    ├── go.sum            # Dependency checksums
    ├── Dockerfile        # Container definition
    └── README.md         # Module documentation (optional)
```

### 1. Entry Point

The entry point initializes the HTTP server and registers handlers:

```go
// main.go
package main

import (
    "log"
    "net/http"
)

func main() {
    // Register handlers
    http.HandleFunc("/your_endpoint", handleRequest)
    http.HandleFunc("/health", handleHealth)
    
    // Start server
    log.Printf("Starting module on port %s", ModulePort)
    log.Fatal(http.ListenAndServe(":"+ModulePort, nil))
}
```

### 2. Request Handler

The request handler processes incoming requests:

```go
// handler.go

func handleRequest(w http.ResponseWriter, r *http.Request) {
    // 1. Parse the request
    var req RequestEnvelope
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        sendError(w, req.RequestID, "INVALID_JSON", "malformed json", nil)
        return
    }
    
    // 2. Validate input
    if err := validatePayload(req.Payload); err != nil {
        sendError(w, req.RequestID, "INVALID_INPUT", err.Error(), nil)
        return
    }
    
    // 3. Process the request
    result := processData(req.Payload)
    
    // 4. Send success response
    sendSuccess(w, req.RequestID, result)
}

func validatePayload(payload map[string]interface{}) error {
    // Validation logic here
    return nil
}

func processData(payload map[string]interface{}) interface{} {
    // Processing logic here
    return map[string]interface{}{"result": "processed"}
}
```

### 3. Health Check

Every module must provide a health check endpoint:

```go
func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(HealthResponse{
        Status:  "ok",
        Module:  ModuleName,
        Version: ModuleVersion,
    })
}
```

### 4. Error Handler

Proper error handling is essential:

```go
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

func sendSuccess(w http.ResponseWriter, requestID string, data interface{}) {
    resp := ResponseEnvelope{
        RequestID: requestID,
        Module:    ModuleName,
        Version:   ModuleVersion,
        Status:    "success",
        Data:      data,
        Error:     nil,
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}
```

---

## Module Requirements

To be compatible with PolyAPI, a module must:

### 1. HTTP Server

```go
// Must listen on a specific port
http.ListenAndServe(":8082", nil)
```

### 2. JSON Support

```go
// Must parse JSON requests
json.NewDecoder(r.Body).Decode(&req)

// Must send JSON responses
json.NewEncoder(w).Encode(response)
```

### 3. JSON Contract

Must follow the request/response envelope format. See [JSON Contract](../contract/json-contract.md) for details.

### 4. Health Endpoint

```json
GET /health

Response:
{
  "status": "ok",
  "module": "your_module",
  "version": "1.0.0"
}
```

### 5. Error Handling

Must return proper error responses:

```json
{
  "request_id": "...",
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

---

## Request/Response Contract

### Request Envelope (Gateway → Module)

The gateway wraps client requests before forwarding to modules:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "sort",
  "version": "1.0.0",
  "payload": {
    "items": [5, 2, 8, 1],
    "order": "asc"
  }
}
```

### Response Envelope (Module → Gateway)

Modules must return responses in this format:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "sort",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "sorted": [1, 2, 5, 8],
    "item_type": "number",
    "count": 4
  },
  "error": null
}
```

### Client Request Format

Clients send requests to the gateway with a simplified format:

```json
{
  "payload": {
    "items": [5, 2, 8, 1],
    "order": "asc"
  }
}
```

The gateway adds the `request_id`, `module`, and `version` fields automatically.

---

## Module Communication

### Request Flow

```
Client                  Gateway                   Module
  │                       │                         │
  │  POST /sort          │                         │
  │─────────────────────>│                         │
  │                      │  POST /sort             │
  │                      │  + RequestEnvelope     │
  │                      │────────────────────────>│
  │                      │                         │
  │                      │  ResponseEnvelope       │
  │                      │<────────────────────────│
  │  ResponseEnvelope   │                         │
  │<─────────────────────│                         │
```

### Key Points

1. **Gateway as Proxy**: The gateway acts as a reverse proxy
2. **Envelope Wrapping**: Gateway adds metadata to requests
3. **Envelope Echoing**: Modules echo back request_id for tracking
4. **Status Field**: Always "success" or "error"
5. **Data/Error Mutually Exclusive**: Only one of data or error should be present

---

## Adding a New Module

See the detailed [Creating a Module](creating.md) guide for step-by-step instructions.

### Quick Steps

1. **Create the module** in `modules/<name>/`
2. **Implement the JSON contract** (request/response handlers)
3. **Create payload schema** in `gateway/schemas/modules/<name>.py`
4. **Register schema** in `gateway/schemas/modules/__init__.py`
5. **Register module** in `gateway/config.py`
6. **Test** the endpoint

---

## Best Practices

### 1. Single Responsibility

Each module should do one thing well:

```
✓ Good:  sort, uppercase, filter
✗ Bad:   sortAndFilterAndTransform
```

### 2. Error Handling

Always return proper error responses:

- Use standard error codes (see [Error Codes](../contract/error-codes.md))
- Include actionable error messages
- Provide details for debugging

### 3. Input Validation

Validate all input data:

```go
func validatePayload(payload map[string]interface{}) error {
    if payload == nil {
        return errors.New("payload is required")
    }
    
    // Validate required fields
    if _, ok := payload["required_field"]; !ok {
        return errors.New("required_field is required")
    }
    
    return nil
}
```

### 4. Logging

Use structured logging:

```go
log.Printf("Processing request: id=%s, module=%s", requestID, ModuleName)
```

### 5. Health Checks

Implement proper health endpoints:

```go
func handleHealth(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(HealthResponse{
        Status:  "ok",
        Module:  ModuleName,
        Version: ModuleVersion,
    })
}
```

### 6. Versioning

Follow semantic versioning:

- MAJOR (x.0.0): Breaking changes
- MINOR (1.x.0): New features
- PATCH (1.0.x): Bug fixes

### 7. Timeouts

Set appropriate timeouts for external calls:

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(url, json=data)
```

---

## Related Documentation

- [Creating a Module](creating.md) - Detailed module creation guide
- [Sort Module](sort.md) - Complete sort module implementation
- [JSON Contract](../contract/json-contract.md) - Contract specification
- [Error Codes](../contract/error-codes.md) - Standard error codes
- [Gateway Configuration](../gateway/configuration.md) - Configure modules
