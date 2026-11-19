"""The 2026 `ca-nl/low_income_threshold_conditions` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/low_income_threshold_conditions"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; T4127 (Jan and Jul 2026)"
    " does not print this figure and the 2026 form is not yet published, so it is "
    "unconfirmed."
)


def test_2026_low_income_threshold_conditions_are_an_amount_on_line_96_or_on_line_97() -> None:
    data = SOURCE.get(FAMILY, 2026, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "You claimed an amount on line 96",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D(0), None),)),),
            ),
            Condition(
                "You claimed an amount on line 97",
                (ConditionPart((ConditionTest("amount", 2, "more_than", D(0), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, CONDITIONS)
    original = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_2026_low_income_threshold_conditions_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CONDITIONS)

    assert data.rounding == NO_ROUNDING


def test_2026_low_income_threshold_conditions_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CONDITIONS)

    assert data.sources == SOURCES


def test_2026_low_income_threshold_conditions_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CONDITIONS)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "low_income_threshold_conditions" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
