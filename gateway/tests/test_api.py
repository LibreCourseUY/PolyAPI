import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "gateway" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_list_modules():
    """Test the modules list endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/modules")
    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert len(data["modules"]) > 0


@pytest.mark.asyncio
async def test_sort_strings_asc():
    """Test sorting strings in ascending order."""
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
    assert data["data"]["item_type"] == "string"
    assert data["data"]["count"] == 3


@pytest.mark.asyncio
async def test_sort_numbers_desc():
    """Test sorting numbers in descending order."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort", json={"payload": {"items": [5, 2, 8, 1], "order": "desc"}}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["sorted"] == [8, 5, 2, 1]
    assert data["data"]["item_type"] == "number"
    assert data["data"]["count"] == 4


@pytest.mark.asyncio
async def test_sort_empty_array():
    """Test sorting an empty array returns error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort", json={"payload": {"items": [], "order": "asc"}}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "EMPTY_INPUT"


@pytest.mark.asyncio
async def test_sort_mixed_types():
    """Test sorting mixed types returns error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort", json={"payload": {"items": ["a", 1, "b"], "order": "asc"}}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "MIXED_TYPES"


@pytest.mark.asyncio
async def test_sort_invalid_order():
    """Test sorting with invalid order returns error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort", json={"payload": {"items": ["a", "b", "c"], "order": "invalid"}}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "INVALID_ORDER"


@pytest.mark.asyncio
async def test_invalid_json():
    """Test invalid JSON body returns error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort",
            content="not valid json",
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_request_id_propagation():
    """Test that request_id is propagated correctly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/sort",
            json={
                "request_id": "test-123",
                "payload": {"items": ["b", "a"], "order": "asc"},
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "test-123"
