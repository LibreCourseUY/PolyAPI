# Installation

This guide will help you set up your development environment for PolyAPI. Follow these steps to get everything running locally.

## Prerequisites

Before installing PolyAPI, ensure you have the following tools:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Required for the gateway |
| Docker | Latest | For containerized deployment |
| Go | 1.21+ | For building Go modules |
| Git | Any | For cloning the repository |
| pip/uv | Latest | Python package manager |

### Verify Prerequisites

```bash
# Check Python version
python --version

# Check Go version
go version

# Check Docker version
docker --version

# Check Git version
git --version
```

## Clone the Repository

```bash
git clone https://github.com/your-repo/PolyAPI.git
cd PolyAPI
```

## Local Development Setup

### Option A: Manual Setup

#### 1. Set Up the Gateway

```bash
# Navigate to the gateway directory
cd gateway

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Or using the package manager:

```bash
cd gateway
pip install -e .
```

#### 2. Set Up a Module (Sort Module Example)

```bash
# Navigate to the sort module
cd modules/sort

# Install Go dependencies
go mod download

# Build the module
go build -o sort_server .
```

#### 3. Start the Sort Module

```bash
cd modules/sort
./sort_server
```

You should see output like:

```
2026/03/04 13:46:11 Starting sort module on port 8081
2026/03/04 13:46:11 Module: sort, Version: 1.0.0
```

The sort module will start on `http://localhost:8081`.

#### 4. Start the Gateway

Open a new terminal:

```bash
# Activate the virtual environment if not already active
cd gateway
source venv/bin/activate

# Start the gateway
uvicorn main:app --reload --port 8000
```

You should see output like:

```
INFO:     Started server process [10]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

The gateway will start on `http://localhost:8000`.

---

### Option B: Using Docker

#### Using Docker Compose (Recommended)

The easiest way to run the entire stack:

```bash
# Build and start all services
docker-compose up --build
```

This will start:
- Gateway on port 8000
- Sort module on port 8081

#### Manual Docker Build

If you want to run services individually:

**Build the gateway:**

```bash
cd gateway
docker build -t polyapi/gateway .
```

**Run the gateway:**

```bash
docker run -p 8000:8000 polyapi/gateway
```

**Build the sort module:**

```bash
cd modules/sort
docker build -t polyapi/sort .
```

**Run the sort module:**

```bash
docker run -p 8081:8081 polyapi/sort
```

---

## Verify Installation

### 1. Gateway Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "gateway": "gateway",
  "version": "1.0.0"
}
```

### 2. List Modules

```bash
curl http://localhost:8000/modules
```

Expected response:

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

### 3. Test the Sort Module

```bash
curl -X POST http://localhost:8000/sort \
  -H "Content-Type: application/json" \
  -d '{"payload": {"items": [5, 2, 8, 1], "order": "asc"}}'
```

Expected response:

```json
{
  "request_id": "...",
  "module": "sort",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "sorted": [1, 2, 5, 8],
    "item_type": "number",
    "count": 4
  },
  "error": null
}
```

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Environment Variables

Configure your PolyAPI deployment using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SORT_MODULE_URL` | `http://localhost:8081` | URL for the sort module |
| `UPPERCASE_MODULE_URL` | `http://localhost:8082` | URL for the uppercase module |
| `ROOT_PATH` | `""` | Root path for the gateway (useful for reverse proxies) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `GATEWAY_HOST` | `0.0.0.0` | Host to bind the gateway to |
| `GATEWAY_PORT` | `8000` | Port to bind the gateway to |

### Example: Using Environment Variables

```bash
# Start gateway with custom configuration
SORT_MODULE_URL=http://my-sort-service:8081 \
LOG_LEVEL=DEBUG \
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker Compose Environment Variables

```yaml
services:
  gateway:
    environment:
      - SORT_MODULE_URL=http://sort:8081
      - LOG_LEVEL=DEBUG
```

---

## Project Structure

After installation, your project should look like:

```
PolyAPI/
├── docs/                         # Documentation
│   ├── getting-started/
│   ├── modules/
│   ├── gateway/
│   └── contract/
├── gateway/                       # Main gateway (FastAPI)
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Module configuration
│   ├── router/                   # API routes
│   │   └── routes.py             # Route definitions
│   ├── schemas/                  # Payload schemas
│   │   ├── request.py            # Request models
│   │   └── modules/              # Module-specific schemas
│   │       ├── __init__.py
│   │       └── sort.py
│   └── contracts/                # Contract models
│       └── models.py
├── modules/                       # Microservice modules
│   └── sort/                     # Sort module (Go)
│       ├── main.go
│       ├── handler.go
│       ├── go.mod
│       └── Dockerfile
├── docker-compose.yml            # Docker orchestration
├── pyproject.toml               # Python project config
└── README.md
```

---

## Common Issues

### Port Already in Use

If you get an error about port 8000 already being in use:

```bash
# Find the process using the port
lsof -i :8000
# or on macOS
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Python Import Errors

If you get import errors:

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Go Module Errors

If Go can't find modules:

```bash
cd modules/sort
go mod tidy
go mod download
```

### Docker Permission Denied

If you get permission errors with Docker:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Or run with sudo (not recommended for production)
sudo docker-compose up
```

---

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first API call
- [Architecture Overview](architecture.md) - Understand the system design
- [JSON Contract](../contract/json-contract.md) - Learn the communication protocol
- [Creating a Module](../modules/creating.md) - Build your first module
