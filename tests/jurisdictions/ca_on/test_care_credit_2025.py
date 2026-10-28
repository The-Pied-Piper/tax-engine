"""The 2025 Ontario CARE credit's table and rounding, checked against CRA's Schedule ON479-A.

2025 Schedule ON479-A (form 5006-TCA), "Ontario Childcare Access and Relief from Expenses (CARE)
Tax Credit": line 7 "If your family adjusted income on line 5 is "0", enter 75%. If not, enter the
tax credit rate that applies to your family adjusted income from the table below."; the table
"Family adjusted income and Tax credit rate", from "more than $0 but not more than $20,000: 75%"
to "more than $150,000: 0%"; line 8 "Line 6 multiplied by the percentage from line 7 Enter this
amount on line 63050 of your Form ON479.".

The yearly table is ON479-A's copied row for row, none derived, the 9% row as printed ("more than
$132,000 but not more than $136,500: 9%", overlapping "more than $135,600 but not more than
$139,200: 7%") and commented as such. Each rate is a printed figure, so line 7 is not rounded. Line
8 is a dollars-and-cents box, so the product rounds half-up to the cent, the rule of a
`rounding_only` dataset of its own.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities.apply_chosen_rate import ApplyChosenRate
from tax_calculator.jurisdictions.ca_on.capabilities.rate_by_income_band import RateByIncomeBand
from tests.jurisdictions.ca_on.capabilities.on479a_table import (
    FAMILY_INCOME,
    ON479A_ROWS,
    on479a_table,
)

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
TABLE_FAMILY = "ca-on/care_credit_rate"
ROUNDING_FAMILY = "ca-on/care_credit_rounding"
ON479A_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-tca/5006-tca-25e.txt"
FORM_TEXT = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "5006-tca-25e.txt"

# Made up for this test and not registered: line 6 (the child care expenses deduction), line 7
# (the rate) and line 8 (the credit).
CHILD_CARE = ArtifactKind("ex/child_care", Decimal)
RATE_LINE = ArtifactKind("ex/rate", Rate)
CREDIT = ArtifactKind("ex/credit", Decimal)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_lines(family: str) -> list[str]:
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca-on")]
    return (root / "parameters" / family.partition("/")[2] / "2025.yaml").read_text().splitlines()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    lines = dataset_lines(family)
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def rate_for(income: str) -> Rate:
    """Line 7 for a family adjusted income, from the real dataset."""
    capability = RateByIncomeBand(
        SOURCE.get(TABLE_FAMILY, 2025, RATE_TABLE), FAMILY_INCOME, RATE_LINE
    )

    result = capability.compute((Artifact(FAMILY_INCOME, D(income)),))

    (output,) = result.outputs
    assert isinstance(output.value, Rate)
    return output.value


def credit_for(child_care: str, rate: str) -> Decimal:
    """Line 8 for the child care expenses deduction (line 6) and the rate (line 7)."""
    capability = ApplyChosenRate(
        SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY), CHILD_CARE, RATE_LINE, CREDIT
    )

    result = capability.compute(
        (Artifact(CHILD_CARE, D(child_care)), Artifact(RATE_LINE, Rate(D(rate))))
    )

    (output,) = result.outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_2025_table_is_the_forms_rows_as_printed() -> None:
    data = SOURCE.get(TABLE_FAMILY, 2025, RATE_TABLE)

    assert data.values == on479a_table()
    assert data.values.rate_at_zero == Rate(D("0.75"))
    assert len(data.values.rows) == len(ON479A_ROWS) == 39
    # Line 7 states the rate as printed, so nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_table_enters_the_overlapping_9_percent_row_as_printed() -> None:
    rows = SOURCE.get(TABLE_FAMILY, 2025, RATE_TABLE).values.rows

    nine, seven = rows[33], rows[34]
    assert (nine.more_than, nine.not_more_than, nine.rate) == (
        D("132000"),
        D("136500"),
        Rate(D("0.09")),
    )
    assert (seven.more_than, seven.not_more_than, seven.rate) == (
        D("135600"),
        D("139200"),
        Rate(D("0.07")),
    )


def test_2025_table_comments_why_the_9_percent_row_overlaps_the_next() -> None:
    lines = dataset_lines(TABLE_FAMILY)
    row = next(i for i, line in enumerate(lines) if "136500" in line)

    # The comment is on the row's own lines or just above them.
    nearby = squashed("\n".join(line for line in lines[max(0, row - 4) : row + 2] if "#" in line))
    assert "135,600" in nearby or "135600" in nearby


def test_2025_table_cites_only_the_on479_a_text() -> None:
    assert SOURCE.get(TABLE_FAMILY, 2025, RATE_TABLE).sources == (ON479A_TEXT,)


def test_2025_rounding_is_half_up_to_the_cent_with_no_values() -> None:
    data = SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # ON479-A line 8, a dollars-and-cents box: half-up to the cent (the owner's decision, as the
    # form states no rounding rule).
    assert data.rounding == CENT


def test_2025_rounding_cites_only_the_on479_a_text() -> None:
    assert SOURCE.get(ROUNDING_FAMILY, 2025, ROUNDING_ONLY).sources == (ON479A_TEXT,)


@pytest.mark.parametrize(
    ("family", "quotes"),
    [
        (
            TABLE_FAMILY,
            (
                "line 7",
                'if your family adjusted income on line 5 is "0", enter 75%.',
                "enter the tax credit rate that applies to your family adjusted income from the "
                "table below.",
                "family adjusted income and tax credit rate",
            ),
        ),
        (
            ROUNDING_FAMILY,
            (
                "line 8",
                "line 6 multiplied by the percentage from line 7",
                "enter this amount on line 63050 of your form on479.",
            ),
        ),
    ],
)
def test_each_dataset_header_quotes_on479_a_as_the_form_prints_it(
    family: str, quotes: tuple[str, ...]
) -> None:
    header = dataset_header(family).lower()
    form = squashed(FORM_TEXT.read_text(encoding="utf-8-sig")).lower()

    for quoted in quotes:
        assert quoted in header, quoted
        assert quoted in form, quoted


@pytest.mark.parametrize(
    ("income", "rate"),
    [
        # Line 7: "If your family adjusted income on line 5 is "0", enter 75%."
        ("0", "0.75"),
        ("0.01", "0.75"),
        ("20000", "0.75"),
        ("20000.01", "0.73"),
        ("22500", "0.73"),
        # The acceptance figure: 50,000 is "more than $45,000 but not more than $50,000: 55%".
        ("50000", "0.55"),
        ("50000.01", "0.53"),
        # Returns F, G and M: 59,435.00 is more than $55,000 but not more than $60,000.
        ("59435", "0.51"),
        # Return Y: 89,435.00 is more than $88,800 but not more than $92,400.
        ("89435", "0.33"),
        ("60000", "0.51"),
        ("60000.01", "0.49"),
        ("132000", "0.11"),
        ("132000.01", "0.09"),
        # The overlap as printed: up to 135,600 the 9% row, then the later row (7%) wins, even
        # below the 9% row's printed $136,500.
        ("135600", "0.09"),
        ("135600.01", "0.07"),
        ("136500", "0.07"),
        ("139200", "0.07"),
        ("139200.01", "0.05"),
        ("150000", "0.01"),
        ("150000.01", "0"),
        ("1000000", "0"),
    ],
)
def test_line_7_is_the_rate_of_the_row_the_family_adjusted_income_falls_in(
    income: str, rate: str
) -> None:
    assert rate_for(income) == Rate(D(rate))


def test_line_7_is_75_percent_for_a_family_adjusted_income_of_0_and_for_the_first_row() -> None:
    assert rate_for("0") == rate_for("20000") == Rate(D("0.75"))


@pytest.mark.parametrize(
    ("child_care", "rate", "credit"),
    [
        # The worked example: family adjusted income 50,000 -> 55%; 5,000 x 55%.
        ("5000", "0.55", "2750.00"),
        # Returns F, G and M: 5,000 at 51%.
        ("5000", "0.51", "2550.00"),
        # Return Y: 5,000 at 33%.
        ("5000", "0.33", "1650.00"),
        ("0", "0.75", "0.00"),
        # 1234.56 x 57% = 703.6992, rounded half-up to 703.70.
        ("1234.56", "0.57", "703.70"),
        # 0.10 x 75% = 0.075, a tie, up to 0.08; 0.01 x 49% = 0.0049, down to 0.00.
        ("0.10", "0.75", "0.08"),
        ("0.01", "0.49", "0.00"),
        # 0.01 x 55% = 0.0055, up to 0.01.
        ("0.01", "0.55", "0.01"),
        ("5000", "0", "0.00"),
    ],
)
def test_line_8_is_line_6_times_line_7_rounded_half_up_to_the_cent(
    child_care: str, rate: str, credit: str
) -> None:
    assert credit_for(child_care, rate) == D(credit)
