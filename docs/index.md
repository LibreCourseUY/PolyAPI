# PolyAPI - Polyglot Microservices Gateway

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/FastAPI-0.135+-blue.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

PolyAPI is a **polyglot microservices architecture** that demonstrates how to build production-ready APIs using multiple programming languages. It uses a Python FastAPI gateway for orchestration and language-agnostic JSON contracts for inter-module communication.

## Why PolyAPI?

Traditional monolithic APIs force you to choose a single programming language for your entire application. PolyAPI flips this paradigm by treating each functionality as an independent, language-agnostic module that communicates through a standardized JSON contract.

### Key Benefits

1. **Best Tool for the Job**: Each module can use the most appropriate language for its specific task
   - Go for high-performance microservices
   - Python for data processing and ML
   - Rust for system-level performance
   - Any language that supports HTTP + JSON

2. **Team Flexibility**: Teams can work in their preferred languages without being constrained by the project's main language

3. **Incremental Adoption**: Add new modules without rewriting existing code

4. **Learning Opportunity**: Developers can contribute in their language of choice

5. **Isolation**: Modules are independently deployable and scalable

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Client                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Gateway (FastAPI)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Validation │  │   Routing   │  │  Rate Limit │  │    Auth     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Sort Module     │  │  Filter Module   │  │  Your Module     │
│  (Go)            │  │  (Python)        │  │  (Any Language) │
│  Port: 8081      │  │  Port: 8082      │  │  Port: 8083      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## How It Works

1. **Client Request**: Client sends a request to the gateway with a payload
2. **Gateway Validation**: Gateway validates the request against the module's payload schema
3. **Envelope Wrapping**: Gateway wraps the payload in a `RequestEnvelope` with metadata
4. **Module Processing**: Gateway proxies the request to the appropriate module
5. **Module Response**: Module processes the request and returns a `ResponseEnvelope`
6. **Gateway Response**: Gateway returns the response to the client

## Features

- **Language Agnostic**: Write modules in any language that supports HTTP + JSON
- **Automatic Documentation**: OpenAPI/Swagger documentation generated automatically
- **Type Safety**: Pydantic models for request/response validation
- **Loose Coupling**: Modules communicate through standardized JSON contracts
- **Easy Extensibility**: Add new modules by simply updating the configuration
- **Schema Validation**: Gateway validates payloads against module-specific schemas
- **Request Tracking**: Every request has a unique ID for tracing

## Quick Example

### Sort Numbers

=== "Request"
    ```bash
    curl -X POST http://localhost:8000/sort \
      -H "Content-Type: application/json" \
      -d '{"payload": {"items": [5, 2, 8, 1], "order": "desc"}}'
    ```

=== "Response"
    ```json
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440000",
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

### Sort Strings

=== "Request"
    ```bash
    curl -X POST http://localhost:8000/sort \
      -H "Content-Type: application/json" \
      -d '{"payload": {"items": ["banana", "apple", "cherry"], "order": "asc"}}'
    ```

=== "Response"
    ```json
    {
      "request_id": "550e8400-e29b-41d4-a716-446655440001",
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

## Supported Languages

| Language | Use Case | Status | Example Modules |
|----------|----------|--------|-----------------|
| Python | Gateway, data processing | Stable | Gateway, orchestration |
| Go | Performance-critical modules | Stable | Sort module |
| Any | Your custom modules | Supported | Add your own! |

## Project Structure

```
PolyAPI/
├── docs/                    # Documentation
│   ├── getting-started/    # Getting started guides
│   ├── modules/            # Module development guides
│   ├── gateway/            # Gateway configuration
│   └── contract/           # JSON contract specification
├── gateway/                 # Main gateway (FastAPI)
│   ├── config.py           # Module configuration
│   ├── router/              # API routes
│   ├── schemas/             # Payload schemas
│   └── contracts/           # Contract models
├── modules/                 # Microservice modules
│   └── sort/                # Sort module (Go example)
└── docker-compose.yml       # Docker orchestration
```

## API Documentation

Once the gateway is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Get Started

Ready to dive in? Here's how to get started:

1. **[Installation](getting-started/installation.md)** - Set up your development environment
2. **[Quick Start](getting-started/quickstart.md)** - Run your first example
3. **[Architecture](getting-started/architecture.md)** - Understand the system design
4. **[JSON Contract](contract/json-contract.md)** - Learn the communication protocol
5. **[Creating a Module](modules/creating.md)** - Build your first module

## License

MIT License - see [CLA.md](CLA.md) for details.
