"""The 2026 `ca-pe/brackets` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/brackets"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form "
    "text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds 33,928 / 65,820 / 106,890 / 142,520 / 200,000 and rates "
    "9.5% / 13.47% / 16.6% / 17.62% / 19% / 20% as printed in T4127 (Jul 2026) Prince "
    "Edward Island change notice and Table 8.1 (the 21% in the July notice is the "
    "prorated payroll rate for the second half of 2026; the rate for the year is 20%); "
    "tax_at_start calculated as the cumulative tax on the earlier brackets, exact, then "
    "rounded half-up to the cent, the way the 2025 printed constants come out (33,928 x "
    "9.5% = 3,223.16; plus 31,892 x 13.47% = 7,519.0124, 7,519.01; plus 41,070 x 16.6% = "
    "14,336.6324, 14,336.63; plus 35,630 x 17.62% = 20,614.6384, 20,614.64; plus 57,480 "
    "x 19% = 31,535.8384, 31,535.84), because the 2026 line 7 constants are not yet "
    "published."
)


def test_2026_brackets_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.095"), D("0.00")),
        (D("33928.00"), D("0.1347"), D("3223.16")),
        (D("65820.00"), D("0.166"), D("7519.01")),
        (D("106890.00"), D("0.1762"), D("14336.63")),
        (D("142520.00"), D("0.19"), D("20614.64")),
        (D("200000.00"), D("0.2"), D("31535.84")),
    ]
    assert data.values.up_to is None


def test_2026_brackets_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("33928.00", "0.00"),
        ("33928.01", "33928.00"),
        ("65820.00", "33928.00"),
        ("65820.01", "65820.00"),
        ("106890.00", "65820.00"),
        ("106890.01", "106890.00"),
        ("142520.00", "106890.00"),
        ("142520.01", "142520.00"),
        ("200000.00", "142520.00"),
        ("200000.01", "200000.00"),
        ("1000000.00", "200000.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2026, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)


@pytest.mark.parametrize(
    ("lower", "tax"),
    [
        ("33928", "3223.160"),
        ("65820", "7519.0124"),
        ("106890", "14336.6324"),
        ("142520", "20614.6384"),
        ("200000", "31535.8384"),
    ],
)
def test_each_constant_is_the_cumulative_tax_at_its_lower_bound_to_the_cent(
    lower: str, tax: str
) -> None:
    brackets = SOURCE.get(FAMILY, 2026, BRACKETS).values.brackets
    cumulative = D(0)
    for earlier, later in zip(brackets, brackets[1:], strict=False):
        cumulative += (later.lower - earlier.lower) * earlier.rate
        if later.lower == D(lower):
            break

    assert cumulative == D(tax)
    assert later.tax_at_start == cumulative.quantize(D("0.01"), rounding="ROUND_HALF_UP")


def test_2026_brackets_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.sources == SOURCES


def test_2026_brackets_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    path = root / "parameters" / "brackets" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
