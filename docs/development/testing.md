# Testing

This guide covers testing practices for PolyAPI.

## Running Tests

### Gateway Tests

```bash
cd gateway
pytest tests/ -v
```

### With Coverage

```bash
cd gateway
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Tests

```bash
cd gateway
pytest tests/test_api.py::test_sort_strings_asc -v
```

## Test Structure

```
gateway/tests/
├── __init__.py
└── test_api.py
```

## Writing Tests

### Basic API Test

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

### Module Test

```python
@pytest.mark.asyncio
async def test_sort_strings_asc():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort",
            json={"payload": {"items": ["zebra", "ant", "mango"], "order": "asc"}},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["sorted"] == ["ant", "mango", "zebra"]
```

### Error Test

```python
@pytest.mark.asyncio
async def test_sort_empty_array():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort", json={"payload": {"items": [], "order": "asc"}}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "EMPTY_INPUT"
```

## Integration Testing

### Start Services for Integration Tests

```bash
docker-compose up -d
```

### Test Against Running Services

```python
import httpx
import pytest

@pytest.mark.asyncio
async def test_integration():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/sort",
            json={"payload": {"items": [3, 1, 2], "order": "asc"}}
        )
    assert response.status_code == 200
    assert response.json()["data"]["sorted"] == [1, 2, 3]
```

## Mocking

### Mock External Services

```python
from unittest.mock import patch

@pytest.mark.asyncio
async def test_with_mocked_module():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = {
            "request_id": "test",
            "module": "sort",
            "version": "1.0.0",
            "status": "success",
            "data": {"sorted": [1, 2, 3], "item_type": "number", "count": 3},
            "error": None
        }
        
        mock_client.return_value.__aenter__.return_value.post.return_value.json.return_value = mock_response
        
        # Your test code here
```

## Test Fixtures

### Define Custom Fixtures

```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_using_fixture(client):
    response = await client.get("/health")
    assert response.status_code == 200
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r gateway/requirements.txt
      
      - name: Run tests
        run: |
          cd gateway
          pytest tests/ -v
```

## Best Practices

1. **Test Edge Cases**: Test empty inputs, max values, etc.
2. **Test Errors**: Ensure error handling works correctly
3. **Test Integration**: Test module communication
4. **Use Fixtures**: Reuse common test setup
5. **Keep Tests Fast**: Avoid slow external calls in unit tests

## Related Documentation

- [Contributing](contributing.md)
- [Gateway Configuration](../gateway/configuration.md)
