"""The 2026 `ca-nl/low_income_reduction_maximum` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    newfoundland_packages().roots(),
    newfoundland_parameter_parsers(),
    newfoundland_units(),
)
FAMILY = "ca-nl/low_income_reduction_maximum"
SOURCES = (
    "https://www.assembly.nl.ca/Legislation/sr/regulations/rc260018.htm",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",
)
CONFIRMED_HEADER = (
    "# Confirmed from the regulation named in the next line; the 2026 NL428 is not yet published."
)
SOURCE_HEADER = (
    "# Source: the form's maximum is the sum of the basic reduction and one of the spouse "
    "or dependant reductions (2025: 997 + 557 = 1,554); for 2026 it is 842 + 563 = 1,405, "
    "both as printed in Newfoundland and Labrador Regulation 18/26, Low Income Tax "
    "Reduction Regulations for the 2025 and 2026 Taxation Years (filed May 14, 2026; "
    "https://www.assembly.nl.ca/Legislation/sr/regulations/rc260018.htm), s.3(b), in force "
    "January 1, 2026 (s.5(2))."
)


def test_2026_low_income_reduction_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.values == Amount(D("1405"))


def test_2026_low_income_reduction_maximum_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_low_income_reduction_maximum_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.sources == SOURCES


def test_2026_low_income_reduction_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, AMOUNT)

    assert data.tax_year == 2026


def test_the_2026_file_is_confirmed_and_states_its_source() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "low_income_reduction_maximum" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == CONFIRMED_HEADER
    assert lines[1] == SOURCE_HEADER


def test_2025_low_income_reduction_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, AMOUNT)

    assert data.values == Amount(D("1554"))
    assert data.sources != SOURCES
