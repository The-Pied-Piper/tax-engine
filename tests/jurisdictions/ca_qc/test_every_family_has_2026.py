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
CARRIED_FORWARD = "carried forward unchanged from the 2025 file"
CARRIED_FORWARD_FAMILIES = [
    "cent_rounding",
    "cwb_base_amount",
    "cwb_maximum",
    "cwb_rate",
    "cwb_reduction_rate",
    "cwb_reduction_threshold",
    "exact_rounding",
    "schedule_b_line_20_conditions",
    "schedule_b_line_31_rate",
    "schedule_k_brackets",
    "schedule_k_line_41_amount",
    "schedule_k_line_83_maximum",
    "schedule_k_line_87_maximum",
    "schedule_k_monthly_amount_box_60",
    "schedule_k_monthly_amount_box_61",
    "schedule_k_months_box_60",
    "schedule_k_months_box_61",
    "schedule_k_months_in_year_line_85",
    "schedule_u_line_15_rate",
    "schedule_u_line_21_rate",
    "solidarity_housing_multiple_amount",
    "solidarity_housing_single_amount",
    "solidarity_living_alone_amount",
    "solidarity_occupants_conditions",
    "solidarity_qst_base_amount",
    "solidarity_reduction_rate",
    "solidarity_reduction_rate_one_component",
    "solidarity_reduction_threshold",
    "tp1_line_377_1_rate",
    "tp1_line_389_rate",
    "tp1_line_397_rate",
    "tp1_zero_line_474_475",
    "work_chart_201_rate",
    "work_premium_rate",
    "work_premium_reduction_rate",
    "work_premium_supplement_amount",
]


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


@pytest.mark.parametrize("name", CARRIED_FORWARD_FAMILIES)
def test_a_carried_forward_2026_file_equals_its_2025_file_apart_from_the_year(name: str) -> None:
    lines = (_parameters_dir() / name / "2026.yaml").read_text().splitlines()
    old = SOURCE.get(f"ca-qc/{name}", 2025, _kind(name, 2025))
    new = SOURCE.get(f"ca-qc/{name}", 2026, _kind(name, 2026))

    assert CARRIED_FORWARD in lines[1]
    assert new.values == old.values
    assert new.rounding == old.rounding
    assert new.sources == old.sources
    assert (old.tax_year, new.tax_year) == (2025, 2026)
