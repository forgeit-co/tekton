from tekton.application.health.health import HealthReader, HealthStatus


class FakeHealthReader(HealthReader):
    def __init__(self, health_status: HealthStatus):
        self._health_status = health_status

    def read_health(self) -> HealthStatus:
        return self._health_status
