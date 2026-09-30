# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.7.20@sha256:2fd1b38e3398a256d6af3f71f0e2ba6a517b249998726a64d8cfbe55ab34af5e AS uv
FROM python:3.14.3-slim-bookworm@sha256:f21c0d5a44c56805654c15abccc1b2fd576c8d93aca0a3f74b4aba2dc92510e2 AS builder
COPY --from=uv /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv UV_NO_INSTALLER_METADATA=1
WORKDIR /workspace
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml
COPY edge/pyproject.toml edge/pyproject.toml
COPY packages/tekton-conventions/pyproject.toml packages/tekton-conventions/pyproject.toml
COPY backend/src backend/src
COPY backend/migrations backend/migrations
COPY packages/tekton-conventions/src packages/tekton-conventions/src
RUN uv sync --frozen --no-dev --package tekton-backend --no-install-project
COPY backend/src backend/src
RUN uv pip install --python /opt/venv/bin/python --no-deps ./backend
RUN uv pip install --python /opt/venv/bin/python 'minio==7.2.18'
COPY images/backend/s3-init.py /app/s3-init.py
ADD --chmod=0555 https://github.com/minio/mc/releases/download/RELEASE.2025-08-13T08-35-41Z/mc.linux-amd64.RELEASE.2025-08-13T08-35-41Z /usr/local/bin/mc
RUN printf '#!/bin/sh\nexec python /app/s3-init.py\n' > /usr/local/bin/s3-init && chmod 0555 /usr/local/bin/s3-init

FROM python:3.14.3-slim-bookworm@sha256:f21c0d5a44c56805654c15abccc1b2fd576c8d93aca0a3f74b4aba2dc92510e2 AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH=/app PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    TEKTON_CONFIGURATION_PATH=/app/deploy/backend.toml \
    TEKTON_SECRETS_DIRECTORY=/run/secrets
WORKDIR /app
RUN groupadd --system --gid 10001 tekton && useradd --system --uid 10001 --gid tekton --home-dir /app --no-create-home tekton \
    && mkdir -p /app/data/db /app/deploy /tmp \
    && chown -R 10001:10001 /app /tmp
COPY --from=builder --chown=10001:10001 /opt/venv /opt/venv
COPY --from=builder --chown=10001:10001 /workspace/backend/migrations /opt/venv/lib/python3.14/migrations
COPY --from=builder --chown=10001:10001 /usr/local/bin/mc /usr/local/bin/mc
COPY --from=builder --chown=10001:10001 /usr/local/bin/s3-init /usr/local/bin/s3-init
COPY --chown=10001:10001 backend/deploy/backend.toml /app/deploy/backend.toml
COPY --chown=10001:10001 images/backend/s3-init.py /app/s3-init.py
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "tekton.entrypoints.api:app", "--host", "0.0.0.0", "--port", "8000"]
