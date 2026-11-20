"""Every `ca-qc` dataset family that 2025 declares has a 2026 file, read through its typed kind.

A family whose 2026 file says it is carried forward unchanged from 2025 equals its 2025 file apart
from the year, as the other provinces' carried-forward datasets do.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
CARRIED_FORWARD = "# Derivation: carried forward unchanged from the 2025 file;"


def _parameters_dir() -> Path:
    return Path(ca_qc_package.__file__).parent / "parameters"


def _families() -> list[str]:
    return sorted(p.name for p in _parameters_dir().iterdir() if p.is_dir())


def _kind(family: str, year: int) -> Any:
    declared = yaml.safe_load((_parameters_dir() / family / f"{year}.yaml").read_text())["kind"]
    return quebec_parameter_parsers().get(declared).kind


def test_every_family_with_a_2025_file_has_a_2026_file() -> None:
    families = _families()

    assert families
    missing = [name for name in families if not (_parameters_dir() / name / "2026.yaml").is_file()]
    assert missing == []
    assert all((_parameters_dir() / name / "2025.yaml").is_file() for name in families)


@pytest.mark.parametrize("name", _families())
def test_the_2026_file_reads_through_its_kind_and_names_its_sources(name: str) -> None:
    data = SOURCE.get(f"ca-qc/{name}", 2026, _kind(name, 2026))

    assert data.tax_year == 2026
    assert data.sources


@pytest.mark.parametrize("name", _families())
def test_a_carried_forward_2026_file_equals_its_2025_file_apart_from_the_year(name: str) -> None:
    lines = (_parameters_dir() / name / "2026.yaml").read_text().splitlines()
    if not lines[1].startswith(CARRIED_FORWARD):
        pytest.skip("figures differ from 2025 by design")
    old = SOURCE.get(f"ca-qc/{name}", 2025, _kind(name, 2025))
    new = SOURCE.get(f"ca-qc/{name}", 2026, _kind(name, 2026))

    assert new.values == old.values
    assert new.rounding == old.rounding
    assert (old.tax_year, new.tax_year) == (2025, 2026)
