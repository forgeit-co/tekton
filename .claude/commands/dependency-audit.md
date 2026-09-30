Find and report dependency vulnerabilities across every dependency ecosystem in this repository. Do not change dependency versions or manifests unless the operator explicitly asks for remediation.

## Python workspace

1. Run `just audit` to scan the locked Python workspace dependencies and frontend dependency tree. The command reports both ecosystems even when one finds vulnerabilities.
2. Report the Python findings from `pip-audit`, including affected package, installed version, advisory ID, and fixed version if available.
3. Do not update dependencies or run automatic fixes.

## Frontend

1. Report the `pnpm audit` findings separately, including package, severity, advisory ID, and patched version if available.
2. Do not run `pnpm audit --fix` or update dependencies without explicit approval.

## Report

Summarize each ecosystem's result, list unresolved findings as reported by the tools, and include tool or registry errors distinctly from vulnerability results. If an operator separately authorizes remediation, run `just test-all` after updates and report any failures.