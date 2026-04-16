import os
import tempfile
import uuid
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


DB_FILE = Path(tempfile.gettempdir()) / f"test_{uuid.uuid4().hex}.sqlite3"

os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DEFAULT_CITY_ID"] = "1"
os.environ["DEFAULT_CITY_NAME"] = "Unknown"

# Auto-seeding for init_db()
os.environ["DEFAULT_ADMIN_EMAIL"] = "admin@test.com"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "adminpass"
os.environ["DEFAULT_SIMPLE_EMAIL"] = "user@test.com"
os.environ["DEFAULT_SIMPLE_PASSWORD"] = "userpass"
os.environ["DEFAULT_BIRTHDAY_ADMIN"] = "1990-01-01"
os.environ["DEFAULT_BIRTHDAY_SIMPLE"] = "1995-01-01"


from main import app  # noqa: E402


def _login(client: TestClient, login: str, password: str) -> dict:
    resp = client.post("/login", json={"login": login, "password": password})
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_login_wrong_password_returns_400(client: TestClient):
    resp = client.post("/login", json={"login": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 400
    body = resp.json()
    assert "code" in body and "message" in body


def test_login_current_patch_and_logout(client: TestClient):
    _login(client, "admin@test.com", "adminpass")

    resp = client.get("/users/current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@test.com"
    assert body["is_admin"] is True
    assert body["birthday"] == "1990-01-01"

    resp = client.patch(
        "/users/current",
        json={"first_name": "Admin2", "birthday": "2000-02-02"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["first_name"] == "Admin2"
    assert body["email"] == "admin@test.com"
    assert body["birthday"] == "2000-02-02"

    resp = client.get("/logout")
    assert resp.status_code == 200
    assert resp.json() == {}

    resp = client.get("/users/current")
    assert resp.status_code == 401
    assert resp.json()["message"]


def test_users_list_requires_cookie_and_pagination(client: TestClient):
    client.cookies.clear()
    resp = client.get("/users?page=1&size=1")
    assert resp.status_code == 401

    _login(client, "user@test.com", "userpass")
    resp = client.get("/users?page=1&size=1")
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body and "meta" in body
    assert "pagination" in body["meta"]
    assert len(body["data"]) == 1


def test_admin_private_endpoints_authz_and_crud(client: TestClient):
    # Non-admin cannot access admin endpoints.
    _login(client, "user@test.com", "userpass")
    resp = client.get("/private/users?page=1&size=10")
    assert resp.status_code == 403

    # Admin CRUD.
    _login(client, "admin@test.com", "adminpass")

    # Create user with minimal required fields.
    create_resp = client.post(
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
    created_id = created["id"]
    assert created["email"] == "created@test.com"
    assert created["city"] == 1
    assert created["other_name"] == ""
    assert created["phone"] == ""
    assert created["additional_info"] == ""
    assert created["is_admin"] is False

    # Admin list
    list_resp = client.get("/private/users?page=1&size=10")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["meta"]["pagination"]["page"] == 1
    assert list_body["meta"]["hint"]["city"]

    # Admin get
    get_resp = client.get(f"/private/users/{created_id}")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["id"] == created_id
    assert get_body["phone"] == ""

    # Admin patch
    patch_resp = client.patch(
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

    # Admin delete
    delete_resp = client.delete(f"/private/users/{created_id}")
    assert delete_resp.status_code == 204

    # Deleted user gone
    not_found_resp = client.get(f"/private/users/{created_id}")
    assert not_found_resp.status_code == 404

