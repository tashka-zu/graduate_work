import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise.context import TortoiseContext


# Ensure app config picks up test settings BEFORE importing `main`.
DB_FILE = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex}.sqlite3")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(DB_FILE).as_posix()}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DEFAULT_CITY_ID"] = "1"
os.environ["DEFAULT_CITY_NAME"] = "Unknown"

from authentication.models.city import City  # noqa: E402
from authentication.models.user import User  # noqa: E402
from authentication.security import hash_password  # noqa: E402

from main import app  # noqa: E402


async def _login(client: AsyncClient, login: str, password: str) -> dict:
    resp = await client.post("/login", json={"login": login, "password": password})
    assert resp.status_code == 200
    return resp.json()


@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncClient:
    transport = ASGITransport(app=app, lifespan="on")
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Make sure lifespan startup has completed.
        await c.get("/")

        # Seed initial data once.
        async with TortoiseContext():
            await City.get_or_create(id=1, defaults={"name": "Unknown"})
            await User.create(
                first_name="Admin",
                last_name="User",
                other_name="",
                email="admin@test.com",
                phone="",
                birthday=date(1990, 1, 1),
                city_id=1,
                additional_info="",
                is_admin=True,
                password_hash=hash_password("adminpass"),
            )
            await User.create(
                first_name="Simple",
                last_name="User",
                other_name="",
                email="user@test.com",
                phone="",
                birthday=date(1995, 1, 1),
                city_id=1,
                additional_info="",
                is_admin=False,
                password_hash=hash_password("userpass"),
            )

        yield c


@pytest.mark.asyncio
async def test_login_wrong_password_returns_400(client: AsyncClient):
    resp = await client.post("/login", json={"login": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 400
    body = resp.json()
    assert "code" in body and "message" in body


@pytest.mark.asyncio
async def test_login_and_current_patch_and_logout(client: AsyncClient):
    await _login(client, "admin@test.com", "adminpass")

    resp = await client.get("/users/current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@test.com"
    assert body["is_admin"] is True

    resp = await client.patch(
        "/users/current",
        json={
            "first_name": "Admin2",
            "email": "admin2@test.com",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["first_name"] == "Admin2"
    assert body["email"] == "admin2@test.com"

    resp = await client.get("/logout")
    assert resp.status_code == 200
    assert resp.json() == {}

    resp = await client.get("/users/current")
    assert resp.status_code == 401
    assert resp.json()["message"]


@pytest.mark.asyncio
async def test_users_list_requires_cookie_and_pagination(client: AsyncClient):
    client.cookies.clear()
    resp = await client.get("/users?page=1&size=1")
    assert resp.status_code == 401

    await _login(client, "user@test.com", "userpass")
    resp = await client.get("/users?page=1&size=1")
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body and "meta" in body
    assert "pagination" in body["meta"]
    assert len(body["data"]) <= 1


@pytest.mark.asyncio
async def test_admin_private_endpoints_authz_and_crud(client: AsyncClient):
    # Simple user cannot access admin endpoints.
    await _login(client, "user@test.com", "userpass")
    resp = await client.get("/private/users?page=1&size=10")
    assert resp.status_code == 403

    # Admin creates a user without optional fields to validate defaults.
    await _login(client, "admin@test.com", "adminpass")
    create_resp = await client.post(
        "/private/users",
        json={
            "first_name": "Created",
            "last_name": "User",
            "email": "created@test.com",
            "is_admin": False,
            "password": "createdpass",
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["email"] == "created@test.com"
    assert created["city"] == 1
    assert created["additional_info"] == ""
    created_id = created["id"]

    list_resp = await client.get("/private/users?page=1&size=10")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["meta"]["hint"]["city"]
    assert any(c["id"] == 1 for c in list_body["meta"]["hint"]["city"])

    get_resp = await client.get(f"/private/users/{created_id}")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["id"] == created_id
    assert get_body["phone"] == ""

    patch_resp = await client.patch(
        f"/private/users/{created_id}",
        json={
            "id": created_id,
            "first_name": "Created2",
            "phone": "+1000000",
            "additional_info": "some info",
            "city": 1,
            "is_admin": True,
        },
    )
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["first_name"] == "Created2"
    assert patched["phone"] == "+1000000"
    assert patched["additional_info"] == "some info"
    assert patched["is_admin"] is True

    delete_resp = await client.delete(f"/private/users/{created_id}")
    assert delete_resp.status_code == 204

    not_found_resp = await client.get(f"/private/users/{created_id}")
    assert not_found_resp.status_code == 404

