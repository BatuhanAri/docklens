# 🐳 DockLens

DockLens is a Python-based CLI tool that performs **static analysis** on `docker-compose.yml` files and generates a structured **best-practice, risk, and quality report**.

It helps developers and DevOps engineers detect Compose-level misconfigurations **early**, before they cause runtime incidents or CI/CD failures.

---

## Why DockLens?

As Docker Compose files evolve, they tend to accumulate subtle but dangerous configuration issues such as:

- unpinned images (`latest`)
- unsafe host mounts
- port collisions
- fragile startup ordering
- missing health checks

DockLens analyzes Compose files **offline** and turns these risks into **clear, actionable findings**.

---

## Features (v0.1.0)

### Compose Parsing
DockLens parses the following service attributes:

- image
- ports
- volumes
- network_mode
- restart policy
- environment variables
- depends_on
- healthcheck

### Detection Rules
DockLens detects and reports:

- missing or `latest` image tags
- privileged containers
- usage of `network_mode: host`
- host port collisions
- sensitive host paths mounted without `:ro`
- missing healthchecks
- `depends_on` usage without health readiness guarantees

### Output & Tooling
- colored terminal summary
- Markdown report
- JSON report (machine-readable)
- CI-friendly exit codes

---

## Installation (local / development)

```bash
pip install -e .
