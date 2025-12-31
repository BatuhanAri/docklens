# 🐳 DockLens

DockLens is a Python-based CLI tool for static analysis of `docker-compose.yml` files.  
It detects best-practice violations, configuration risks, and reliability issues **before** they reach runtime or CI/CD pipelines.

## Quick Start

This section walks you through installing DockLens and running your first analysis.

### 1. Installation

Clone the repository and install DockLens in editable mode:

```bash
git clone https://github.com/<your-username>/docklens.git
cd docklens

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```
### 2. Running DockLens
Basic scan (terminal output only):

```bash
docklens docker-compose.yml

```

### 3. Example Output

Terminal summary:

    ERROR   PORT001  api,db   Host port collision
    WARN    IMG002   api      Image tag is 'latest' or missing
    WARN    VOL001   api      Critical host path mounted without :ro
    INFO    HLT001   api      No healthcheck defined

Generated artifacts:

report.md — human-readable Markdown report
report.json — machine-readable JSON output
A deliberately misconfigured demo file is included:

examples/docker-compose.sample.yml

### 4. Exit Codes
DockLens is designed for CI/CD usage.

    0 → No errors found
    2 → One or more ERROR-level findings

Warnings and informational findings do not fail execution.

### 5. Project Structure

    docklens/
    ├── docklens/
    │   ├── cli.py          # CLI entry point
    │   ├── parser.py       # Compose file parsing
    │   ├── rules.py        # Rule definitions
    │   └── report.py       # Markdown / JSON reporting
    ├── tests/
    ├── examples/
    ├── pyproject.toml
    └── README.md

### 6. Roadmap
Diff mode: docklens diff old.yml new.yml
Additional security and reliability rules
SARIF output for GitHub code scanning
Rule severity configuration


