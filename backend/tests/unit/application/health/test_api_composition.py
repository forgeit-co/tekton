from tekton.application.health.health import HealthCheck


def test_two_api_apps_can_start_in_one_process(
    two_started_api_apps: tuple[HealthCheck, HealthCheck],
):
    first_health_check, second_health_check = two_started_api_apps

    assert first_health_check is not second_health_check, (
        "Each running app must own its composed services"
    )
