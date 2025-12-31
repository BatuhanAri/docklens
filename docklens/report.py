from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .parser import ComposeModel
from .rules import Finding, Severity


def _summary(findings: list[Finding]) -> dict[str, int]:
    c = {Severity.ERROR.value: 0, Severity.WARN.value: 0, Severity.INFO.value: 0}
    for f in findings:
        c[f.severity.value] += 1
    return c


def render_markdown(model: ComposeModel, findings: list[Finding]) -> str:
    s = _summary(findings)
    now = datetime.now(timezone.utc).isoformat()

    lines: list[str] = []
    lines.append("# DockLens Report\n")
    lines.append(f"- **File:** `{model.path}`")
    lines.append(f"- **Compose version:** `{model.version or 'n/a'}`")
    lines.append(f"- **Generated at (UTC):** `{now}`\n")
    lines.append("## Summary\n")
    lines.append(f"- Errors: **{s['error']}**")
    lines.append(f"- Warnings: **{s['warn']}**")
    lines.append(f"- Info: **{s['info']}**\n")

    lines.append("## Services\n")
    for svc in model.services.values():
        lines.append(f"### `{svc.name}`")
        lines.append(f"- image: `{svc.image or 'n/a'}`")
        lines.append(f"- ports: `{', '.join(svc.ports) if svc.ports else 'n/a'}`")
        lines.append(f"- volumes: `{', '.join(svc.volumes) if svc.volumes else 'n/a'}`")
        lines.append(f"- network_mode: `{svc.network_mode or 'n/a'}`")
        lines.append(f"- restart: `{svc.restart or 'n/a'}`")
        lines.append(f"- privileged: `{svc.privileged}`")
        lines.append(f"- depends_on: `{', '.join(svc.depends_on) if svc.depends_on else 'n/a'}`")
        lines.append(f"- healthcheck: `{'yes' if svc.healthcheck_present else 'no'}`\n")

    lines.append("## Findings\n")
    if not findings:
        lines.append("No findings. Your compose looks clean.\n")
        return "\n".join(lines)

    for f in findings:
        sev = f.severity.value.upper()
        lines.append(f"- **{sev}** `{f.rule_id}` — `{f.service}` — {f.title}")
        lines.append(f"  - {f.detail}")
    lines.append("")
    return "\n".join(lines)


def render_json(model: ComposeModel, findings: list[Finding]) -> str:
    payload = {
        "file": str(model.path),
        "compose_version": model.version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": _summary(findings),
        "services": {name: asdict(svc) for name, svc in model.services.items()},
        "findings": [asdict(f) for f in findings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def write_output(path: str | Path, content: str) -> Path:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p
