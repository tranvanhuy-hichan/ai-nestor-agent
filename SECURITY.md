# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue. Use GitHub's private reporting:
<https://github.com/tranvanhuy-hichan/argus-agent/security/advisories/new>

Include steps to reproduce, affected version/commit and impact. We aim to acknowledge within 7 days.

## Scope notes

Argus runs shell commands and tools on your machine. Keep the default localhost-only binding, enable a login password and API-token auth if you expose it, and use the Docker sandbox for untrusted workloads. Never share your `user-data/` directory (it holds API keys).
