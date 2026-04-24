"""
Funding Aggregator - API Tests
"""
import pytest


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "FundingAggregator"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login(client):
    # Register first
    await client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "testpassword123",
    })
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_list_grants_empty(client):
    response = await client.get("/api/v1/grants/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_grant_not_found(client):
    response = await client.get(
        "/api/v1/grants/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
