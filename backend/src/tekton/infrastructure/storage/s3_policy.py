from dataclasses import dataclass
from enum import StrEnum
from typing import assert_never


class S3Bucket(StrEnum):
    DOCUMENTS = "documents"
    PUBLIC = "public"
    SNAPSHOTS = "snapshots"
    TRANSCRIPTS = "transcripts"
    SESSION_FILES = "session-files"


class S3Service(StrEnum):
    API = "api"
    WORKER = "worker"


@dataclass(frozen=True, slots=True)
class S3PolicyStatement:
    effect: str
    actions: tuple[str, ...]
    resources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class S3Policy:
    version: str
    statements: tuple[S3PolicyStatement, ...]

    def to_document(self) -> dict[str, object]:
        return {
            "Version": self.version,
            "Statement": [
                {
                    "Effect": statement.effect,
                    "Action": list(statement.actions),
                    "Resource": list(statement.resources),
                }
                for statement in self.statements
            ],
        }


V1_BUCKETS = tuple(S3Bucket)
API_READABLE_BUCKETS = V1_BUCKETS
API_WRITABLE_BUCKETS = (S3Bucket.DOCUMENTS,)
WORKER_READABLE_BUCKETS = V1_BUCKETS
WORKER_WRITABLE_BUCKETS = V1_BUCKETS
WORKER_DELETABLE_BUCKETS = V1_BUCKETS


def policy_for_service(service: S3Service) -> S3Policy:
    match service:
        case S3Service.API:
            readable_buckets = API_READABLE_BUCKETS
            writable_buckets = API_WRITABLE_BUCKETS
            deletable_buckets = ()
        case S3Service.WORKER:
            readable_buckets = WORKER_READABLE_BUCKETS
            writable_buckets = WORKER_WRITABLE_BUCKETS
            deletable_buckets = WORKER_DELETABLE_BUCKETS
        case _:
            assert_never(service)
    statements: list[S3PolicyStatement] = []
    for bucket in readable_buckets:
        statements.append(
            S3PolicyStatement(
                effect="Allow",
                actions=("s3:ListBucket", "s3:GetBucketLocation"),
                resources=(f"arn:aws:s3:::{bucket.value}",),
            )
        )
        object_actions = ["s3:GetObject"]
        if bucket in writable_buckets:
            object_actions.extend(("s3:PutObject", "s3:AbortMultipartUpload"))
        if bucket in deletable_buckets:
            object_actions.extend(("s3:DeleteObject", "s3:DeleteObjectVersion"))
        statements.append(
            S3PolicyStatement(
                effect="Allow",
                actions=tuple(object_actions),
                resources=(f"arn:aws:s3:::{bucket.value}/*",),
            )
        )
    return S3Policy(version="2012-10-17", statements=tuple(statements))
