"""The 2025 datasets of the Form T1206 section "Dispositions of certain capital property - shares
subject to TOSI" (page 6), checked against the printed form.

Form T1206 (2025), read from the PDF (https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/
t1206-25e.pdf; no .txt is published). Four datasets, one for each figure the section prints:
- `ca/t1206_reserve_percentage`: "Applicable percentage for year of sale or year after sale (1)":
  "Year of sale 80%", "1st year 60%", "2nd year 40%", "3rd year 20%" and "4th year 0%", keyed by the
  number of years after the sale (0 for the year of sale); a year with no row is refused;
- `ca/t1206_under_18_percentage`: "Multiply the amount from line G by 1.15" for a filer under 18
  (keyed by the age answer: 0 for under 18, 1 for 18 or older, which takes 0);
- `ca/t1206_aged_18_or_older_percentage`: "multiply the capital gain ... by 50%" for a filer 18 or
  older (keyed by the age answer: 0 takes 0, 1 takes 50);
- `ca/t1206_rounding`: the calculations of the section are dollars-and-cents boxes, rounded half-up
  to the cent once, the owner's decision, as the form states no rounding rule.
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T1206_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/t1206-25e.pdf"
RESERVE_PERCENTAGE = "ca/t1206_reserve_percentage"
UNDER_18_PERCENTAGE = "ca/t1206_under_18_percentage"
AGED_18_OR_OLDER_PERCENTAGE = "ca/t1206_aged_18_or_older_percentage"
ROUNDING = "ca/t1206_rounding"

# The printed percentages of the reserve table, keyed by the years after the sale.
RESERVE_PRINTED = {0: "80", 1: "60", 2: "40", 3: "20", 4: "0"}
# The printed percentages of the two age branches, keyed by the age answer (0 under 18, 1 at 18 or
# older): line G times 1.15 for a filer under 18, and 50% for a filer 18 or older.
UNDER_18_PRINTED = {0: "115", 1: "0"}
AGED_18_OR_OLDER_PRINTED = {0: "0", 1: "50"}

# Made up for this test and not registered: the count and the output the capability reads and
# produces.
YEARS = ArtifactKind("ex/years_after_sale", int)
OUTPUT = ArtifactKind("ex/percentage", Decimal)


def rows_of(name: str) -> dict[int, Decimal]:
    data = SOURCE.get(name, 2025, AMOUNT_BY_COUNT)
    return {code: amount for code, amount in data.values.rows}


def test_2025_reserve_percentage_is_the_printed_table_by_years_after_the_sale() -> None:
    data = SOURCE.get(RESERVE_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((code, D(rate)) for code, rate in RESERVE_PRINTED.items())
    )
    assert T1206_PDF in data.sources


def test_the_reserve_table_has_a_row_for_the_year_of_sale_and_four_years_after_and_no_other() -> (
    None
):
    assert sorted(rows_of(RESERVE_PERCENTAGE)) == [0, 1, 2, 3, 4]


def test_the_reserve_percentages_are_80_60_40_20_and_0() -> None:
    rows = rows_of(RESERVE_PERCENTAGE)

    assert [rows[year] for year in range(5)] == [D("80"), D("60"), D("40"), D("20"), D("0")]


def test_2025_under_18_percentage_is_1_15_as_115_and_nothing_for_18_or_older() -> None:
    data = SOURCE.get(UNDER_18_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((code, D(rate)) for code, rate in UNDER_18_PRINTED.items())
    )
    assert T1206_PDF in data.sources


def test_2025_18_or_older_percentage_is_50_percent_and_nothing_for_under_18() -> None:
    data = SOURCE.get(AGED_18_OR_OLDER_PERCENTAGE, 2025, AMOUNT_BY_COUNT)

    assert data.values == AmountByCount(
        tuple((code, D(rate)) for code, rate in AGED_18_OR_OLDER_PRINTED.items())
    )
    assert T1206_PDF in data.sources


@pytest.mark.parametrize(
    "name",
    [RESERVE_PERCENTAGE, UNDER_18_PERCENTAGE, AGED_18_OR_OLDER_PERCENTAGE],
)
def test_the_percentage_tables_are_rounded_half_up_to_the_cent(name: str) -> None:
    assert SOURCE.get(name, 2025, AMOUNT_BY_COUNT).rounding == CENT


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT
    assert T1206_PDF in data.sources


@pytest.mark.parametrize("years", [5, 6])
def test_a_year_after_the_sale_with_no_row_is_refused(years: int) -> None:
    capability = AmountForCount(
        SOURCE.get(RESERVE_PERCENTAGE, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT
    )

    with pytest.raises(NoAmountForCountError):
        capability.compute((Artifact(YEARS, years),))


@pytest.mark.parametrize(
    ("years", "percentage"), [(0, "80"), (1, "60"), (2, "40"), (3, "20"), (4, "0")]
)
def test_the_printed_percentage_is_read_for_each_year_after_the_sale(
    years: int, percentage: str
) -> None:
    capability = AmountForCount(
        SOURCE.get(RESERVE_PERCENTAGE, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT
    )

    result = capability.compute((Artifact(YEARS, years),))

    assert result.outputs == (Artifact(OUTPUT, D(percentage)),)


def test_the_age_answer_of_18_or_older_takes_no_under_18_percentage() -> None:
    capability = AmountForCount(
        SOURCE.get(UNDER_18_PERCENTAGE, 2025, AMOUNT_BY_COUNT), YEARS, OUTPUT
    )

    assert capability.compute((Artifact(YEARS, 1),)).outputs == (Artifact(OUTPUT, D("0")),)
    assert capability.compute((Artifact(YEARS, 0),)).outputs == (Artifact(OUTPUT, D("115")),)
