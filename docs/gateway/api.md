# API Reference

Complete API reference for the PolyAPI Gateway.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

Check the health status of the gateway.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "ok",
  "gateway": "gateway",
  "version": "1.0.0"
}
```

---

### List Modules

Get a list of all registered modules.

**Endpoint:** `GET /modules`

**Response:**

```json
{
  "modules": [
    {
      "name": "sort",
      "version": "1.0.0",
      "url": "http://localhost:8081",
      "status": "unknown"
    }
  ]
}
```

---

### Get Module Info

Get detailed information about a specific module.

**Endpoint:** `GET /modules/{module_name}`

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `module_name` | string | Name of the module |

**Response:**

```json
{
  "name": "sort",
  "language": "Go",
  "port": "8081",
  "url": "http://localhost:8081",
  "description": "String and number sorting microservice",
  "version": "1.0.0",
  "endpoints": ["/sort"]
}
```

---

### Sort Module

Sort an array of strings or numbers.

**Endpoint:** `POST /sort`

**Request Body:**

```json
{
  "payload": {
    "items": ["banana", "apple", "cherry"],
    "order": "asc"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payload.items` | array | Yes | Array of strings or numbers to sort |
| `payload.order` | string | No | Sort order: "asc" (default) or "desc" |

**Success Response:**

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

| Field | Type | Description |
|-------|------|-------------|
| `data.sorted` | array | Sorted array |
| `data.item_type` | string | Type of items: "string" or "number" |
| `data.count` | integer | Number of items |

**Error Response (Empty Input):**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
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

**Error Response (Mixed Types):**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
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

**Error Response (Invalid Order):**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440003",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_ORDER",
    "message": "invalid order value, must be 'asc' or 'desc'",
    "details": null
  }
}
```

---

## Interactive Documentation

FastAPI provides interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## cURL Examples

### Health Check

```bash
curl http://localhost:8000/health
```

### List Modules

```bash
curl http://localhost:8000/modules
```

### Sort Strings

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["zebra", "ant", "mango"], "order": "asc"}}'
```

### Sort Numbers

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": [5, 2, 8, 1], "order": "desc"}}'
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 404 | Module not found |
| 422 | Unprocessable Entity (validation error) |
| 502 | Bad Gateway (module unreachable) |
| 500 | Internal Server Error |

## Error Response Format

All errors follow this format:

```json
{
  "request_id": "uuid-v4",
  "module": "module-name",
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
