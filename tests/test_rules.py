from __future__ import annotations

from pathlib import Path

from docklens.parser import load_compose
from docklens.rules import Severity, run_rules


def test_port_collision_detected(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
services:
  a:
    image: repo/a:1
    ports: ["7000:80"]
  b:
    image: repo/b:1
    ports: ["7000:8080"]
        """.strip(),
        encoding="utf-8",
    )
    model = load_compose(yml)
    findings = run_rules(model)
    assert any(f.rule_id == "PORT001" and f.severity == Severity.ERROR for f in findings)


def test_latest_or_missing_tag_warn(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
services:
  a:
    image: repo/a
  b:
    image: repo/b:latest
  c:
    image: repo/c:1.0.0
        """.strip(),
        encoding="utf-8",
    )
    model = load_compose(yml)
    findings = run_rules(model)
    warn_services = {f.service for f in findings if f.rule_id == "IMG002"}
    assert "a" in warn_services
    assert "b" in warn_services
    assert "c" not in warn_services


def test_privileged_is_error(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
services:
  pwn:
    image: repo/x:1
    privileged: true
        """.strip(),
        encoding="utf-8",
    )
    model = load_compose(yml)
    findings = run_rules(model)
    assert any(f.rule_id == "SEC001" and f.severity == Severity.ERROR for f in findings)


def test_network_mode_host_warn(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
services:
  api:
    image: repo/api:1
    network_mode: host
        """.strip(),
        encoding="utf-8",
    )
    model = load_compose(yml)
    findings = run_rules(model)
    assert any(f.rule_id == "NET001" and f.severity == Severity.WARN for f in findings)
