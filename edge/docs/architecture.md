# Edge architecture

`edge/` is a separate Python package for services that belong at the boundary of the local application, including the future launcher, model proxy, and egress proxy described in the [technical specification](../../docs/technical-spec.md). It contains no business-domain modules and must not import the backend package.

The current source is a minimal scaffold; do not describe later services as implemented until their code and Compose integration exist. Package structure and checks are documented in [`../CLAUDE.md`](../CLAUDE.md).
