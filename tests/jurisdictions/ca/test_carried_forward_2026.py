"""The seventeen 2026 datasets carried forward unchanged from 2025 (structure or a rule, not an
indexed dollar amount): each equals its 2025 file apart from the year, and its 2026 file opens
with the provisional and derivation header lines.
"""

from __future__ import annotations

from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT
from tax_engine.domain.parameters.conditions import CONDITIONS
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.fraction import FRACTION
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation: carried forward unchanged from the 2025 file;"
FAMILIES: list[tuple[str, ParameterKind[Any]]] = [
    ("ca/cent_rounding", ROUNDING_ONLY),
    ("ca-on/cent_rounding", ROUNDING_ONLY),
    ("ca-on/rate_rounding", ROUNDING_ONLY),
    ("ca/cwb_rate", RATE),
    ("ca/cwb_reduction_rate", RATE),
    ("ca/t2204_exemption", CREDIT),
    ("ca/t2204_line_1_conditions", CONDITIONS),
    ("ca/t2204_line_15_conditions", CONDITIONS),
    ("ca/schedule_8_zero", CREDIT),
    ("ca/donation_net_income_rate", RATE),
    ("ca-on/farmers_food_donation_rate", RATE),
    ("ca-on/on428_line_80_conditions", CONDITIONS),
    ("ca-on/lift_maximum", AMOUNT),
    ("ca-on/lift_individual_income_threshold", CREDIT),
    ("ca-on/lift_rate", RATE),
    ("ca-on/lift_single_rate", RATE),
    ("ca-on/tax_reduction_multiplier", FRACTION),
]


@pytest.mark.parametrize(("family", "kind"), FAMILIES, ids=[f for f, _ in FAMILIES])
def test_2026_equals_2025_apart_from_the_year(family: str, kind: ParameterKind[Any]) -> None:
    old = SOURCE.get(family, 2025, kind)
    new = SOURCE.get(family, 2026, kind)

    assert new.values == old.values
    assert new.rounding == old.rounding
    assert new.sources == old.sources
    assert (old.tax_year, new.tax_year) == (2025, 2026)


@pytest.mark.parametrize("family", [family for family, _ in FAMILIES])
def test_2026_file_carries_the_provisional_and_derivation_headers(family: str) -> None:
    namespace, name = family.split("/")
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace(namespace)]
    lines = (root / "parameters" / name / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)
