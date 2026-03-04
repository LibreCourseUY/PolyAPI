# Error Codes

This document provides a comprehensive list of error codes used in PolyAPI.

## Error Code Registry

| Code | Description | HTTP Status |
|------|-------------|--------------|
| `INVALID_INPUT` | Request payload failed validation | 400 |
| `EMPTY_INPUT` | Required input array is empty | 400 |
| `MIXED_TYPES` | Array contains mixed data types | 400 |
| `INVALID_ORDER` | Invalid sort order value | 400 |
| `UNSUPPORTED_TYPE` | Unsupported data type in array | 400 |
| `MODULE_UNREACHABLE` | Module is not responding | 502 |
| `CONTRACT_VIOLATION` | Response doesn't match contract | 500 |
| `INVALID_JSON` | Malformed JSON in request | 400 |
| `INVALID_METHOD` | Wrong HTTP method used | 405 |
| `MODULE_ERROR` | Module returned an error | 502 |

## Detailed Error Descriptions

### INVALID_INPUT

**Description:** The request payload failed validation. This could be due to:
- Missing required fields
- Wrong field types
- Invalid field values

**HTTP Status:** 400 Bad Request

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "validation failed for field 'items'",
    "details": {
      "field": "items",
      "issue": "required field missing"
    }
  }
}
```

---

### EMPTY_INPUT

**Description:** A required input (typically an array) is empty when it should contain items.

**HTTP Status:** 400 Bad Request

**Example:**

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

---

### MIXED_TYPES

**Description:** An array contains mixed data types when all items should be of the same type.

**HTTP Status:** 400 Bad Request

**Example:**

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
    "details": {
      "expected_type": "string",
      "found_types": ["string", "number"]
    }
  }
}
```

---

### INVALID_ORDER

**Description:** An invalid sort order value was provided. Valid values are "asc" or "desc".

**HTTP Status:** 400 Bad Request

**Example:**

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
    "details": {
      "provided_value": "invalid"
    }
  }
}
```

---

### UNSUPPORTED_TYPE

**Description:** The array contains data types that are not supported by the module.

**HTTP Status:** 400 Bad Request

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440004",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "UNSUPPORTED_TYPE",
    "message": "unsupported type in array",
    "details": {
      "unsupported_types": ["object", "null"]
    }
  }
}
```

---

### MODULE_UNREACHABLE

**Description:** The module is not responding to requests. This could be due to:
- Module is down
- Network issues
- Wrong URL configuration

**HTTP Status:** 502 Bad Gateway

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440005",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "MODULE_UNREACHABLE",
    "message": "The sort module is not reachable",
    "details": {
      "url": "http://sort:8081"
    }
  }
}
```

---

### CONTRACT_VIOLATION

**Description:** The response from the module doesn't follow the JSON contract format.

**HTTP Status:** 500 Internal Server Error

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440006",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "CONTRACT_VIOLATION",
    "message": "Module response does not match contract format",
    "details": {
      "missing_fields": ["status"]
    }
  }
}
```

---

### INVALID_JSON

**Description:** The request body contains malformed JSON.

**HTTP Status:** 400 Bad Request

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440007",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_JSON",
    "message": "malformed json in request body",
    "details": {
      "parse_error": "invalid character at position 15"
    }
  }
}
```

---

### INVALID_METHOD

**Description:** The wrong HTTP method was used for the endpoint.

**HTTP Status:** 405 Method Not Allowed

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440008",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "INVALID_METHOD",
    "message": "GET method not supported, use POST",
    "details": {
      "used_method": "GET",
      "supported_methods": ["POST"]
    }
  }
}
```

---

### MODULE_ERROR

**Description:** The module returned an error. This is a catch-all for module-specific errors.

**HTTP Status:** 502 Bad Gateway

**Example:**

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440009",
  "module": "sort",
  "version": "1.0.0",
  "status": "error",
  "data": null,
  "error": {
    "code": "MODULE_ERROR",
    "message": "Module returned error: 400 Bad Request",
    "details": {
      "status_code": 400,
      "original_error": "EMPTY_INPUT"
    }
  }
}
```

## Creating Custom Error Codes

When creating a new module, you can define custom error codes. It's recommended to follow the naming convention:

1. Use UPPERCASE_SNAKE_CASE
2. Prefix with a category (e.g., `VALIDATION_`, `PROCESSING_`)
3. Keep messages human-readable

### Example Custom Errors

```json
{
  "error": {
    "code": "VALIDATION_INVALID_EMAIL",
    "message": "email address format is invalid",
    "details": {
      "field": "email",
      "value": "not-an-email"
    }
  }
}
```

```json
{
  "error": {
    "code": "PROCESSING_TIMEOUT",
    "message": "processing exceeded time limit",
    "details": {
      "timeout_seconds": 30,
      "processing_time": 35
    }
  }
}
```

## Error Handling Best Practices

1. **Always return proper errors**: Don't expose raw stack traces
2. **Use appropriate HTTP status codes**: Match HTTP status to error type
3. **Include helpful details**: Provide context in the `details` field
4. **Log errors**: Keep server-side logs for debugging
5. **Validate early**: Catch errors at the gateway level when possible

## Related Documentation

- [JSON Contract](json-contract.md)
- [Modules Overview](../modules/overview.md)
- [Creating a Module](../modules/creating.md)
