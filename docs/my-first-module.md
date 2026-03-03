# My First Module

This guide walks you through creating your first module for PolyAPI from scratch. By the end, you'll have a working module that communicates with the gateway via the JSON contract.

## What We're Building

We'll create a simple "greet" module that:
- Accepts a name in the payload
- Returns a personalized greeting
- Follows the PolyAPI JSON contract

## Prerequisites

- Python 3.11+ (for local development)
- Go 1.21+ (for this example, but you can use any language)
- Docker and Docker Compose

## Step 1: Create the Module Directory

Create a new directory for your module under `modules/`:

```bash
mkdir -p modules/greet
cd modules/greet
```

## Step 2: Create the Go Module Files

Create the following files in your module directory:

### go.mod

```go
module greet

go 1.21
```

### main.go

```go
package main

import (
	"log"
	"net/http"
	"os"
)

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func main() {
	port := getEnv("PORT", "8082")

	http.HandleFunc("/greet", HandleGreet)
	http.HandleFunc("/health", HandleHealth)

	log.Printf("Starting greet module on port %s", port)
	log.Printf("Module: %s, Version: %s", moduleName, moduleVersion)

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
```

### handler.go

```go
package main

import (
	"encoding/json"
	"net/http"
	"time"
)

const (
	moduleName    = "greet"
	moduleVersion = "1.0.0"
)

// RequestEnvelope represents the incoming JSON contract request.
type RequestEnvelope struct {
	RequestID string      `json:"request_id"`
	Module    string      `json:"module"`
	Version   string      `json:"version"`
	Payload   GreetPayload `json:"payload"`
}

// GreetPayload contains the greeting request data.
type GreetPayload struct {
	Name string `json:"name"`
}

// ResponseEnvelope represents the outgoing JSON contract response.
type ResponseEnvelope struct {
	RequestID string       `json:"request_id"`
	Module    string       `json:"module"`
	Version   string       `json:"version"`
	Status    string       `json:"status"`
	Data      *GreetResponseData `json:"data"`
	Error     *ResponseError    `json:"error"`
}

// GreetResponseData contains the greeting result.
type GreetResponseData struct {
	Greeting string `json:"greeting"`
}

// ResponseError represents an error in the contract format.
type ResponseError struct {
	Code    string      `json:"code"`
	Message string      `json:"message"`
	Details interface{} `json:"details"`
}

// HealthResponse represents the health check response.
type HealthResponse struct {
	Status  string `json:"status"`
	Module  string `json:"module"`
	Version string `json:"version"`
}

func generateRequestID() string {
	return "req-" + time.Now().Format("20060102150405")
}

// HandleGreet processes the greet request.
func HandleGreet(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPost {
		resp := ResponseEnvelope{
			RequestID: generateRequestID(),
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    "INVALID_METHOD",
				Message: "Only POST method is allowed",
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusMethodNotAllowed)
		json.NewEncoder(w).Encode(resp)
		return
	}

	var req RequestEnvelope
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		resp := ResponseEnvelope{
			RequestID: generateRequestID(),
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    "INVALID_JSON",
				Message: "Invalid JSON format: " + err.Error(),
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(resp)
		return
	}

	requestID := req.RequestID
	if requestID == "" {
		requestID = generateRequestID()
	}

	if req.Payload.Name == "" {
		resp := ResponseEnvelope{
			RequestID: requestID,
			Module:    moduleName,
			Version:   moduleVersion,
			Status:    "error",
			Data:      nil,
			Error: &ResponseError{
				Code:    "INVALID_INPUT",
				Message: "Name is required",
				Details: nil,
			},
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(resp)
		return
	}

	resp := ResponseEnvelope{
		RequestID: requestID,
		Module:    moduleName,
		Version:   moduleVersion,
		Status:    "success",
		Data: &GreetResponseData{
			Greeting: "Hello, " + req.Payload.Name + "!",
		},
		Error: nil,
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}

// HandleHealth returns the health status of the module.
func HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := HealthResponse{
		Status:  "ok",
		Module:  moduleName,
		Version: moduleVersion,
	}
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(resp)
}
```

### Dockerfile

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /greet-service

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /greet-service .
EXPOSE 8082
CMD ["./greet-service"]
```

## Step 3: Register the Module in the Gateway

### Update gateway/config.py

Add your module to the SERVICES dictionary:

```python
SERVICES = {
    "sort": {
        "name": "sort",
        "language": "Go",
        "port": "8081",
        "url": os.getenv("SORT_MODULE_URL", "http://sort:8081"),
        "description": "String and number sorting microservice",
        "version": "1.0.0",
    },
    "greet": {  # Add this new entry
        "name": "greet",
        "language": "Go",
        "port": "8082",
        "url": os.getenv("GREET_MODULE_URL", "http://greet:8082"),
        "description": "Personalized greeting microservice",
        "version": "1.0.0",
    },
}
```

### Add a Route in gateway/router/routes.py

Add a new endpoint to proxy requests to your module:

```python
@router.post("/greet")
async def greet_person(request: Request):
    """Proxy request to the Go greet module."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    request_id = body.get("request_id", "")
    if not request_id:
        request_id = str(uuid.uuid4())

    greet_url = get_service_url("greet")

    envelope = RequestEnvelope(
        request_id=request_id,
        module=body.get("module", "greet"),
        version=body.get("version", "1.0.0"),
        payload=body.get("payload", {}),
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{greet_url}/greet",
                json=envelope.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            module_response = response.json()
    except httpx.ConnectError:
        error_response = ResponseEnvelope(
            request_id=request_id,
            module="greet",
            version="1.0.0",
            status="error",
            data=None,
            error=ResponseError(
                code="MODULE_UNREACHABLE",
                message="The greet module is not reachable",
                details={"url": greet_url},
            ),
        )
        return error_response.model_dump()

    return module_response
```

## Step 4: Update Docker Compose

Add your module to `docker-compose.yml`:

```yaml
services:
  gateway:
    # ... existing config
    environment:
      - SORT_MODULE_URL=http://sort:8081
      - GREET_MODULE_URL=http://greet:8082  # Add this

  sort:
    # ... existing config

  greet:  # Add this new service
    build:
      context: ./modules/greet
      dockerfile: Dockerfile
    container_name: polyapi-greet
    environment:
      - PORT=8082
    networks:
      - polyapi-net
    restart: unless-stopped
```

## Step 5: Write Documentation

Create `docs/modules/greet.md`:

```markdown
# Greet Module

The Greet module is a Go-based microservice that returns personalized greetings.

## Overview

| Property | Value |
|----------|-------|
| Language | Go |
| Version | 1.0.0 |
| Port | 8082 |

## API Reference

### Health Endpoint

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "module": "greet",
  "version": "1.0.0"
}
```

### Greet Endpoint

**Endpoint:** `POST /greet`

**Request:**
```json
{
  "payload": {
    "name": "World"
  }
}
```

**Response:**
```json
{
  "request_id": "...",
  "module": "greet",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "greeting": "Hello, World!"
  },
  "error": null
}
```

## Error Codes

| Code | Description |
|------|-------------|
| INVALID_INPUT | Name is required |
| INVALID_METHOD | Only POST allowed |
| INVALID_JSON | Malformed JSON |
```

## Step 6: Test Your Module

```bash
# Build and start all services
docker-compose up --build -d

# Test the greet endpoint
curl -X POST http://localhost:8000/greet \
  -H "Content-Type: application/json" \
  -d '{"payload": {"name": "PolyAPI"}}'

# Expected response:
# {
#   "request_id": "...",
#   "module": "greet",
#   "version": "1.0.0",
#   "status": "success",
#   "data": {
#     "greeting": "Hello, PolyAPI!"
#   },
#   "error": null
# }
```

## Summary

Congratulations! You've created your first PolyAPI module. The key concepts are:

1. **JSON Contract**: All modules communicate using the same request/response envelope format
2. **HTTP + JSON**: No shared databases or direct imports between modules
3. **Environment Configuration**: All settings come from environment variables
4. **Docker Networking**: Modules communicate internally through the Docker network

You can now create modules in any language following this same pattern!
