"""Every `ca-qc` dataset family that 2025 declares has a 2026 file."""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_qc as ca_qc_package


def _parameters_dir() -> Path:
    return Path(ca_qc_package.__file__).parent / "parameters"


def test_every_family_with_a_2025_file_has_a_2026_file() -> None:
    families = sorted(p for p in _parameters_dir().iterdir() if p.is_dir())

    assert families
    missing = [p.name for p in families if not (p / "2026.yaml").is_file()]
    assert missing == []
    assert all((p / "2025.yaml").is_file() for p in families)
