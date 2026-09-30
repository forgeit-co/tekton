from tekton.infrastructure.storage.s3_policy import (
    API_READABLE_BUCKETS,
    API_WRITABLE_BUCKETS,
    V1_BUCKETS,
    WORKER_DELETABLE_BUCKETS,
    WORKER_READABLE_BUCKETS,
    WORKER_WRITABLE_BUCKETS,
    S3Bucket,
    S3Service,
    policy_for_service,
)


def test_v1_bucket_set_matches_service_access_catalogue():
    assert V1_BUCKETS == (
        S3Bucket.DOCUMENTS,
        S3Bucket.PUBLIC,
        S3Bucket.SNAPSHOTS,
        S3Bucket.TRANSCRIPTS,
        S3Bucket.SESSION_FILES,
    ), "S3 policies must explicitly cover the v1 buckets"


def test_api_policy_is_limited_to_document_writes():
    policy = policy_for_service(S3Service.API)

    assert API_READABLE_BUCKETS == V1_BUCKETS, "API should be able to read all v1 buckets"
    assert API_WRITABLE_BUCKETS == (S3Bucket.DOCUMENTS,), "API should only write documents"
    policy_buckets = {
        statement.resources[0].removeprefix("arn:aws:s3:::").split("/")[0]
        for statement in policy.statements
    }
    assert policy_buckets == {bucket.value for bucket in V1_BUCKETS}, (
        "API policy must only reference the v1 bucket set"
    )


def test_worker_policy_can_manage_all_v1_buckets():
    policy = policy_for_service(S3Service.WORKER)

    assert WORKER_READABLE_BUCKETS == V1_BUCKETS, "Worker should be able to read all v1 buckets"
    assert WORKER_WRITABLE_BUCKETS == V1_BUCKETS, "Worker should write all v1 buckets"
    assert WORKER_DELETABLE_BUCKETS == V1_BUCKETS, "Worker should own retention deletion"
    assert len(policy.statements) == len(V1_BUCKETS) * 2, "Policy should scope each bucket"


def test_api_policy_does_not_grant_delete_actions():
    policy = policy_for_service(S3Service.API)
    granted_actions = [action for statement in policy.statements for action in statement.actions]

    assert "s3:DeleteObject" not in granted_actions, "API must not delete stored objects"
    assert "s3:DeleteObjectVersion" not in granted_actions, "API must not delete object versions"
