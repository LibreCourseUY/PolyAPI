# PolyAPI - Polyglot Microservices Gateway

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/FastAPI-0.135+-blue.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/docker/pulls/polyapi/gateway.svg" alt="Docker Pulls">
</p>

PolyAPI is a **polyglot microservices architecture** that demonstrates how to build production-ready APIs using multiple programming languages. It uses a Python FastAPI gateway for orchestration and language-agnostic JSON contracts for inter-module communication.

## Features

- **Language Agnostic**: Write modules in any language that supports HTTP + JSON
- **Automatic Documentation**: OpenAPI/Swagger documentation generated automatically
- **Type Safety**: Pydantic models for request/response validation
- **Loose Coupling**: Modules communicate through standardized JSON contracts
- **Easy Extensibility**: Add new modules by simply updating the configuration

## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│ Gateway  │────▶│  Module  │
└──────────┘     └──────────┘     └──────────┘
                       │                 │
                       │            ┌────┴────┐
                       │            │   Go    │
                       │            │ Python  │
                       │            │  Rust   │
                       │            └─────────┘
                       ▼
                ┌──────────┐
                │ Response │
                └──────────┘
```

## Quick Example

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

## Why PolyAPI?

1. **Best Tool for the Job**: Each module can use the most appropriate language
2. **Team Flexibility**: Teams can work in their preferred languages
3. **Incremental Adoption**: Add new modules without rewriting existing code
4. **Learning Opportunity**: Developers can contribute in their language of choice

## Supported Languages

| Language | Use Case | Status |
|----------|----------|--------|
| Python | Gateway, orchestration | Stable |
| Go | Performance-critical modules | Stable |
| More coming soon | Your favorite language | Planning |

## Get Started

Ready to dive in? Here's how to get started:

1. **[Installation](getting-started/installation.md)** - Set up your development environment
2. **[Quick Start](getting-started/quickstart.md)** - Run your first example
3. **[Architecture](getting-started/architecture.md)** - Understand the system design

## License

MIT License - see [CLA.md](../CLA.md) for details.
