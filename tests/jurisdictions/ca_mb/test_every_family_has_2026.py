"""Every `ca-mb` dataset family that 2025 declares has a 2026 file (ticket #1364)."""

from __future__ import annotations

from pathlib import Path

from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_mb.support import manitoba_packages

FAMILY_COUNT = 20


def _parameters_dir() -> Path:
    return manitoba_packages().roots()[Namespace("ca-mb")] / "parameters"


def test_there_are_twenty_families() -> None:
    families = [p for p in _parameters_dir().iterdir() if p.is_dir()]

    assert len(families) == FAMILY_COUNT


def test_every_family_with_a_2025_file_has_a_2026_file() -> None:
    families = sorted(p for p in _parameters_dir().iterdir() if p.is_dir())

    missing = [p.name for p in families if not (p / "2026.yaml").is_file()]
    assert missing == []
    assert all((p / "2025.yaml").is_file() for p in families)
