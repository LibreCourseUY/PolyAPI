# Contributing to PolyAPI

Thank you for your interest in contributing to PolyAPI!

## Ways to Contribute

There are many ways to contribute:

- **Report Bugs**: Create issues for any bugs you find
- **Suggest Features**: Propose new features or improvements
- **Write Code**: Implement new modules, fix bugs, or add features
- **Improve Documentation**: Fix typos, add examples, write guides
- **Review Code**: Help review pull requests

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/fingdev/PolyAPI.git
cd PolyAPI
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Make your changes and ensure:
- Tests pass
- Code is properly formatted
- Documentation is updated

### 4. Commit Changes

```bash
git add .
git commit -m "Add feature: your feature description"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python (Gateway)

- Follow PEP 8
- Use type hints
- Use Pydantic for validation
- Run `ruff check .` before committing

```bash
cd gateway
ruff check .
ruff format .
```

### Go (Modules)

- Follow Go code conventions
- Run `go fmt` before committing
- Add tests for new features

```bash
cd modules/sort
go fmt ./...
go test ./...
```

## Project Structure

```
PolyAPI/
├── gateway/               # Python FastAPI gateway
│   ├── main.py           # Application entry point
│   ├── config.py         # Module configuration
│   ├── router/           # API routes
│   ├── schemas/          # Request/response schemas
│   ├── contracts/        # Contract models
│   └── tests/            # Test files
├── modules/              # Module implementations
│   └── sort/            # Sort module (Go)
├── docs/                 # Documentation
└── docker-compose.yml    # Docker composition
```

## Testing

### Run Gateway Tests

```bash
cd gateway
pytest tests/ -v
```

### Run All Tests

```bash
# Start required services
docker-compose up -d

# Run tests
cd gateway
pytest tests/ -v

# Clean up
docker-compose down
```

## Writing Tests

### Python Tests

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_your_feature():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/your_endpoint", json={...})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
```

### Go Tests

```go
func TestYourFunction(t *testing.T) {
    // Test implementation
}
```

## Documentation Guidelines

- Use Markdown for documentation
- Include code examples
- Keep sections concise
- Update related docs when changing APIs

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism gracefully

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions in GitHub Issues

## License

By contributing to PolyAPI, you agree that your contributions will be licensed under the MIT License.
