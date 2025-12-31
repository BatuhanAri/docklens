from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Service:
    name: str
    image: str | None
    ports: list[str]
    volumes: list[str]
    network_mode: str | None
    privileged: bool
    restart: str | None
    environment: dict[str, str]
    depends_on: list[str]
    healthcheck_present: bool


@dataclass(frozen=True)
class ComposeModel:
    path: Path
    version: str | None
    services: dict[str, Service]


def _normalize_env(env: Any) -> dict[str, str]:
    # compose: environment can be dict or list like ["A=1", "B=2"]
    if env is None:
        return {}
    if isinstance(env, dict):
        out: dict[str, str] = {}
        for k, v in env.items():
            out[str(k)] = "" if v is None else str(v)
        return out
    if isinstance(env, list):
        out = {}
        for item in env:
            if not isinstance(item, str):
                continue
            if "=" in item:
                k, v = item.split("=", 1)
                out[k.strip()] = v.strip()
            else:
                out[item.strip()] = ""
        return out
    return {}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]


def load_compose(path: str | Path) -> ComposeModel:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"compose file not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("compose file is not a YAML mapping")

    services_raw = raw.get("services")
    if not isinstance(services_raw, dict) or not services_raw:
        raise ValueError("compose file has no services")

    services: dict[str, Service] = {}
    for svc_name, svc_cfg in services_raw.items():
        if not isinstance(svc_cfg, dict):
            svc_cfg = {}

        image = svc_cfg.get("image")
        image = str(image) if image is not None else None

        ports = _as_list(svc_cfg.get("ports"))
        volumes = _as_list(svc_cfg.get("volumes"))
        network_mode = svc_cfg.get("network_mode")
        network_mode = str(network_mode) if network_mode is not None else None

        privileged = bool(svc_cfg.get("privileged", False))
        restart = svc_cfg.get("restart")
        restart = str(restart) if restart is not None else None

        environment = _normalize_env(svc_cfg.get("environment"))

        depends_on = svc_cfg.get("depends_on")
        if isinstance(depends_on, dict):
            depends_on_list = [str(k) for k in depends_on.keys()]
        else:
            depends_on_list = _as_list(depends_on)

        healthcheck_present = isinstance(svc_cfg.get("healthcheck"), dict)

        services[str(svc_name)] = Service(
            name=str(svc_name),
            image=image,
            ports=ports,
            volumes=volumes,
            network_mode=network_mode,
            privileged=privileged,
            restart=restart,
            environment=environment,
            depends_on=depends_on_list,
            healthcheck_present=healthcheck_present,
        )

    version = raw.get("version")
    version = str(version) if version is not None else None
    return ComposeModel(path=p, version=version, services=services)
