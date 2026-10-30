"""The 2025 rental income figures (T776 Parts 3 and 4, T1 lines 12599 and 12600), checked against
CRA's forms.

2025 Form T776 (Statement of Real Estate Rentals), Part 4: "Line 9366: Non-compliant amount for
short-term rentals (amount B from Chart A)"; Chart A: "Column 3: Related portion of the total from
line 9365 of Part 4", "Column 4: Number of days the residential property was a non compliant
short-term rental", "Column 5: Number of days the residential property was a short-term rental",
"Column 6: Non-compliant amount (column 3 multiplied by column 4 divided by column 5)" and "Line B:
Total non-compliant amount of expenses for short-term rentals: Total of column 6 (enter on line
9366 of Part 4)". Line 9366 has no figure of its own, so its one dataset is a `rounding_only` one:
each row of column 6 is a dollars-and-cents box, rounded half-up to the cent, the owner's decision,
as the form states no rounding rule. The other lines of Parts 3 and 4 only add and subtract
amounts already in cents, so they have no dataset.

The dataset is tested with the capability that reads it, on the registered kinds; the lines
together, from the gross rents to T1 lines 12599 and 12600, are in test_end_to_end_2025.py and
`returns/2025_return_ad.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.capabilities.short_term_rental_non_compliant_expenses import (
    ShortTermRentalNonCompliantExpenses,
)
from tax_engine.jurisdictions.ca.catalog import (
    GROSS_RENTAL_INCOME,
    RENTAL_DEDUCTIBLE_EXPENSES,
    RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS,
    RENTAL_NON_COMPLIANT_EXPENSES,
    SHORT_TERM_RENTAL_DAYS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS,
    SHORT_TERM_RENTAL_RELATED_EXPENSES,
    SHORT_TERM_RENTAL_UNITS,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/short_term_rental_non_compliant_rounding"
T776_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t776/t776-25e.txt"
T776_FILE = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "t776-25e.txt"
T1_FILE = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "5006-r-25e.txt"


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Chart A column 6, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_dataset_cites_only_the_t776_text() -> None:
    assert SOURCE.get(FAMILY, 2025, ROUNDING_ONLY).sources == (T776_TEXT,)


def test_the_dataset_header_quotes_t776_as_the_form_prints_it() -> None:
    header = dataset_header(FAMILY).lower()
    form = squashed(T776_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in (
        "line 9366: non-compliant amount for short-term rentals (amount b from chart a)",
        "column 6: non-compliant amount (column 3 multiplied by column 4 divided by column 5)",
        "line b: total non-compliant amount of expenses for short-term rentals: total of column 6 "
        "(enter on line 9366 of part 4)",
    ):
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_the_dataset_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(FAMILY).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header


def test_the_form_text_in_the_repository_is_the_text_the_wiring_is_checked_against() -> None:
    t776 = squashed(T776_FILE.read_text(encoding="utf-8-sig"))

    for printed in (
        "Line 8140: Total of your gross rents for short-term rentals in the year you receive them"
        ' (add amounts under "Gross rents for short-term rentals")',
        "Line 8141: Total of all your gross rents in the year you receive them (add lines under"
        ' "Gross rents for all units").',
        "Line 8230: Other income (for example, premiums and leases, sharecropping)",
        "Line 8299: Total gross rental income: Enter this amount on your income tax and benefit"
        " return on line 12599 (line 8141 plus line 8230)",
        'Line A: Total expenses (add amounts listed under "Total expenses")',
        'Line 9949: Total for personal portion (add amounts listed under "Personal portion of'
        ' total expenses")',
        'Line 9365: Total for short-term rental portion (add amounts listed under "Short-term'
        ' rental portion of total expenses")',
        "Line 9366: Non-compliant amount for short-term rentals (amount B from Chart A)",
        "Line 1: Deductible expenses (amount A minus line 9949 minus line 9366)",
        "Line 9369: Net income (loss) before adjustments (total gross rental income from line"
        " 8299 minus deductible expenses from amount 1)",
        "Line 2: Co-owners: calculate your share of net income from line 9369. Enter your result"
        " on amount 2",
        "Line 9945: Other expenses of the co-owner: other deductible expenses you have as a"
        " co-owner which you did not deduct elsewhere",
        "Line 3: Subtotal (amount 2 minus line 9945)",
        "Line 9947: Recaptured capital cost allowance (co-owners: enter your share of the amount)",
        "Line 4: Subtotal (amount 3 plus line 9947)",
        "Line 9948: Terminal loss (co-owners: enter your share of the amount)",
        "Line 5: Subtotal (amount 4 minus line 9948)",
        "Line 9936: Total CCA claim for the year (amount ii from Area A minus any personal part"
        " of CCA, and any CCA for business-use-of home expenses)",
        "Line 6: Net income (loss) (amount 5 minus line 9936)",
        "Line 7: Partners: your share of amount 6, or the amount from your T5013 slip, Statement"
        " of Partnership Income",
        "Line 9974: Partners: GST/HST rebate for partners received in the year",
        "Line 9943: Partners: other expenses of the partner",
        "Line 9946: Your net income (loss): For sole proprietors or co-owners, enter the result"
        " from amount 6. For partnerships, enter the result from amount 7 plus line 9974 minus"
        " line 9943. Enter this amount on line 12600 of your income tax and benefit return",
    ):
        assert printed in t776, printed
    t1 = squashed(T1_FILE.read_text(encoding="utf-8-sig"))
    for printed in (
        "Line 13: Rental income (complete Form T776)",
        "Line 12599: Gross",
        "Line 12600: Net",
        "Line 33 and line 15000: Line 28 plus line 32 Total income =",
    ):
        assert printed in t1, printed


@pytest.mark.parametrize(
    "line",
    [
        (8521, "Advertising"),
        (8690, "Insurance"),
        (8710, "Interest and bank charges"),
        (8810, "Office expenses"),
        (8860, "Professional fees (including legal and accounting fees)"),
        (8871, "Management and administration fees"),
        (8960, "Repairs and maintenance"),
        (9060, "Salaries, wages and benefits (including employer's contributions)"),
        (9180, "Property taxes"),
        (9200, "Travel"),
        (9220, "Utilities"),
        (9281, "Motor vehicle expenses (not including capital cost allowance)"),
        (9270, "Other expenses"),
    ],
)
def test_the_form_prints_each_of_the_thirteen_expense_lines_with_three_boxes(
    line: tuple[int, str],
) -> None:
    t776 = squashed(T776_FILE.read_text(encoding="utf-8-sig"))
    number, label = line
    printed = (
        f"Line {number}: {label} Total expenses ^ Personal portion of total expenses ^ "
        "Short-term rental portion of total expenses ^"
    )

    assert printed in t776


# --- line 9366, Chart A line B -------------------------------------------------------------------


def units(*rows: tuple[str, int, int]) -> Artifact[RecordList]:
    """A `ca/short_term_rental_units` artifact of one record per (column 3, 4, 5) row."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            SHORT_TERM_RENTAL_RELATED_EXPENSES: D(expenses),
            SHORT_TERM_RENTAL_NON_COMPLIANT_DAYS: non_compliant,
            SHORT_TERM_RENTAL_DAYS: days,
        }
        for expenses, non_compliant, days in rows
    ]
    return Artifact(SHORT_TERM_RENTAL_UNITS, RecordList(SHORT_TERM_RENTAL_UNITS.fields, records))


def line_9366(*rows: tuple[str, int, int]) -> Decimal:
    capability = ShortTermRentalNonCompliantExpenses(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY),
        SHORT_TERM_RENTAL_UNITS,
        RENTAL_NON_COMPLIANT_EXPENSES,
    )
    (output,) = capability.compute((units(*rows),)).outputs
    assert output.kind == RENTAL_NON_COMPLIANT_EXPENSES
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        # The ticket's example: 900 of related expenses, 30 non-compliant days of 90.
        ((("900", 30, 90),), "300.00"),
        ((), "0"),
        # 100 x 2 / 3 = 66.666..., half-up to 66.67.
        ((("100", 2, 3),), "66.67"),
        # 0.03 x 1 / 2 = 0.015, a tie, up to 0.02; 0.01 x 1 / 3 = 0.00333..., down to 0.00.
        ((("0.03", 1, 2),), "0.02"),
        ((("0.01", 1, 3),), "0.00"),
        # Each row is rounded on its own before the rows are added: 66.67 + 300.00.
        ((("900", 30, 90), ("100", 2, 3)), "366.67"),
    ],
)
def test_line_9366_is_chart_a_line_b_with_each_row_rounded_half_up_to_the_cent(
    rows: tuple[tuple[str, int, int], ...], expected: str
) -> None:
    assert line_9366(*rows) == D(expected)


def test_a_rental_loss_of_2000_is_line_9369_below_zero() -> None:
    # Line 9369 "Net income (loss) before adjustments (total gross rental income from line 8299
    # minus deductible expenses from amount 1)": gross rental income of 10000.00 less deductible
    # expenses of 12000.00 is a loss of 2000.00, kept with its sign.
    capability = Subtract(
        GROSS_RENTAL_INCOME, RENTAL_DEDUCTIBLE_EXPENSES, RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS
    )

    result = capability.compute(
        (
            Artifact(GROSS_RENTAL_INCOME, D("10000.00")),
            Artifact(RENTAL_DEDUCTIBLE_EXPENSES, D("12000.00")),
        )
    )

    assert result.outputs == (Artifact(RENTAL_NET_INCOME_BEFORE_ADJUSTMENTS, D("-2000.00")),)
