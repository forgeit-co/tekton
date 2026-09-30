from tests.api.client import ApiClient


def test_health_live_returns_plain_text_ok(api_client: ApiClient):
    response = api_client.get("/api/v1/health/live")

    assert response.status_code == 200, "Liveness should return success"
    assert response.text == "ok", "Liveness must use the specified response body"
    assert response.headers["content-type"].startswith("text/plain"), "Liveness must be plain text"


def test_health_returns_status_and_schema_revision(api_client: ApiClient):
    response = api_client.get("/api/v1/health")

    assert response.status_code == 200, "Health probe should return success"
    assert response.json() == {"status": "ok", "schema_revision": "0001"}, (
        "Health should report database status and current schema revision"
    )
