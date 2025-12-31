# DockLens

DockLens is a Python-based CLI tool that performs static analysis on `docker-compose.yml` files and generates a structured **best-practice, risk, and quality report**.  
It helps developers and DevOps engineers catch Compose-level misconfigurations **early**, before runtime incidents or CI failures.

---

## Why DockLens?

As Docker Compose files evolve, they commonly accumulate:
- unpinned images (`latest`)
- unsafe host mounts
- port collisions
- fragile startup ordering
- missing health checks

DockLens analyzes Compose files offline and turns these issues into **clear, actionable findings**.

---

## Features (v0.1.0)

- Parses Docker Compose services:
  - image
  - ports
  - volumes
  - network_mode
  - restart policy
  - environment variables
  - depends_on
  - healthcheck

- Detects:
  - missing or `latest` image tags
  - privileged containers
  - `network_mode: host`
  - host port collisions
  - sensitive host paths mounted without `:ro`
  - missing healthchecks
  - `depends_on` usage without health readiness guarantees

- Outputs:
  - colored terminal summary
  - Markdown report
  - JSON report (machine-readable)

- CI-friendly exit codes

---

## Installation (local / development)

```bash
pip install -e .
