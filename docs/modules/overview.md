# Modules Overview

Modules are the core building blocks of PolyAPI. Each module is an independent microservice that performs a specific task.

## What is a Module?

A module is:

- **Independent**: Runs as its own process/service
- **Language Agnostic**: Can be written in any language
- **Contract-Comiant**: Uses the JSON contract format
- **Self-Contained**: Has its own logic and data

## Module Structure

```
modules/
└── your_module/
    ├── main.go           # Entry point
    ├── handler.go       # Request handlers
    ├── go.mod           # Dependencies
    └── Dockerfile       # Container definition
```

## Current Modules

### Sort Module

| Property | Value |
|----------|-------|
| Name | sort |
| Language | Go |
| Version | 1.0.0 |
| Port | 8081 |
| Description | String and number sorting |

**Features:**
- Sort strings alphabetically
- Sort numbers (ascending/descending)
- Type validation
- Error handling

## Anatomy of a Module

### 1. Entry Point

```go
// main.go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

func main() {
    http.HandleFunc("/sort", handleSort)
    http.HandleFunc("/health", handleHealth)
    log.Fatal(http.ListenAndServe(":8081", nil))
}
```

### 2. Request Handler

```go
// handler.go
func handleSort(w http.ResponseWriter, r *http.Request) {
    var req RequestEnvelope
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        sendError(w, "INVALID_JSON", "malformed json")
        return
    }
    
    // Process the request
    // ...
    
    // Send response
    json.NewEncoder(w).Encode(response)
}
```

### 3. Health Check

```go
func handleHealth(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(map[string]string{
        "status": "ok",
        "module": "sort",
        "version": "1.0.0",
    })
}
```

## Module Requirements

To be compatible with PolyAPI, a module must:

1. **Listen on HTTP**: Accept HTTP requests
2. **Handle JSON**: Parse and produce JSON
3. **Follow Contract**: Use request/response envelopes
4. **Health Endpoint**: Provide `/health` endpoint
5. **Error Handling**: Return proper error responses

## Request/Response Contract

### Request Envelope

```json
{
  "request_id": "uuid-v4-string",
  "module": "module-name",
  "version": "1.0.0",
  "payload": { }
}
```

### Response Envelope

```json
{
  "request_id": "uuid-v4-string",
  "module": "module-name",
  "version": "1.0.0",
  "status": "success",
  "data": { },
  "error": null
}
```

## Adding a New Module

See [Creating a Module](creating.md) for detailed instructions.

## Module Communication

```
Gateway ──────HTTP──────> Module
   │                      │
   │   Request Envelope   │
   │─────────────────────>│
   │                      │
   │   Response Envelope  │
   │<─────────────────────│
   │                      │
   ▼                      ▼
```

## Best Practices

1. **Single Responsibility**: Each module should do one thing well
2. **Error Handling**: Always return proper error responses
3. **Logging**: Log important events for debugging
4. **Validation**: Validate all input data
5. **Health Checks**: Implement proper health endpoints

## Related Documentation

- [Creating a Module](creating.md)
- [Sort Module](sort.md)
- [JSON Contract](../contract/json-contract.md)
- [Error Codes](../contract/error-codes.md)
