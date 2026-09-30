from pathlib import Path

from tekton.composition.worker import worker_heartbeat_is_fresh


def test_worker_heartbeat_is_fresh_when_recent_timestamp_exists(tmp_path: Path):
    heartbeat_path = tmp_path / "worker-heartbeat"
    heartbeat_path.write_text("1000", encoding="utf-8")

    assert worker_heartbeat_is_fresh(heartbeat_path, now=1119), "Recent heartbeat should be healthy"


def test_worker_heartbeat_is_stale_after_two_minutes(tmp_path: Path):
    heartbeat_path = tmp_path / "worker-heartbeat"
    heartbeat_path.write_text("1000", encoding="utf-8")

    assert not worker_heartbeat_is_fresh(heartbeat_path, now=1121), "Old heartbeat should be stale"


def test_worker_heartbeat_is_unhealthy_when_file_is_missing(tmp_path: Path):
    heartbeat_path = tmp_path / "worker-heartbeat"

    assert not worker_heartbeat_is_fresh(heartbeat_path, now=1000), (
        "Missing heartbeat should be unhealthy"
    )


def test_worker_heartbeat_is_unhealthy_when_timestamp_is_invalid(tmp_path: Path):
    heartbeat_path = tmp_path / "worker-heartbeat"
    heartbeat_path.write_text("unavailable", encoding="utf-8")

    assert not worker_heartbeat_is_fresh(heartbeat_path, now=1000), (
        "Invalid heartbeat should be unhealthy"
    )
