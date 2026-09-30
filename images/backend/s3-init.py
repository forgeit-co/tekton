import json
import os
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from tekton.infrastructure.storage.s3_policy import (
    API_READABLE_BUCKETS,
    S3Bucket,
    S3Service,
    policy_for_service,
)

MC_COMMAND_TIMEOUT_SECONDS = 30
EXPECTED_MC_FAILURES = (
    "access denied",
    "accessdenied",
    "insufficient permissions",
    "no policy entities",
    "not authorized",
    "notauthorized",
    "policy not found",
    "policy does not exist",
    "specified user does not exist",
    "user does not exist",
    "user not found",
    "object does not exist",
)
POLICY_NAMES = {
    S3Service.API: "tekton-api",
    S3Service.WORKER: "tekton-worker",
}
SERVICE_USERS = tuple(S3Service)
BUCKETS = tuple(bucket.value for bucket in S3Bucket)
API_PROBE_BUCKETS = tuple(
    bucket.value for bucket in API_READABLE_BUCKETS if bucket != S3Bucket.DOCUMENTS
)


def read_secret(variable: str) -> str:
    return Path(os.environ[variable]).read_text(encoding="utf-8").strip()


def mc_command(config_directory: Path, *arguments: str) -> list[str]:
    return ["mc", "--config-dir", str(config_directory), *arguments]


def run_mc(config_directory: Path, *arguments: str, input_bytes: bytes | None = None) -> None:
    command = mc_command(config_directory, *arguments)
    try:
        subprocess.run(
            command,
            check=True,
            input=input_bytes,
            stdout=subprocess.DEVNULL,
            timeout=MC_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"MinIO command failed: {' '.join(command)}") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"MinIO command timed out after {MC_COMMAND_TIMEOUT_SECONDS}s: {' '.join(command)}"
        ) from error


def mc_is_denied(config_directory: Path, *arguments: str, input_bytes: bytes | None = None) -> bool:
    command = mc_command(config_directory, *arguments)
    try:
        result = subprocess.run(
            command,
            check=False,
            input=input_bytes,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=MC_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"MinIO command timed out after {MC_COMMAND_TIMEOUT_SECONDS}s: {' '.join(command)}"
        ) from error
    if result.returncode == 0:
        return False
    error_output = result.stderr.decode("utf-8", errors="replace").lower()
    if any(expected_failure in error_output for expected_failure in EXPECTED_MC_FAILURES):
        return True
    raise RuntimeError(
        f"MinIO command failed ({result.returncode}): {' '.join(command)}: {error_output.strip()}"
    )


def wait_for_minio(endpoint: str) -> None:
    request = f"{endpoint}/minio/health/ready"
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            with urlopen(request, timeout=3):
                return
        except (OSError, URLError):
            time.sleep(2)
    raise RuntimeError("MinIO did not become ready before provisioning timeout")


def policy_bytes(service: S3Service) -> bytes:
    return json.dumps(policy_for_service(service).to_document()).encode("utf-8")


def configure_user(config_directory: Path, service: S3Service) -> None:
    access_key = read_secret(f"S3_{service.value.upper()}_USER_FILE")
    secret_key = read_secret(f"S3_{service.value.upper()}_PASSWORD_FILE")
    if mc_is_denied(config_directory, "admin", "user", "info", "tekton-init", access_key):
        run_mc(config_directory, "admin", "user", "add", "tekton-init", access_key, secret_key)
    run_mc(
        config_directory,
        "admin",
        "policy",
        "attach",
        "tekton-init",
        POLICY_NAMES[service],
        "--user",
        access_key,
    )


def configure_policy(config_directory: Path, service: S3Service) -> None:
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=config_directory, suffix=".json"
    ) as policy_file:
        policy_file.write(policy_bytes(service))
        policy_file.flush()
        if mc_is_denied(
            config_directory,
            "admin",
            "policy",
            "info",
            "tekton-init",
            POLICY_NAMES[service],
        ):
            run_mc(
                config_directory,
                "admin",
                "policy",
                "create",
                "tekton-init",
                POLICY_NAMES[service],
                policy_file.name,
            )
            return

        for service_user in SERVICE_USERS:
            command = mc_command(
                config_directory,
                "admin",
                "policy",
                "detach",
                "tekton-init",
                POLICY_NAMES[service],
                "--user",
                read_secret(f"S3_{service_user.value.upper()}_USER_FILE"),
            )
            try:
                subprocess.run(
                    command,
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=MC_COMMAND_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"MinIO command timed out after {MC_COMMAND_TIMEOUT_SECONDS}s: "
                    f"{' '.join(command)}"
                ) from error
        run_mc(
            config_directory,
            "admin",
            "policy",
            "remove",
            "tekton-init",
            POLICY_NAMES[service],
        )
        run_mc(
            config_directory,
            "admin",
            "policy",
            "create",
            "tekton-init",
            POLICY_NAMES[service],
            policy_file.name,
        )


def expect_denied(
    config_directory: Path, *arguments: str, input_bytes: bytes | None = None
) -> None:
    if not mc_is_denied(config_directory, *arguments, input_bytes=input_bytes):
        raise RuntimeError(f"MinIO allowed forbidden operation: {' '.join(arguments)}")


def verify_service_policy(config_directory: Path, service: S3Service) -> None:
    access_key = read_secret(f"S3_{service.value.upper()}_USER_FILE")
    secret_key = read_secret(f"S3_{service.value.upper()}_PASSWORD_FILE")
    alias = f"tekton-{service.value}"
    endpoint = os.environ.get("S3_ENDPOINT_URL", "http://s3:9000")
    run_mc(config_directory, "alias", "set", alias, endpoint, access_key, secret_key)


def verify_policies(config_directory: Path) -> None:
    probe_key = f"policy-probe/{uuid.uuid4().hex}"
    probe_body = b"temporary service policy probe"
    for service in SERVICE_USERS:
        verify_service_policy(config_directory, service)
    api_alias = f"tekton-{S3Service.API.value}"
    worker_alias = f"tekton-{S3Service.WORKER.value}"
    try:
        for bucket in BUCKETS:
            run_mc(
                config_directory,
                "pipe",
                f"tekton-init/{bucket}/{probe_key}",
                input_bytes=probe_body,
            )

        for bucket in BUCKETS:
            run_mc(config_directory, "ls", f"{api_alias}/{bucket}")
            run_mc(config_directory, "cat", f"{api_alias}/{bucket}/{probe_key}")
            if bucket == S3Bucket.DOCUMENTS.value:
                run_mc(
                    config_directory,
                    "pipe",
                    f"{api_alias}/{bucket}/{probe_key}",
                    input_bytes=probe_body,
                )
            else:
                expect_denied(
                    config_directory,
                    "pipe",
                    f"{api_alias}/{bucket}/{probe_key}",
                    input_bytes=probe_body,
                )
            expect_denied(config_directory, "rm", f"{api_alias}/{bucket}/{probe_key}")
        for bucket in API_PROBE_BUCKETS:
            expect_denied(
                config_directory,
                "pipe",
                f"{api_alias}/{bucket}/{probe_key}",
                input_bytes=probe_body,
            )

        for bucket in BUCKETS:
            run_mc(config_directory, "ls", f"{worker_alias}/{bucket}")
            run_mc(config_directory, "cat", f"{worker_alias}/{bucket}/{probe_key}")
            run_mc(
                config_directory,
                "pipe",
                f"{worker_alias}/{bucket}/{probe_key}-worker",
                input_bytes=probe_body,
            )
            run_mc(config_directory, "rm", f"{worker_alias}/{bucket}/{probe_key}-worker")
            run_mc(config_directory, "rm", f"{worker_alias}/{bucket}/{probe_key}")
        expect_denied(config_directory, "admin", "info", worker_alias)
        expect_denied(config_directory, "admin", "info", api_alias)
    finally:
        for bucket in BUCKETS:
            mc_is_denied(config_directory, "rm", "--force", f"tekton-init/{bucket}/{probe_key}")
            mc_is_denied(
                config_directory,
                "rm",
                "--force",
                f"tekton-init/{bucket}/{probe_key}-worker",
            )
            mc_is_denied(
                config_directory,
                "rm",
                "--force",
                f"tekton-init/{bucket}/{probe_key}-api",
            )


def remove_temporary_files(directory: Path) -> None:
    for path in directory.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
    directory.rmdir()


def main() -> None:
    endpoint = os.environ.get("S3_ENDPOINT_URL", "http://s3:9000")
    root_access = read_secret("MINIO_ROOT_USER_FILE")
    root_secret = read_secret("MINIO_ROOT_PASSWORD_FILE")
    wait_for_minio(endpoint)

    config_directory = Path(tempfile.mkdtemp(prefix="tekton-mc-config-"))
    try:
        run_mc(config_directory, "alias", "set", "tekton-init", endpoint, root_access, root_secret)
        for bucket in BUCKETS:
            run_mc(config_directory, "mb", "--ignore-existing", f"tekton-init/{bucket}")
        for service in SERVICE_USERS:
            configure_policy(config_directory, service)
            configure_user(config_directory, service)
        verify_policies(config_directory)
    finally:
        remove_temporary_files(config_directory)


if __name__ == "__main__":
    main()
