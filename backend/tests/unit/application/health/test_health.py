from tekton.application.health.health import HealthCheck, HealthStatus
from tests.unit.application.health.fakes import FakeHealthReader


def test_health_check_returns_status_reported_by_reader():
    expected_status = HealthStatus(status="ok", schema_revision="0001")
    health_check = HealthCheck(FakeHealthReader(expected_status))

    result = health_check.execute()

    assert result == expected_status, "Health use case should return the reader status"
