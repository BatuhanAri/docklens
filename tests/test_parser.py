from __future__ import annotations

from pathlib import Path

import pytest

from docklens.parser import load_compose


def test_load_compose_parses_services(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
version: "3.8"
services:
  api:
    image: myrepo/api:1.2.3
    ports:
      - "8080:80"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    environment:
      A: "1"
      B: 2
    depends_on:
      - db
  db:
    image: postgres:16
        """.strip(),
        encoding="utf-8",
    )

    model = load_compose(yml)
    assert model.version == "3.8"
    assert "api" in model.services and "db" in model.services
    assert model.services["api"].image == "myrepo/api:1.2.3"
    assert model.services["api"].environment["B"] == "2"
    assert model.services["api"].depends_on == ["db"]


def test_environment_list_form(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text(
        """
services:
  s1:
    image: repo/s1:1
    environment:
      - A=1
      - B
        """.strip(),
        encoding="utf-8",
    )
    model = load_compose(yml)
    env = model.services["s1"].environment
    assert env["A"] == "1"
    assert env["B"] == ""


def test_missing_services_raises(tmp_path: Path) -> None:
    yml = tmp_path / "docker-compose.yml"
    yml.write_text("version: '3.8'\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_compose(yml)
