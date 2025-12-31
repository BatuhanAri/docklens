# DockLens

DockLens is a Python-based CLI tool that performs **static analysis** on `docker-compose.yml` files and generates a structured **best-practice, risk, and quality report**.

It helps developers and DevOps engineers identify Compose-level misconfigurations **early**, before they turn into runtime incidents or CI/CD failures.

---

## Why DockLens?

As Docker Compose files grow and evolve, they often accumulate subtle but critical issues, such as:

- unpinned images (`latest`)
- unsafe host mounts
- port collisions
- fragile startup ordering
- missing health checks

These problems are usually discovered **late**—during deployment, runtime, or production incidents.

DockLens analyzes Compose files **offline** and turns these risks into **clear, actionable findings** before they cause damage.

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

Usage

Basic scan:

docklens docker-compose.yml


Generate reports:

docklens docker-compose.yml \
  --out report.md \
  --json report.json

Example Output

Terminal summary:

ERROR   PORT001  api,db   Host port collision
WARN    IMG002   api      Image tag is 'latest' or missing
WARN    VOL001   api      Critical host path mounted without :ro
INFO    HLT001   api      No healthcheck defined


Generated artifacts:

report.md

report.json

A deliberately misconfigured demo file is available at:

examples/docker-compose.sample.yml

Exit Codes

DockLens is designed for CI/CD usage:

Exit Code	Meaning
0	No errors found
2	One or more ERROR findings

Warnings and info findings do not fail execution.

Project Structure
docklens/
├── docklens/
│   ├── cli.py
│   ├── parser.py
│   ├── rules.py
│   └── report.py
├── tests/
├── examples/
├── pyproject.toml
└── README.md

Roadmap

docklens diff old.yml new.yml

Additional security and reliability rules

SARIF output for GitHub code scanning

Rule severity configuration
