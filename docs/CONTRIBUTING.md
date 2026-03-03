# Contributing to PolyAPI

Thank you for your interest in contributing to PolyAPI! This guide will help you understand how to add new modules and contribute to the project.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Adding a New Module](#adding-a-new-module)
3. [Module Requirements](#module-requirements)
4. [Docker Networking](#docker-networking)
5. [Code Style](#code-style)
6. [Testing](#testing)
7. [PR Checklist](#pr-checklist)
8. [CLA Requirement](#cla-requirement)

## Architecture Overview

PolyAPI uses a microservices architecture where:

- **Gateway** (Python FastAPI): The only externally accessible service. Routes requests to modules.
- **Modules**: Individual services written in any language. Communicate exclusively via JSON over HTTP.
- **Network**: All inter-module communication happens through an internal Docker network (`polyapi-net`).

```
Client → Gateway (port 8000) → Modules (internal network)
```

## Adding a New Module

Adding a new module to PolyAPI involves several steps:

### Step 1: Create the Module Directory

Create a new directory under `modules/` with your module name:

```
modules/
└── mymodule/
    ├── main.go        # or main.rs, main.ts, etc.
    ├── handler.go     # or equivalent
    ├── Dockerfile
    └── go.mod         # or package.json, Cargo.toml, etc.
```

### Step 2: Implement the JSON Contract

Your module must implement the JSON contract as defined in [CONTRACT.md](CONTRACT.md):

- Accept request envelopes with `request_id`, `module`, `version`, and `payload`
- Return response envelopes with `status`, `data`, and `error` fields
- Implement proper error handling with error codes
- All communication must be HTTP + JSON (no shared memory, databases, or direct imports)

### Step 3: Implement Health Endpoint

Add a health check endpoint:

```json
GET /health

Response:
{
  "status": "ok",
  "module": "mymodule",
  "version": "1.0.0"
}
```

### Step 4: Create Dockerfile

Every module **must** have a Dockerfile. The Dockerfile should:

- Expose only the internal port (not externally accessible)
- Use environment variables for configuration
- Be built as part of the orchestrator docker-compose

Example:

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /mymodule

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /mymodule .
EXPOSE 8082
CMD ["./mymodule"]
```

### Step 5: Register in Gateway Configuration

Update the gateway configuration to include your module:

1. **Register service** in `gateway/config.py`:
   ```python
   SERVICES = {
       "mymodule": {
           "name": "mymodule",
           "language": "Go",  # or your language
           "port": "8082",
           "url": os.getenv("MYMODULE_URL", "http://mymodule:8082"),
           "description": "Description of what your module does",
           "version": "1.0.0",
       },
   }
   ```

2. **Add route** in `gateway/router/routes.py`:
   Create a new endpoint that proxies to your module.

### Step 6: Update Docker Compose

Add your module to `docker-compose.yml`:

```yaml
services:
  gateway:
    # ... existing config
    environment:
      - MYMODULE_URL=http://mymodule:8082

  mymodule:
    build:
      context: ./modules/mymodule
      dockerfile: Dockerfile
    container_name: polyapi-mymodule
    environment:
      - PORT=8082
    volumes:
      - mymodule-data:/app/data
    networks:
      - polyapi-net
    restart: unless-stopped

volumes:
  mymodule-data:
    name: polyapi-mymodule-data
```

### Step 7: Write Documentation

Create documentation in `docs/modules/`:

```markdown
docs/modules/
└── mymodule.md
```

Include:
- Module description
- API reference (endpoints, request/response schemas)
- Examples
- Error codes
- Implementation notes

## Module Requirements

### Must Have

- [ ] JSON contract compliance (request/response envelopes)
- [ ] Health endpoint (`GET /health`)
- [ ] Proper error handling with contract error codes
- [ ] Environment-based configuration (no hardcoded URLs/ports)
- [ ] **Dockerfile** for containerization
- [ ] **Named volume** for data persistence (e.g., `mymodule-data:/app/data`)
- [ ] Module documentation
- [ ] Registered in `gateway/config.py`
- [ ] Route added in `gateway/router/routes.py`
- [ ] Service added to `docker-compose.yml`
- [ ] Communicates via HTTP + JSON over internal Docker network

### Should Have

- [ ] Unit tests
- [ ] Input validation
- [ ] Logging
- [ ] Graceful shutdown

### Nice to Have

- [ ] Metrics endpoint
- [ ] OpenAPI/Swagger documentation
- [ ] Rate limiting

## Docker Networking

### Internal Network

All modules communicate through the `polyapi-net` Docker network. This network:

- Is defined in `docker-compose.yml`
- Is accessible only to containers running in the same compose project
- Is NOT exposed externally (only the gateway has exposed ports)

### Module Communication

Modules MUST NOT:
- Expose ports externally (remove `ports` from docker-compose for modules)
- Connect to external services directly (go through the gateway)
- Share databases or filesystems with other modules

Modules MUST:
- Listen on the port specified in their `PORT` environment variable
- Respond to `/health` for health checks
- Return JSON contract-compliant responses

## Code Style

### Go

- Follow [Effective Go](https://golang.org/doc/effective_go) conventions
- Use `go vet` and check for warnings
- Add GoDoc comments on all exported functions
- Run `golint` if available

Example:

```go
// HandleSort processes the sort request.
func HandleSort(w http.ResponseWriter, r *http.Request) {
    // implementation
}
```

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to all functions
- Run `ruff check` for linting

Example:

```python
async def sort_items(request: Request) -> ResponseEnvelope:
    """Sort items via the sort module.
    
    Args:
        request: The incoming HTTP request with sort payload.
    
    Returns:
        ResponseEnvelope with sorted items or error.
    """
    pass
```

### General

- Use meaningful variable and function names
- Keep functions focused and small
- Write comments that explain *why*, not *what*
- Handle errors gracefully (no raw exceptions to clients)

## Testing

### Local Testing

```bash
# Build and start services
make up

# Run test suite
make test

# View logs
make logs
```

### Manual Testing

Test through the gateway (the only externally accessible service):

```bash
# Test via gateway
curl -X POST http://localhost:8000/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"payload": {}}'
```

## PR Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the style guide for the relevant language
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation is updated
- [ ] Module works end-to-end with `make up`
- [ ] No hardcoded URLs or ports
- [ ] Error responses follow the contract format
- [ ] Commit messages are clear and descriptive
- [ ] Service registered in `gateway/config.py`
- [ ] Route added in `gateway/router/routes.py`
- [ ] Module added to `docker-compose.yml`
- [ ] Module Dockerfile exists and is properly configured
- [ ] Module does NOT expose external ports (internal network only)
- [ ] You have read and agree to the [CLA](CLA.md)

## CLA Requirement

Before your contribution can be accepted, you must sign the [Contributor License Agreement (CLA)](CLA.md). By submitting a pull request, patch, or other form of contribution to the Project, you agree to be bound by the terms of the CLA.

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions in the repository
- Check existing issues and PRs before creating new ones

We look forward to your contributions!
