"""The 2026 CPP monthly proration table, calculated from CRA T4127, 122nd Edition (January 2026).

The 2026 Schedule 8 (form 5000-S8) is not published. T4127 prints, for Canada except Quebec, the
2026 year's maximum pensionable earnings $74,600.00, the additional maximum pensionable earnings
$85,000.00, the second additional pensionable earnings $10,400.00 (the band between them) and,
from its CPP tables (Table 6.1 and Table 8.3), the basic exemption $3,500. Each of the four
families is the Schedule 8 "Monthly proration" column for those figures: for n months, the
annual figure x n / 12, rounded
half-up to the cent. CALCULATED, so each file is provisional and its second line states the
derivation. The same method reproduces every row of the 2025 files (annual figures 71,300, 9,900,
81,200 and 3,500), and the 2026 files keep the 2025 row layout: keys 1 to 12, no row for 0.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.parameter_shapes.amount_by_count import (
    AMOUNT_BY_COUNT,
    AmountByCount,
)

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
MAXIMUM_PENSIONABLE_EARNINGS = "ca/cpp_maximum_pensionable_earnings"
SECOND_ADDITIONAL_EARNINGS_MAXIMUM = "ca/cpp_second_additional_earnings_maximum"
ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS = "ca/cpp_additional_maximum_pensionable_earnings"
BASIC_EXEMPTION = "ca/cpp_basic_exemption"
FAMILIES = (
    MAXIMUM_PENSIONABLE_EARNINGS,
    SECOND_ADDITIONAL_EARNINGS_MAXIMUM,
    ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS,
    BASIC_EXEMPTION,
)
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_PREFIX = "# Derivation:"

# The annual figure of each family, for 2026 and for 2025.
ANNUAL_2026 = {
    MAXIMUM_PENSIONABLE_EARNINGS: D("74600"),
    SECOND_ADDITIONAL_EARNINGS_MAXIMUM: D("10400"),
    ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS: D("85000"),
    BASIC_EXEMPTION: D("3500"),
}
ANNUAL_2025 = {
    MAXIMUM_PENSIONABLE_EARNINGS: D("71300"),
    SECOND_ADDITIONAL_EARNINGS_MAXIMUM: D("9900"),
    ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS: D("81200"),
    BASIC_EXEMPTION: D("3500"),
}

# The table as calculated, one row for each number of months: maximum pensionable earnings,
# second additional earnings maximum, additional maximum pensionable earnings, basic exemption.
CALCULATED = {
    1: ("6216.67", "866.67", "7083.33", "291.67"),
    2: ("12433.33", "1733.33", "14166.67", "583.33"),
    3: ("18650.00", "2600.00", "21250.00", "875.00"),
    4: ("24866.67", "3466.67", "28333.33", "1166.67"),
    5: ("31083.33", "4333.33", "35416.67", "1458.33"),
    6: ("37300.00", "5200.00", "42500.00", "1750.00"),
    7: ("43516.67", "6066.67", "49583.33", "2041.67"),
    8: ("49733.33", "6933.33", "56666.67", "2333.33"),
    9: ("55950.00", "7800.00", "63750.00", "2625.00"),
    10: ("62166.67", "8666.67", "70833.33", "2916.67"),
    11: ("68383.33", "9533.33", "77916.67", "3208.33"),
    12: ("74600.00", "10400.00", "85000.00", "3500.00"),
}


def _parameters_file(family: str) -> list[str]:
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.split("/")[1]
    return (root / "parameters" / name / "2026.yaml").read_text().splitlines()


@pytest.mark.parametrize(("column", "family"), list(enumerate(FAMILIES)))
def test_2026_table_is_the_calculated_column_for_months_1_to_12(column: int, family: str) -> None:
    data = SOURCE.get(family, 2026, AMOUNT_BY_COUNT)

    assert data.tax_year == 2026
    assert data.values == AmountByCount(
        tuple((months, D(row[column])) for months, row in CALCULATED.items())
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_2026_table_is_rounded_half_up_to_the_cent(family: str) -> None:
    assert SOURCE.get(family, 2026, AMOUNT_BY_COUNT).rounding == CENT


@pytest.mark.parametrize("family", FAMILIES)
def test_2026_table_cites_t4127(family: str) -> None:
    assert T4127 in SOURCE.get(family, 2026, AMOUNT_BY_COUNT).sources


@pytest.mark.parametrize("family", FAMILIES)
def test_2026_table_has_the_2025_row_layout_months_1_to_12_and_no_row_for_0(family: str) -> None:
    rows_2026 = SOURCE.get(family, 2026, AMOUNT_BY_COUNT).values.rows
    rows_2025 = SOURCE.get(family, 2025, AMOUNT_BY_COUNT).values.rows

    assert [months for months, _ in rows_2026] == list(range(1, 13))
    assert [months for months, _ in rows_2026] == [months for months, _ in rows_2025]


@pytest.mark.parametrize("family", FAMILIES)
def test_the_12_month_row_is_the_annual_figure(family: str) -> None:
    assert dict(SOURCE.get(family, 2026, AMOUNT_BY_COUNT).values.rows)[12] == ANNUAL_2026[family]


def test_the_second_additional_row_is_the_band_between_the_two_ceilings() -> None:
    rows = {
        family: dict(SOURCE.get(family, 2026, AMOUNT_BY_COUNT).values.rows) for family in FAMILIES
    }

    # 85,000 - 74,600 = 10,400, in every row up to the rounding of each column.
    assert (
        rows[ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS][12] - rows[MAXIMUM_PENSIONABLE_EARNINGS][12]
        == rows[SECOND_ADDITIONAL_EARNINGS_MAXIMUM][12]
    )


@pytest.mark.parametrize(
    ("months", "family", "figure"),
    [
        (1, MAXIMUM_PENSIONABLE_EARNINGS, "6216.67"),
        (6, MAXIMUM_PENSIONABLE_EARNINGS, "37300.00"),
        (9, MAXIMUM_PENSIONABLE_EARNINGS, "55950.00"),
        (1, ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS, "7083.33"),
        (6, ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS, "42500.00"),
        (9, ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS, "63750.00"),
        (1, SECOND_ADDITIONAL_EARNINGS_MAXIMUM, "866.67"),
        (6, SECOND_ADDITIONAL_EARNINGS_MAXIMUM, "5200.00"),
        (9, SECOND_ADDITIONAL_EARNINGS_MAXIMUM, "7800.00"),
        (1, BASIC_EXEMPTION, "291.67"),
        (6, BASIC_EXEMPTION, "1750.00"),
        (9, BASIC_EXEMPTION, "2625.00"),
    ],
)
def test_spot_check_months_1_6_and_9(months: int, family: str, figure: str) -> None:
    rows = dict(SOURCE.get(family, 2026, AMOUNT_BY_COUNT).values.rows)

    assert rows[months] == D(figure)


@pytest.mark.parametrize("family", FAMILIES)
def test_the_annual_x_months_over_12_method_reproduces_every_2026_row(family: str) -> None:
    data = SOURCE.get(family, 2026, AMOUNT_BY_COUNT)

    # 74,600 x 1 / 12 = 6,216.6666..., half-up 6,216.67; 10,400 x 5 / 12 = 4,333.3333...
    for months, amount in data.values.rows:
        assert CENT.apply(ANNUAL_2026[family] * months / 12) == amount


@pytest.mark.parametrize("family", FAMILIES)
def test_the_same_method_reproduces_every_row_of_the_2025_files(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    # The check that the method is the one CRA printed: 71,300 x 1 / 12 = 5,941.6666...,
    # printed 5,941.67; 9,900 x 1 / 12 = 825.00; 81,200 x 1 / 12 = 6,766.6666..., printed 6,766.67.
    assert len(data.values.rows) == 12
    for months, amount in data.values.rows:
        assert CENT.apply(ANNUAL_2025[family] * months / 12) == amount


@pytest.mark.parametrize("family", FAMILIES)
def test_2026_file_starts_with_the_provisional_line_then_a_derivation_line(family: str) -> None:
    lines = _parameters_file(family)

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith(DERIVATION_PREFIX)
    assert "n/12" in lines[1]
    assert "half-up" in lines[1]
