"""2025 `ca-ns/brackets`, checked against Form NS428 (CRA 5003-C, 2025), Part A.

Form text (confirmed 2026-11-26 from the PDF 5003-c-25e; the .txt, CRA_FORM_TEXT below, agrees
on every figure): "Column 1: Line 1 is $30,507 or less", "Line 3: 0.00", "Line 5: 8.79%",
"Line 7: 0.00"; "Column 2: Line 1 is more than $30,507 but not more than $61,015",
"Line 3: 30,507.00", "14.95%", "2,681.57";
"Column 3: ... more than $61,015 but not more than $95,883", "61,015.00", "16.67%", "7,242.51";
"Column 4: ... more than $95,883 but not more than $154,650", "95,883.00", "17.5%", "13,055.01";
"Column 5: Line 1 is more than $154,650", "154,650.00", "21%", "23,339.23".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule. Column 5 has no
upper boundary, so the schedule has no `up_to` and covers every amount.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_ns.ns428_support import COLUMNS, parameter_source

D = Decimal
FAMILY = "ca-ns/brackets"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"


def _schedule() -> BracketSchedule:
    return parameter_source().get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_five_columns_as_printed() -> None:
    data = parameter_source().get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.0879"), D("0.00")),
        (D("30507.00"), D("0.1495"), D("2681.57")),
        (D("61015.00"), D("0.1667"), D("7242.51")),
        (D("95883.00"), D("0.175"), D("13055.01")),
        (D("154650.00"), D("0.21"), D("23339.23")),
    ]
    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == COLUMNS


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = parameter_source().get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_ns428() -> None:
    assert parameter_source().get(FAMILY, 2025, BRACKETS).sources == (CRA_FORM_TEXT,)


def test_2025_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


@pytest.mark.parametrize("amount", ["0.00", "154650.00", "154650.01", "500000.00", "99999999.99"])
def test_the_table_covers_every_amount(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("30507.00", "0.00"),
        ("30507.01", "30507.00"),
        ("61015.00", "30507.00"),
        ("61015.01", "61015.00"),
        ("95883.00", "61015.00"),
        ("95883.01", "95883.00"),
        ("154650.00", "95883.00"),
        ("154650.01", "154650.00"),
        ("500000.00", "154650.00"),
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
