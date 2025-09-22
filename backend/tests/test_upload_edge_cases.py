import io
import os
import sys
import json
import pytest
from typing import Optional

# Ensure backend package is importable
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient  # type: ignore
from main import app  # type: ignore
from config import settings  # type: ignore


client = TestClient(app)


def auth_headers() -> dict:
    # Create a user and login to get token
    email = "test_user@example.com"
    password = "password123"

    # Register (ignore if already exists)
    client.post("/auth/register", json={"email": email, "password": password, "full_name": "Test User"})
    # Login
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_unsupported_file_type():
    headers = auth_headers()
    content = b"{}"  # JSON content
    files = {"file": ("data.json", io.BytesIO(content), "application/json")}
    resp = client.post("/datasets/upload", files=files, headers=headers)
    assert resp.status_code == 400
    assert "Supported types" in resp.json()["detail"]


def test_upload_empty_csv():
    headers = auth_headers()
    content = b""  # empty file
    files = {"file": ("empty.csv", io.BytesIO(content), "text/csv")}
    resp = client.post("/datasets/upload", files=files, headers=headers)
    assert resp.status_code == 400
    assert "Invalid tabular file" in resp.json()["detail"] or "contains no rows" in resp.json()["detail"].lower()


def test_upload_malformed_csv():
    headers = auth_headers()
    # Malformed CSV: only delimiters, no header/columns
    content = b",,,\n,,,\n"
    files = {"file": ("bad.csv", io.BytesIO(content), "text/csv")}
    resp = client.post("/datasets/upload", files=files, headers=headers)
    assert resp.status_code == 400
    # Should fail due to zero columns detected
    assert "Invalid tabular file" in resp.json()["detail"] or "no columns" in resp.json()["detail"].lower()


@pytest.mark.skipif("openpyxl" not in sys.modules and False, reason="openpyxl not installed")
def test_upload_simple_excel_when_supported():
    headers = auth_headers()
    try:
        import pandas as pd  # type: ignore
    except Exception:
        pytest.skip("pandas not available at test runtime")
    try:
        import openpyxl  # type: ignore  # noqa: F401
    except Exception:
        pytest.skip("openpyxl not installed")

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:  # type: ignore
        df.to_excel(writer, index=False)
    bio.seek(0)

    files = {"file": ("table.xlsx", bio, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    resp = client.post("/datasets/upload", files=files, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("success") is True
    assert data.get("rows_count") == 2
    assert data.get("columns_count") == 2


def test_upload_exceeds_file_size_limit(monkeypatch):
    headers = auth_headers()

    # Temporarily reduce max file size to a tiny value
    original_max = settings.max_file_size
    monkeypatch.setattr(settings, "max_file_size", 10)

    try:
        content = b"this is more than ten bytes"
        files = {"file": ("big.csv", io.BytesIO(content), "text/csv")}
        resp = client.post("/datasets/upload", files=files, headers=headers)
        assert resp.status_code == 400
        assert "File size" in resp.json()["detail"] or "exceeds" in resp.json()["detail"].lower()
    finally:
        # Restore
        monkeypatch.setattr(settings, "max_file_size", original_max)


