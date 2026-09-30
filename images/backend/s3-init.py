import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

BUCKETS = ("documents", "public", "snapshots", "transcripts", "session-files")
POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
            "Resource": [f"arn:aws:s3:::{bucket}" for bucket in BUCKETS],
        },
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject", "s3:PutObject", "s3:AbortMultipartUpload"],
            "Resource": [f"arn:aws:s3:::{bucket}/*" for bucket in BUCKETS],
        },
    ],
}


def read_secret(variable: str) -> str:
    return Path(os.environ[variable]).read_text(encoding="utf-8").strip()


def run_mc(config_directory: Path, *arguments: str) -> None:
    subprocess.run(
        ["mc", "--config-dir", str(config_directory), *arguments],
        check=True,
        stdout=subprocess.DEVNULL,
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


def policy_bytes() -> bytes:
    return json.dumps(POLICY).encode("utf-8")


def configure_user(config_directory: Path, user_name: str) -> None:
    access_key = read_secret(f"S3_{user_name.upper()}_USER_FILE")
    secret_key = read_secret(f"S3_{user_name.upper()}_PASSWORD_FILE")
    result = subprocess.run(
        [
            "mc",
            "--config-dir",
            str(config_directory),
            "admin",
            "user",
            "info",
            "tekton-init",
            access_key,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode:
        run_mc(config_directory, "admin", "user", "add", "tekton-init", access_key, secret_key)
    run_mc(
        config_directory,
        "admin",
        "policy",
        "attach",
        "tekton-init",
        "tekton-api",
        "--user",
        access_key,
    )


def configure_policy(config_directory: Path) -> None:
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=config_directory, suffix=".json"
    ) as policy_file:
        policy_file.write(policy_bytes())
        policy_file.flush()
        result = subprocess.run(
            [
                "mc",
                "--config-dir",
                str(config_directory),
                "admin",
                "policy",
                "info",
                "tekton-init",
                "tekton-api",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode:
            run_mc(
                config_directory,
                "admin",
                "policy",
                "create",
                "tekton-init",
                "tekton-api",
                policy_file.name,
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
        configure_policy(config_directory)
        for user_name in ("api", "worker"):
            configure_user(config_directory, user_name)
    finally:
        remove_temporary_files(config_directory)


if __name__ == "__main__":
    main()
