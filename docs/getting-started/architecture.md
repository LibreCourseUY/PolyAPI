# Architecture Overview

This document provides a comprehensive overview of PolyAPI's architecture, design decisions, and system components.

## High-Level Architecture

```
                                    ┌─────────────────┐
                                    │    External     │
                                    │    Clients      │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   FastAPI       │
                                    │   Gateway       │
                                    │  (Python 3.12)  │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
           ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
           │     Sort      │       │    Future    │       │    Future    │
           │     Module    │       │    Module     │       │    Module    │
           │     (Go)      │       │   (Python)   │       │    (Rust)    │
           └───────────────┘       └───────────────┘       └───────────────┘
```

## Core Components

### 1. Gateway (Python/FastAPI)

The gateway is the single entry point for all client requests. It handles:

- **Request Validation**: Validates incoming requests using Pydantic models
- **Routing**: Routes requests to the appropriate module based on endpoint path
- **Request Envelope Creation**: Wraps client payloads in the JSON contract format
- **Response Processing**: Passes through module responses or transforms errors
- **Documentation**: Auto-generates OpenAPI/Swagger documentation

**Key Files:**
- `gateway/main.py` - FastAPI application setup
- `gateway/router/routes.py` - Request routing and proxy logic
- `gateway/config.py` - Module configuration
- `gateway/schemas/` - Request/response schemas

### 2. Modules

Modules are independent services that perform specific tasks. Each module:

- Exposes HTTP endpoints following the JSON contract
- Implements business logic in any language
- Returns responses in the standardized envelope format
- Handles its own validation and error cases

**Current Modules:**
- **Sort Module** (Go) - String and number sorting

### 3. JSON Contract

The JSON contract is the backbone of PolyAPI's polyglot architecture. It ensures:

- Language independence
- Loose coupling between modules
- Interface consistency
- Independent deployment

## Request Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│ Gateway  │────▶│  Module  │────▶│ Gateway  │────▶│  Client  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                                           │
                       │ 1. Receive request                        │
                       │ 2. Validate request                       │
                       │ 3. Create envelope                        │
                       │ 4. Route to module                        │
                       │                              7. Return    │
                       │                              response    │
                                          5. Forward to
                                          module via HTTP
                                          
                                          6. Receive
                                          module response
```

### Detailed Steps

1. **Client Request**: External client sends HTTP POST to gateway with JSON body
2. **Gateway Validation**: Gateway validates request against Pydantic models
3. **Request ID Injection**: If not provided, gateway generates UUID v4
4. **Module Forwarding**: Gateway forwards request to appropriate module
5. **Module Processing**: Module validates, processes, and returns response
6. **Response Transformation**: Gateway may transform or enrich the response
7. **Client Response**: Gateway returns contract-compliant JSON to client

## Design Principles

### 1. Language Agnosticism

Any language that can send/receive HTTP + JSON can participate in PolyAPI:

- **Python**: Rapid development, strong typing with Pydantic
- **Go**: Performance-critical services, simple deployment
- **Rust**: High-performance systems programming
- **Node.js**: I/O-heavy services
- **Java**: Enterprise applications

### 2. Loose Coupling

Modules don't import each other's code. They communicate exclusively through:

- HTTP endpoints
- JSON request/response envelopes

### 3. Contract-First Design

The JSON contract is defined first, then implementations follow:

```json
{
  "request_id": "uuid-v4",
  "module": "module-name",
  "version": "1.0.0",
  "payload": { }
}
```

### 4. Configuration-Driven

Adding a new module requires only:

1. Creating the module (any language)
2. Adding configuration in `config.py`
3. Creating a payload schema in `schemas/modules/`

No code changes needed in the gateway!

## Security Considerations

### Network Isolation

- Modules are not directly exposed to the internet
- Only the gateway listens on externally accessible ports
- Internal communication happens on a Docker network

### Input Validation

- Gateway validates all incoming requests using Pydantic
- Each module validates input before processing
- Error responses follow the contract format (no raw tracebacks)

### Environment Variables

- No hardcoded URLs or ports in code
- All configuration via environment variables
- Sensitive data should use Docker secrets or external config management

## Performance Characteristics

### Gateway

- **Async I/O**: Uses FastAPI's async capabilities for concurrent requests
- **Connection Pooling**: Reuses HTTP connections to modules
- **Timeout Handling**: Configurable timeouts for module calls

### Modules

Each module's performance depends on its implementation. The sort module, written in Go, provides:
- O(n log n) sorting complexity
- Low memory footprint
- High throughput

## Scalability

### Horizontal Scaling

- **Gateway**: Can run multiple instances behind a load balancer
- **Modules**: Each module can be scaled independently

### Vertical Scaling

- **Modules**: Can be optimized for specific hardware
- **Language Selection**: Choose the best language for the workload

## Future Enhancements

Possible improvements to the architecture:

1. **Service Discovery**: Replace static URLs with dynamic service discovery
2. **Authentication**: Add JWT or API key authentication at the gateway
3. **Rate Limiting**: Implement rate limiting per client/module
4. **Tracing**: Add distributed tracing with OpenTelemetry
5. **Caching**: Implement response caching for expensive operations
6. **Circuit Breakers**: Add resilience patterns for module failures

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Gateway | FastAPI | 0.135+ |
| Validation | Pydantic | 2.12+ |
| HTTP Client | httpx | 0.28+ |
| Documentation | Swagger UI | Built-in |
| Modules | Go | 1.21+ |
| Containers | Docker | Latest |

## Related Documentation

- [JSON Contract Specification](../contract/json-contract.md)
- [Gateway Configuration](../gateway/configuration.md)
- [Creating a Module](../modules/creating.md)
- [Error Codes](../contract/error-codes.md)
