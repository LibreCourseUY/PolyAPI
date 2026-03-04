# Quick Start

Get up and running with PolyAPI in just a few minutes.

## Prerequisites

Before you begin, make sure you have:
- Python 3.12+ installed
- Go 1.21+ installed (for modules)
- Docker and Docker Compose (optional)

## Step 1: Start the Services

=== "Local Development"

    **Terminal 1 - Start the Sort Module:**
    
    ```bash
    cd modules/sort
    go run main.go
    ```
    
    **Terminal 2 - Start the Gateway:**
    
    ```bash
    cd gateway
    uvicorn main:app --reload
    ```

=== "Docker Compose"

    ```bash
    docker-compose up --build
    ```

## Step 2: Test the Sort Endpoint

The gateway automatically routes requests to the appropriate module based on the endpoint path.

### Sort Strings (Ascending)

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "items": ["banana", "apple", "cherry"],
      "order": "asc"
    }
  }'
```

Response:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "sort",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "sorted": ["apple", "banana", "cherry"],
    "item_type": "string",
    "count": 3
  },
  "error": null
}
```

### Sort Numbers (Descending)

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "items": [5, 2, 8, 1],
      "order": "desc"
    }
  }'
```

Response:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
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

## Step 3: Explore the API

### Health Check

```bash
curl http://localhost:8000/health
```

### List Available Modules

```bash
curl http://localhost:8000/modules
```

### Get Module Info

```bash
curl http://localhost:8000/modules/sort
```

## Step 4: View Auto-Generated Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Error Handling Examples

### Empty Array

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": [], "order": "asc"}}'
```

Response:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "EMPTY_INPUT",
    "message": "input array is empty",
    "details": null
  }
}
```

### Mixed Types

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["a", 1, "b"], "order": "asc"}}'
```

Response:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440003",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "MIXED_TYPES",
    "message": "mixed types in array",
    "details": null
  }
}
```

## Next Steps

- [Architecture Overview](architecture.md) - Understand the system design
- [Creating a Module](../modules/creating.md) - Add your own module
- [JSON Contract](../contract/json-contract.md) - Learn the contract format
