import os

import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "test-key"
os.environ["FMCSA_WEBKEY"] = "test-fmcsa-key"
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test.db")


@pytest.fixture
def client():
    from app.db import init_db
    from app.main import app

    init_db()
    return TestClient(app)


@pytest.fixture
def authed_client(client):
    client.headers.update({"X-API-Key": "test-key"})
    return client
