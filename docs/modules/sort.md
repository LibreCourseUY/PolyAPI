# Sort Module

The Sort module is a Go-based microservice that provides string and number sorting capabilities. It follows the PolyAPI JSON contract standard and is accessible exclusively through the gateway.

## Overview

| Property | Value |
|----------|-------|
| Language | Go |
| Version | 1.0.0 |
| Port | 8081 |
| Protocol | HTTP + JSON |

## Functionality

The sort module accepts an array of either strings or numbers and returns them sorted in ascending or descending order. The module performs strict type validation to ensure all items in the array are of the same type.

## API Reference

### Health Endpoint

Check the health status of the sort module.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "ok",
  "module": "sort",
  "version": "1.0.0"
}
```

### Sort Endpoint

Sort an array of items.

**Endpoint:** `POST /sort`

**Request Schema:**

```json
{
  "request_id": "uuid-v4-string",
  "module": "sort",
  "version": "1.0.0",
  "payload": {
    "items": ["banana", "apple", "cherry"],
    "order": "asc"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | No | UUID v4 string, auto-generated if not provided |
| `module` | string | Yes | Must be "sort" |
| `version` | string | Yes | Module version (e.g., "1.0.0") |
| `payload.items` | array | Yes | Array of strings or numbers |
| `payload.order` | string | No | "asc" (default) or "desc" |

**Response Schema:**

```json
{
  "request_id": "uuid-v4-string",
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
| `data.sorted` | array | Sorted array of items |
| `data.item_type` | string | "string" or "number" |
| `data.count` | integer | Number of items sorted |

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|--------------|
| `EMPTY_INPUT` | The items array is empty | 400 |
| `MIXED_TYPES` | Array contains mixed types | 400 |
| `INVALID_ORDER` | Order is not "asc" or "desc" | 400 |
| `UNSUPPORTED_TYPE` | Array contains non-string/non-number items | 400 |

## Examples

### Sorting Strings (Ascending)

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["zebra", "ant", "mango"], "order": "asc"}}'
```

**Response:**

```json
{
  "request_id": "...",
  "module": "sort",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "sorted": ["ant", "mango", "zebra"],
    "item_type": "string",
    "count": 3
  },
  "error": null
}
```

### Sorting Numbers (Descending)

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": [5, 2, 8, 1], "order": "desc"}}'
```

**Response:**

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

### Error: Empty Array

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": [], "order": "asc"}}'
```

**Response:**

```json
{
  "request_id": "...",
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

### Error: Mixed Types

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["a", 1, "b"], "order": "asc"}}'
```

**Response:**

```json
{
  "request_id": "...",
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

### Error: Invalid Order

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["a", "b", "c"], "order": "invalid"}}'
```

**Response:**

```json
{
  "request_id": "...",
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

## Implementation Notes

### Algorithm

The sort module uses Go's built-in `sort` package:

- **Strings**: Uses `sort.Strings()` for ascending, `sort.Reverse(sort.StringSlice())` for descending
- **Numbers**: Uses `sort.Slice()` with custom comparison functions

### Complexity

- **Time Complexity**: O(n log n) where n is the number of items
- **Space Complexity**: O(n) for creating the sorted copy

### Type Handling

- JSON numbers are decoded as `float64` in Go
- Type detection is performed on the first item
- All subsequent items must match the detected type
