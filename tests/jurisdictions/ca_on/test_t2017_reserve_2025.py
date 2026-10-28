"""The 2025 datasets of Form T2017 (2025), "Summary of Reserves on Dispositions of Capital
Property", checked against the printed form (page 3, "How do you calculate a reserve").

Form T2017 (2025), read from the PDF (https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2017/
t2017-25e.pdf; no .txt is published). Three datasets:
- `ca/t2017_four_year_percentage`: the table of a disposition with a four-year maximum: "Year of
  disposition (A)" 80%, "1st year: 60%", "2nd year: 40%", "3rd year: 20%" and "4th year: zero",
  keyed
  by the years after the disposition (0 for the year of disposition). The table has rows 5 to 9 at 0
  only so that the unchosen table of a nine-year row of lines 2 and 8 never raises; a four-year
  property has no reserve after its 4th year, and the printed table stops there;
- `ca/t2017_nine_year_percentage`: the table of a disposition with a nine-year maximum: "Year of
  disposition (A)" 90%, "1st year: 80%", "2nd year: 70%", "3rd year: 60%", "4th year: 50%", "5th
  year: 40%", "6th year: 30%", "7th year: 20%", "8th year: 10%" and "9th year: zero";
- `ca/t2017_rounding`: the calculations of the form are dollars-and-cents boxes, rounded half-up to
  the cent once, the owner's decision, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.amount_by_count import AmountForCount
from tax_calculator.domain.errors import NoAmountForCountError
from tax_calculator.domain.parameters.amount_by_count import AMOUNT_BY_COUNT, AmountByCount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T2017_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2017/t2017-25e.pdf"
FOUR_YEAR_PERCENTAGE = "ca/t2017_four_year_percentage"
NINE_YEAR_PERCENTAGE = "ca/t2017_nine_year_percentage"
ROUNDING = "ca/t2017_rounding"

# The printed percentages of the four-year table, keyed by the years after the disposition. The
# years 5 to 9 are not printed: they are zero, as the table is never read past the 4th year.
FOUR_YEAR_PRINTED = {
    0: "80",
    1: "60",
    2: "40",
    3: "20",
    4: "0",
    5: "0",
    6: "0",
    7: "0",
    8: "0",
    9: "0",
}
# The printed percentages of the nine-year table, keyed by the years after the disposition.
NINE_YEAR_PRINTED = {
    0: "90",
    1: "80",
    2: "70",
    3: "60",
    4: "50",
    5: "40",
    6: "30",
    7: "20",
    8: "10",
    9: "0",
}

# Made up for this test and not registered: the count and the output the capability reads and
# produces.
YEARS = ArtifactKind("ex/years_after_disposition", int)
OUTPUT = ArtifactKind("ex/percentage", Decimal)


def rows_of(name: str) -> dict[int, Decimal]:
    data = SOURCE.get(name, 2025, AMOUNT_BY_COUNT)
    return {code: amount for code, amount in data.values.rows}


def test_2025_four_year_percentage_is_the_printed_table_by_years_after_the_disposition() -> None:
    data = SOURCE.get(FOUR_YEAR_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((code, D(rate)) for code, rate in FOUR_YEAR_PRINTED.items())
    )
    assert T2017_PDF in data.sources


def test_2025_nine_year_percentage_is_the_printed_table_by_years_after_the_disposition() -> None:
    data = SOURCE.get(NINE_YEAR_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((code, D(rate)) for code, rate in NINE_YEAR_PRINTED.items())
    )
    assert T2017_PDF in data.sources


def test_the_four_year_table_has_a_row_for_each_year_from_0_to_9_and_no_other() -> None:
    assert sorted(rows_of(FOUR_YEAR_PERCENTAGE)) == list(range(10))


def test_the_four_year_percentages_are_80_60_40_20_and_zero_for_the_printed_years() -> None:
    rows = rows_of(FOUR_YEAR_PERCENTAGE)

    assert [rows[year] for year in range(5)] == [D("80"), D("60"), D("40"), D("20"), D("0")]


def test_the_four_year_table_is_zero_after_the_4th_year() -> None:
    rows = rows_of(FOUR_YEAR_PERCENTAGE)

    assert [rows[year] for year in range(5, 10)] == [D("0")] * 5


def test_the_nine_year_percentages_step_down_from_90_to_zero_in_the_ninth_year() -> None:
    rows = rows_of(NINE_YEAR_PERCENTAGE)

    assert [rows[year] for year in range(10)] == [
        D("90"),
        D("80"),
        D("70"),
        D("60"),
        D("50"),
        D("40"),
        D("30"),
        D("20"),
        D("10"),
        D("0"),
    ]


@pytest.mark.parametrize("name", [FOUR_YEAR_PERCENTAGE, NINE_YEAR_PERCENTAGE])
def test_the_percentage_tables_are_rounded_half_up_to_the_cent(name: str) -> None:
    assert SOURCE.get(name, 2025, AMOUNT_BY_COUNT).rounding == CENT


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert T2017_PDF in data.sources


@pytest.mark.parametrize("name", [FOUR_YEAR_PERCENTAGE, NINE_YEAR_PERCENTAGE])
def test_a_year_past_the_table_is_refused_not_read_as_zero(name: str) -> None:
    capability = AmountForCount(SOURCE.get(name, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT)

    with pytest.raises(NoAmountForCountError):
        capability.compute((Artifact(YEARS, 10),))


@pytest.mark.parametrize(
    ("years", "percentage"),
    [(0, "80"), (1, "60"), (2, "40"), (3, "20"), (4, "0")],
)
def test_the_four_year_percentage_is_read_for_each_year_after_the_disposition(
    years: int, percentage: str
) -> None:
    capability = AmountForCount(
        SOURCE.get(FOUR_YEAR_PERCENTAGE, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT
    )

    result = capability.compute((Artifact(YEARS, years),))

    assert result.outputs == (Artifact(OUTPUT, D(percentage)),)


@pytest.mark.parametrize(
    ("years", "percentage"),
    [(0, "90"), (1, "80"), (4, "50"), (7, "20"), (8, "10"), (9, "0")],
)
def test_the_nine_year_percentage_is_read_for_each_year_after_the_disposition(
    years: int, percentage: str
) -> None:
    capability = AmountForCount(
        SOURCE.get(NINE_YEAR_PERCENTAGE, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT
    )

    result = capability.compute((Artifact(YEARS, years),))

    assert result.outputs == (Artifact(OUTPUT, D(percentage)),)
