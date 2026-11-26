"""2025 `ca-pe/brackets`, checked against Form PE428 (CRA 5002-C, 2025), Part A.

Form text (confirmed 2026-11-26 from the text version, CRA_FORM_TEXT below; the PDF agrees on
every figure): "Column 1: Line 1 is $33,328.00 or less", "Line 3: 0.00", "Line 5: Rate 9.5%",
"Line 7: 0.00"; "Column 2: Line 1 is more than $33,328 but not more than $64,656", "Line 3:
33,328.00", "13.47%", "3,166.16"; "Column 3: more than $64,656 but not more than $105,000",
"64,656.00", "16.6%", "7,386.04"; "Column 4: more than $105,000 but not more than $140,000",
"105,000.00", "17.62%", "14,083.15"; "Column 5: more than $140,000", "140,000.00", "19%",
"20,250.15".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule. Column 5 has no
upper boundary, so the schedule has no `up_to` and covers every amount.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_pe.pe428_support import COLUMNS, parameter_source

D = Decimal
FAMILY = "ca-pe/brackets"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def _schedule() -> BracketSchedule:
    return parameter_source().get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_five_columns_as_printed() -> None:
    data = parameter_source().get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.095"), D("0.00")),
        (D("33328.00"), D("0.1347"), D("3166.16")),
        (D("64656.00"), D("0.166"), D("7386.04")),
        (D("105000.00"), D("0.1762"), D("14083.15")),
        (D("140000.00"), D("0.19"), D("20250.15")),
    ]
    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == COLUMNS


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = parameter_source().get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_pe428() -> None:
    assert parameter_source().get(FAMILY, 2025, BRACKETS).sources == (CRA_FORM_TEXT,)


def test_2025_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


@pytest.mark.parametrize("amount", ["0.00", "140000.00", "140000.01", "500000.00", "99999999.99"])
def test_the_table_covers_every_amount(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("33328.00", "0.00"),
        ("33328.01", "33328.00"),
        ("64656.00", "33328.00"),
        ("64656.01", "64656.00"),
        ("105000.00", "64656.00"),
        ("105000.01", "105000.00"),
        ("140000.00", "105000.00"),
        ("140000.01", "140000.00"),
        ("500000.00", "140000.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


def test_each_printed_constant_is_the_unrounded_tax_of_the_columns_below_it_to_the_cent() -> None:
    # The form's own check (never used to compute): the printed line 7 of each column equals the
    # exact tax of the full columns below it, rounded once to the cent.
    brackets = _schedule().brackets
    owed = D(0)
    for below, bracket in zip(brackets, brackets[1:], strict=False):
        owed += (bracket.lower - below.lower) * below.rate
        assert owed.quantize(D("0.01"), rounding=ROUND_HALF_UP) == bracket.tax_at_start
