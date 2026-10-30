"""The 2025 CPP monthly proration table, checked against CRA's Schedule 8.

T1-2025 Schedule 8 (form 5000-S8), Part 2: "Enter "12" on line A below unless any of the
following conditions apply"; "Box A: Enter the number of months that CPP applied in 2025."; the
"Monthly proration for 2025" table, in print five columns: "Number of months", "Maximum
pensionable earnings" (line B), "Maximum amount subject to second additional contributions"
(line C), "Additional maximum pensionable earnings" (line D) and "Maximum basic exemption" (line
E), a row for each number of months from 1 to 12. Each family below is one column, an
`amount_by_count` dataset keyed by the months in box A. The printed figures are dollars and
cents (the 12-month row is $71,300.00, $9,900.00, $81,200.00 and $3,500.00), so each is rounded
half-up to the cent, which changes none of them. Part 2's conditions a) to h) say when the months
are fewer than 12; the number of months is the filer's own input, not computed.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.amount_by_count import AmountForCount
from tax_engine.domain.errors import NoAmountForCountError
from tax_engine.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
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
S8_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"

# Made up for this test and not registered: the months, and the figure the capability reads.
MONTHS = ArtifactKind("ex/months", int)
FIGURE = ArtifactKind("ex/figure", Decimal)

# The table as printed, one row for each number of months: line B, line C, line D, line E.
PRINTED = {
    1: ("5941.67", "825.00", "6766.67", "291.67"),
    2: ("11883.33", "1650.00", "13533.33", "583.33"),
    3: ("17825.00", "2475.00", "20300.00", "875.00"),
    4: ("23766.67", "3300.00", "27066.67", "1166.67"),
    5: ("29708.33", "4125.00", "33833.33", "1458.33"),
    6: ("35650.00", "4950.00", "40600.00", "1750.00"),
    7: ("41591.67", "5775.00", "47366.67", "2041.67"),
    8: ("47533.33", "6600.00", "54133.33", "2333.33"),
    9: ("53475.00", "7425.00", "60900.00", "2625.00"),
    10: ("59416.67", "8250.00", "67666.67", "2916.67"),
    11: ("65358.33", "9075.00", "74433.33", "3208.33"),
    12: ("71300.00", "9900.00", "81200.00", "3500.00"),
}


@pytest.mark.parametrize(("column", "family"), list(enumerate(FAMILIES)))
def test_2025_table_is_the_printed_column_for_months_1_to_12(column: int, family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((months, D(row[column])) for months, row in PRINTED.items())
    )


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_table_is_rounded_half_up_to_the_cent(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    # The printed figures are in dollars and cents.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize("family", FAMILIES)
def test_2025_table_cites_the_schedule_8_text(family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)

    assert S8_TEXT in data.sources


@pytest.mark.parametrize(("column", "family"), list(enumerate(FAMILIES)))
def test_each_row_is_the_annual_figure_for_the_months_over_12(column: int, family: str) -> None:
    data = SOURCE.get(family, 2025, AMOUNT_BY_COUNT)
    annual = dict(data.values.rows)[12]

    # A cross-check of the printed rows, not a rule of the code: 71,300 x 5 / 12 =
    # 29,708.3333..., printed 29,708.33; 3,500 x 1 / 12 = 291.6666..., printed 291.67.
    for months, amount in data.values.rows:
        assert RoundTo(D("0.01"), RoundingMode.HALF_UP).apply(annual * months / 12) == amount


def test_the_12_month_row_is_the_annual_figures_of_the_cpp_rate_tables() -> None:
    # CRA, "CPP contribution rates, maximums and exemptions", 2025 row: maximum annual
    # pensionable earnings $71,300; basic exemption $3,500. "Second additional CPP contribution
    # rates and maximums", 2025 row: additional maximum annual pensionable earnings $81,200.
    rows = {
        family: dict(SOURCE.get(family, 2025, AMOUNT_BY_COUNT).values.rows) for family in FAMILIES
    }

    assert rows[MAXIMUM_PENSIONABLE_EARNINGS][12] == D("71300.00")
    assert rows[ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS][12] == D("81200.00")
    assert rows[BASIC_EXEMPTION][12] == D("3500.00")
    # Line C of the 12-month row is the band between the two ceilings.
    assert rows[SECOND_ADDITIONAL_EARNINGS_MAXIMUM][12] == D("9900.00")
    assert (
        rows[ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS][12] - rows[MAXIMUM_PENSIONABLE_EARNINGS][12]
        == rows[SECOND_ADDITIONAL_EARNINGS_MAXIMUM][12]
    )


@pytest.mark.parametrize(
    ("months", "family", "figure"),
    [
        # The 12 months of a full year, each of the four lines.
        (12, MAXIMUM_PENSIONABLE_EARNINGS, "71300.00"),
        (12, SECOND_ADDITIONAL_EARNINGS_MAXIMUM, "9900.00"),
        (12, ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS, "81200.00"),
        (12, BASIC_EXEMPTION, "3500.00"),
        # A part year: 5 months, and the first row.
        (5, MAXIMUM_PENSIONABLE_EARNINGS, "29708.33"),
        (5, BASIC_EXEMPTION, "1458.33"),
        (1, ADDITIONAL_MAXIMUM_PENSIONABLE_EARNINGS, "6766.67"),
    ],
)
def test_reads_the_row_for_the_months(months: int, family: str, figure: str) -> None:
    capability = AmountForCount(SOURCE.get(family, 2025, AMOUNT_BY_COUNT), MONTHS, FIGURE)

    result = capability.compute((Artifact(MONTHS, months),))

    assert result.outputs == (Artifact(FIGURE, D(figure)),)


@pytest.mark.parametrize("months", [0, 13])
def test_a_number_of_months_with_no_row_is_refused_not_guessed(months: int) -> None:
    # Part 2's table has rows for 1 to 12 months only; "0" on line A (conditions b, d and g) is
    # not a row, and is not carried over from the nearest one.
    capability = AmountForCount(
        SOURCE.get(MAXIMUM_PENSIONABLE_EARNINGS, 2025, AMOUNT_BY_COUNT), MONTHS, FIGURE
    )

    with pytest.raises(NoAmountForCountError):
        capability.compute((Artifact(MONTHS, months),))
