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


def test_unknown_method_returns_problem_method_not_allowed(api_client: ApiClient):
    response = api_client.post("/api/v1/health/live")

    assert response.status_code == 405, "Unsupported methods should be rejected"
    assert response.headers["content-type"].startswith("application/problem+json"), (
        "HTTP errors must use problem+json"
    )
    assert response.json()["code"] == "method.not_allowed", (
        "405 should use the stable method.not_allowed problem code"
    )
