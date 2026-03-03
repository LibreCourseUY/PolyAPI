# PolyAPI — A Polyglot Open Source API

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-FastAPI-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Go-1.21-blue.svg" alt="Go">
</p>

PolyAPI is a polyglot API architecture that demonstrates how to build production-ready APIs using multiple programming languages, each contributing isolated, well-defined modules. The system is orchestrated by a Python FastAPI gateway, and all inter-module communication happens exclusively via a JSON contract.

## Why Polyglot?

Different programming languages excel at different tasks. PolyAPI embraces this philosophy by allowing each module to be written in the language best suited for its purpose:

- **Go (Sort Module)**: Chosen for its performance, simplicity, and excellent standard library for building lightweight microservices

### Why Python for the Gateway?

Python was chosen as the gateway language for several important reasons:

1. **Accessibility**: Python's readable, English-like syntax lowers the barrier to entry for contributors. Developers can quickly understand and modify the gateway code regardless of their primary programming language.

2. **Ecosystem**: FastAPI provides excellent web framework capabilities with automatic OpenAPI documentation, native async support, and seamless Pydantic integration for request/response validation.

3. **Learning Curve**: New contributors can focus on learning the module-specific logic rather than struggling with complex gateway code.

4. **Community**: Python is one of the most popular languages in the world, making it easy to find contributors who can work on the orchestration layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP + JSON
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   PolyAPI Gateway (Python)                   │
│                        :8000                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ /health     │  │ /modules    │  │ /sort (proxy)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP + JSON Contract
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Sort Module (Go) :8081                         │
│  ┌─────────────┐  ┌─────────────────────────────────────┐  │
│  │ /health     │  │ /sort                                │  │
│  └─────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quickstart

```bash
# Clone and navigate to the project
git clone https://github.com/yourusername/polyapi.git
cd polyapi

# Start all services
make up

# Test the API
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": ["zebra", "ant", "mango"], "order": "asc"}}'

# Expected response:
# {
#   "request_id": "...",
#   "module": "sort",
#   "version": "1.0.0",
#   "status": "success",
#   "data": {
#     "sorted": ["ant", "mango", "zebra"],
#     "item_type": "string",
#     "count": 3
#   },
#   "error": null
# }

# View logs
make logs

# Stop services
make down
```

## Services

| Service | Language | Port | Description |
|---------|----------|------|-------------|
| gateway | Python | 8000 | FastAPI orchestration layer |
| sort | Go | 8081 | String and number sorting service |

## Adding New Modules

PolyAPI is designed to be easily extensible. To add a new module:

1. Create a new directory under `modules/`
2. Implement your service in any language
3. Follow the JSON contract standard (see `docs/CONTRACT.md`)
4. Register the module in `gateway/config.py`
5. Update documentation

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for detailed instructions.

## API Endpoints

### Gateway Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Gateway health check |
| GET | `/modules` | List all registered modules |
| POST | `/sort` | Proxy to Go sort module |

### Module Endpoints

| Module | Method | Path | Description |
|--------|--------|------|-------------|
| sort | GET | `/health` | Module health check |
| sort | POST | `/sort` | Sort items (strings or numbers) |

## Development

```bash
# Run linting
make lint

# Run tests
make test

# Clean up
make clean
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — System design and philosophy
- [Contract Specification](docs/CONTRACT.md) — JSON contract format and error codes
- [Contributing Guide](docs/CONTRIBUTING.md) — How to add new modules
- [Sort Module](docs/modules/sort.md) — Sort module reference
- [Contributor License Agreement](CLA.md) — Terms for contributing

## License

MIT License — see [LICENSE](LICENSE) for details.
