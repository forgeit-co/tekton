import pytest

from tekton.application.health.health import HealthStatus
from tests.unit.application.health.fakes import FakeHealthReader


@pytest.fixture
def health_reader() -> FakeHealthReader:
    return FakeHealthReader(HealthStatus(status="ok", schema_revision="0001"))
