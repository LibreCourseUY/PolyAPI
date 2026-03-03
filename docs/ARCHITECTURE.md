# PolyAPI Architecture

## Overview

PolyAPI is a polyglot microservices architecture that demonstrates how to build production-ready APIs using multiple programming languages. The system uses a Python FastAPI gateway for orchestration and language-agnostic JSON contracts for inter-module communication.

## Why FastAPI?

FastAPI was chosen as the gateway framework for several compelling reasons:

1. **Native Async Support**: FastAPI's async capabilities allow efficient handling of concurrent requests to multiple modules
2. **Automatic Documentation**: OpenAPI/Swagger documentation is generated automatically
3. **Pydantic Integration**: Built-in request/response validation using Pydantic models
4. **Performance**: Comparable to Node.js and Go in terms of raw performance
5. **Ecosystem**: Large ecosystem of middleware, authentication, and database integrations

## Polyglot Philosophy

PolyAPI embraces the principle that different tasks are best solved with different tools:

### Language Selection Criteria

- **Python**: Rapid development, strong typing with Pydantic, excellent for orchestration layers
- **Go**: Performance-critical services, simple deployment, excellent standard library
- **Future modules**: Could include Rust (performance), Node.js (I/O-heavy), Java (enterprise)

### Benefits

1. **Best Tool for the Job**: Each module can use the most appropriate language
2. **Team Flexibility**: Teams can work in their preferred languages
3. **Incremental Adoption**: New modules can be added without rewriting existing code
4. **Learning Opportunity**: Developers can contribute in their language of choice

## JSON Contract Decoupling

The JSON contract is the backbone of PolyAPI's polyglot architecture. It ensures that:

1. **Language Independence**: Any language that can send/receive JSON can participate
2. **Loose Coupling**: Modules don't import each other's code
3. **Interface Segregation**: The contract defines exactly what needs to be implemented
4. **Independent Deployment**: Modules can be updated independently

## Request Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│ Gateway  │────▶│  Module  │────▶│ Gateway  │────▶│  Client  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │                                           │
                      │ 1. Receive request                        │
                      │ 2. Validate contract                      │
                      │ 3. Generate request_id                    │
                      │                              6. Return    │
                      │                              contract     │
                      │                              response    │
                                         4. Forward to
                                         module via HTTP
                                         
                                         5. Receive
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

## Versioning Strategy

### Contract Versioning

The JSON contract uses Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes to contract structure
- **MINOR**: Backward-compatible additions
- **PATCH**: Bug fixes

### Module Versioning

Each module declares its version in the response envelope:

```json
{
  "module": "sort",
  "version": "1.0.0"
}
```

### Gateway Versioning

The gateway itself is versioned and may support multiple contract versions simultaneously.

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

## Future Enhancements

Possible improvements to the architecture:

1. **Service Discovery**: Replace static URLs with dynamic service discovery
2. **Authentication**: Add JWT or API key authentication at the gateway
3. **Rate Limiting**: Implement rate limiting per client/module
4. **Tracing**: Add distributed tracing with OpenTelemetry
5. **Caching**: Implement response caching for expensive operations
6. **Circuit Breakers**: Add resilience patterns for module failures
