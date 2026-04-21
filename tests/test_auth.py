def test_protected_route_rejects_missing_key(client):
    r = client.get("/loads/search")
    assert r.status_code == 401


def test_protected_route_rejects_wrong_key(client):
    r = client.get("/loads/search", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_healthz_does_not_require_key(client):
    r = client.get("/healthz")
    assert r.status_code == 200


def test_protected_route_accepts_correct_key(authed_client):
    r = authed_client.get("/loads/search")
    assert r.status_code in (200, 422)
