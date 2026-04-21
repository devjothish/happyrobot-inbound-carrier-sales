import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("FMCSA_WEBKEY", "test-fmcsa-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)


@pytest.fixture
def authed_client(client):
    client.headers.update({"X-API-Key": "test-key"})
    return client
