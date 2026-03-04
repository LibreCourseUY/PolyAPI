# Installation

This guide will help you set up your development environment for PolyAPI.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Required for the gateway |
| Docker | Latest | For containerized deployment |
| Go | 1.21+ | For building Go modules |
| Git | Any | For cloning the repository |

## Clone the Repository

```bash
git clone https://github.com/fingdev/PolyAPI.git
cd PolyAPI
```

## Local Development Setup

### 1. Install Python Dependencies

```bash
cd gateway
pip install -r requirements.txt
```

Or using the pyproject.toml:

```bash
cd gateway
pip install -e .
```

### 2. Install Go Dependencies (for modules)

```bash
cd modules/sort
go mod download
```

### 3. Start the Sort Module

```bash
cd modules/sort
go run main.go
```

The sort module will start on `http://localhost:8081`.

### 4. Start the Gateway

In a new terminal:

```bash
cd gateway
uvicorn main:app --reload --port 8000
```

The gateway will start on `http://localhost:8000`.

## Docker Setup

### Using Docker Compose

The easiest way to run the entire stack:

```bash
docker-compose up --build
```

This will start:
- Gateway on port 8000
- Sort module on port 8081

### Manual Docker Build

Build the gateway:

```bash
cd gateway
docker build -t polyapi/gateway .
```

Build the sort module:

```bash
cd modules/sort
docker build -t polyapi/sort .
```

## Verify Installation

### Health Check

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

### List Modules

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
      "url": "http://sort:8081",
      "status": "unknown"
    }
  ]
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SORT_MODULE_URL` | `http://localhost:8081` | URL for the sort module |
| `ROOT_PATH` | `""` | Root path for the gateway |
| `LOG_LEVEL` | `INFO` | Logging level |

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first API call
- [Architecture Overview](architecture.md) - Understand the system design
