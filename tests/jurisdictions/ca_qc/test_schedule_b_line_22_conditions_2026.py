"""The 2026 `ca-qc/schedule_b_line_22_conditions` dataset, provisional.

Pins the file as shipped: its figures, rounding, sources and tax year, and the two header
comment lines (the provisional line and the derivation line) that every 2026 file opens with.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc as ca_qc_package

FAMILY = "ca-qc/schedule_b_line_22_conditions"
PATH = (
    Path(ca_qc_package.__file__).parent
    / "parameters"
    / "schedule_b_line_22_conditions"
    / "2026.yaml"
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be "
    "confirmed against the 2026 form text when Revenu Quebec publishes it."
)
DERIVATION_HEADER = (
    '# Derivation: the 2025 form prints "born before January 1, 1961", which is 65 years of age '
    "on 31 December 2025 (the age condition of the amount); for 2026 the same age is born before "
    "January 1, 1962, so the year moves from 1960 to 1961. The 2026 form is not yet published."
)
EXPECTED: dict[str, Any] = {
    "family": "ca-qc/schedule_b_line_22_conditions",
    "tax_year": 2026,
    "kind": "conditions",
    "sources": ["Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part B"],
    "rounding": "none",
    "count_when_any_applies": "0",
    "conditions": [
        {
            "text": "You were born after 1961",
            "parts": [
                {
                    "tests": [
                        {"reads": "count", "position": "1", "relation": "more_than", "than": "1961"}
                    ]
                }
            ],
        }
    ],
}


def test_the_2026_file_holds_the_pinned_figures() -> None:
    assert yaml.safe_load(PATH.read_text()) == EXPECTED


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = PATH.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


@pytest.mark.parametrize(("year", "count"), [(1960, 1), (1961, 1), (1962, 0), (1990, 0)])
def test_the_2026_cutoff_is_65_on_31_december_2026(year: int, count: int) -> None:
    from decimal import Decimal

    from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
    from tax_engine.domain.artifact import Artifact
    from tax_engine.domain.kinds import CountKind
    from tax_engine.domain.parameters.conditions import CONDITIONS
    from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
    from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

    assert Decimal(year)
    source = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
    born, given = CountKind("ex/birth_year"), CountKind("ex/born")
    capability = CountByConditions(source.get(FAMILY, 2026, CONDITIONS), (born,), (), given)

    (output,) = capability.compute((Artifact(born, year),)).outputs

    assert output.value == count
