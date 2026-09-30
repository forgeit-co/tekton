import json
import os
import time
from urllib.error import URLError
from urllib.request import urlopen


def test_local_deployment_health_and_frontend() -> None:
    port = os.environ.get("TEKTON_HOST_PORT", "8080")
    base_url = f"http://127.0.0.1:{port}"
    live_url = f"{base_url}/api/v1/health/live"
    deadline = time.monotonic() + 60
    last_error = "no response"

    while time.monotonic() < deadline:
        try:
            with urlopen(live_url, timeout=2) as response:
                live_body = response.read().decode("utf-8").strip()
                if response.status == 200 and live_body == "ok":
                    break
                last_error = f"unexpected response: HTTP {response.status}, body {live_body!r}"
        except (OSError, URLError) as error:
            last_error = str(error)
        time.sleep(1)
    else:
        raise AssertionError(
            f"Deployment live health did not return 'ok' at {live_url} within 60 seconds; "
            f"last result: {last_error}"
        )

    root_url = f"{base_url}/"
    try:
        with urlopen(root_url, timeout=5) as response:
            if response.status != 200:
                raise AssertionError(
                    f"Deployment frontend root {root_url} returned HTTP {response.status}, expected 200"
                )
    except (OSError, URLError) as error:
        raise AssertionError(f"Deployment frontend root {root_url} failed: {error}") from error

    health_url = f"{base_url}/api/v1/health"
    try:
        with urlopen(health_url, timeout=5) as response:
            if response.status != 200:
                raise AssertionError(
                    f"Deployment health endpoint {health_url} returned HTTP {response.status}, expected 200"
                )
            payload = json.loads(response.read())
    except (OSError, URLError, json.JSONDecodeError) as error:
        raise AssertionError(f"Deployment health endpoint {health_url} failed: {error}") from error

    if not isinstance(payload, dict) or not payload.get("status"):
        raise AssertionError(
            f"Deployment health endpoint {health_url} must return JSON with a status field; got {payload!r}"
        )
