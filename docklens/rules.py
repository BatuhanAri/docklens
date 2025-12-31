from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from .parser import ComposeModel


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    service: str
    title: str
    detail: str


RuleFn = Callable[[ComposeModel], list[Finding]]


def _image_has_latest_or_no_tag(image: str) -> bool:
    # Examples:
    # - repo:latest -> true
    # - repo        -> true (no tag)
    # - repo:1.2.3  -> false
    # - registry/repo@sha256:... -> treat as pinned -> false
    if "@sha256:" in image:
        return False
    if ":" not in image:
        return True
    tag = image.rsplit(":", 1)[-1].strip()
    return tag == "" or tag.lower() == "latest"


def rule_image_tag(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    for s in model.services.values():
        if not s.image:
            out.append(
                Finding(
                    rule_id="IMG001",
                    severity=Severity.WARN,
                    service=s.name,
                    title="Service has no image specified",
                    detail="No 'image' field found. This may rely on 'build' or be misconfigured.",
                )
            )
            continue
        if _image_has_latest_or_no_tag(s.image):
            out.append(
                Finding(
                    rule_id="IMG002",
                    severity=Severity.WARN,
                    service=s.name,
                    title="Image tag is 'latest' or missing",
                    detail=f"Image: {s.image}. Pin an explicit version tag (or digest) to improve reproducibility.",
                )
            )
    return out


def rule_privileged(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    for s in model.services.values():
        if s.privileged:
            out.append(
                Finding(
                    rule_id="SEC001",
                    severity=Severity.ERROR,
                    service=s.name,
                    title="Privileged container",
                    detail="privileged: true grants near-host level permissions. Avoid unless strictly necessary.",
                )
            )
    return out


def rule_network_mode_host(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    for s in model.services.values():
        if (s.network_mode or "").strip().lower() == "host":
            out.append(
                Finding(
                    rule_id="NET001",
                    severity=Severity.WARN,
                    service=s.name,
                    title="network_mode: host",
                    detail="Host networking reduces isolation and can cause port conflicts. Prefer bridged networks.",
                )
            )
    return out


def _host_port(p: str) -> int | None:
    # Compose ports can be:
    # "8080:80", "127.0.0.1:8080:80", "80", "80/tcp"
    s = p.strip()
    if not s:
        return None
    # remove protocol suffix
    if "/" in s:
        s = s.split("/", 1)[0]
    parts = s.split(":")
    if len(parts) == 1:
        # container-only port, no host binding
        return None
    if len(parts) == 2:
        hp = parts[0]
    else:
        hp = parts[1]  # ip:host:container
    try:
        return int(hp)
    except ValueError:
        return None


def rule_port_collisions(model: ComposeModel) -> list[Finding]:
    used: dict[int, list[str]] = {}
    for s in model.services.values():
        for p in s.ports:
            hp = _host_port(p)
            if hp is None:
                continue
            used.setdefault(hp, []).append(s.name)

    out: list[Finding] = []
    for hp, svcs in sorted(used.items(), key=lambda x: x[0]):
        if len(svcs) > 1:
            out.append(
                Finding(
                    rule_id="PORT001",
                    severity=Severity.ERROR,
                    service=",".join(sorted(svcs)),
                    title="Host port collision",
                    detail=f"Host port {hp} is used by multiple services: {', '.join(sorted(svcs))}",
                )
            )
    return out


def _volume_is_readonly(v: str) -> bool:
    # "host:container:ro" or "...:rw"
    parts = v.split(":")
    if len(parts) < 3:
        return False
    mode = parts[-1].strip().lower()
    return mode == "ro"


CRITICAL_HOST_PATH_HINTS = (
    "/var/lib/docker/containers",
    "/var/run/docker.sock",
    "/var/log/journal",
    "/run/log/journal",
    "/etc/systemd",
    "/lib/systemd",
    "/run/systemd",
)


def rule_critical_mounts_not_ro(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    for s in model.services.values():
        for v in s.volumes:
            host = v.split(":")[0].strip()
            if any(hint in host for hint in CRITICAL_HOST_PATH_HINTS):
                if not _volume_is_readonly(v):
                    out.append(
                        Finding(
                            rule_id="VOL001",
                            severity=Severity.WARN,
                            service=s.name,
                            title="Critical host path mounted without :ro",
                            detail=f"Volume '{v}' looks sensitive. Prefer mounting read-only where possible.",
                        )
                    )
    return out


def rule_healthcheck_missing(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    for s in model.services.values():
        if not s.healthcheck_present:
            out.append(
                Finding(
                    rule_id="HLT001",
                    severity=Severity.INFO,
                    service=s.name,
                    title="No healthcheck defined",
                    detail="Consider adding healthcheck to improve restart behavior and observability.",
                )
            )
    return out


def rule_depends_on_without_health(model: ComposeModel) -> list[Finding]:
    out: list[Finding] = []
    # If a service depends_on others but healthchecks are missing, warn that depends_on isn't readiness.
    for s in model.services.values():
        if s.depends_on and not s.healthcheck_present:
            out.append(
                Finding(
                    rule_id="DEP001",
                    severity=Severity.WARN,
                    service=s.name,
                    title="depends_on without healthcheck",
                    detail=(
                        "depends_on controls start order, not readiness. Add healthchecks and handle retries."
                    ),
                )
            )
    return out


DEFAULT_RULES: list[RuleFn] = [
    rule_image_tag,
    rule_privileged,
    rule_network_mode_host,
    rule_port_collisions,
    rule_critical_mounts_not_ro,
    rule_healthcheck_missing,
    rule_depends_on_without_health,
]


def run_rules(model: ComposeModel, rules: list[RuleFn] | None = None) -> list[Finding]:
    rules = rules or DEFAULT_RULES
    findings: list[Finding] = []
    for r in rules:
        findings.extend(r(model))
    # stable ordering for deterministic output
    severity_rank = {Severity.ERROR: 0, Severity.WARN: 1, Severity.INFO: 2}
    findings.sort(key=lambda f: (severity_rank[f.severity], f.service, f.rule_id))
    return findings
