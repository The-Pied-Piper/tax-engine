"""BC428 lines 46 to 53, the medical expenses, end to end (#1843). Form text (Form BC428, CRA
5010-C-25e.txt, confirmed): "Line 46 and line 58689: Amount from line 33099 of your return",
"Line 47: Amount from line 23600 of your return", "Line 48: Applicable rate 3%", "Line 49:
Line 47 multiplied by the percentage from line 48 =", "Line 50: Enter whichever is less:
$2,689 or the amount from line 49.", "Line 51: Line 46 minus line 50 (if negative, enter "0")
=", "Line 52 and line 58729: Allowable amount of medical expenses for other dependants (use
Worksheet BC428)", "Line 53 and line 58769: Line 51 plus line 52 =". At a 70,000 salary the
net income of line 47 is 69,335.00 (the T1 line 23600, the same figure
`test_take_home_on428_line_37.py` reads), so line 49 is 3% of it, 2,080.05. The 2,689.00
ceiling binds from a net income of 89,633.33. Hand figures, not a CRA example. A salary-only
caller gives neither line 46 nor line 52, and line 53 is 0.00.
"""

from __future__ import annotations

import pytest

from tests.jurisdictions.ca_bc.end_to_end.figures import D, figure, sheet

YEARS = [2025, 2026]
FORM = "bc428"


@pytest.mark.parametrize("year", YEARS)
def test_a_salary_only_caller_has_no_medical_expenses(year: int) -> None:
    worksheet = sheet(FORM, year)

    assert figure(worksheet, "bc428_net_income_line_47") == D("69335.00")
    assert figure(worksheet, "bc428_medical_expenses_rate_amount_line_49") == D("2080.05")
    assert figure(worksheet, "bc428_medical_expenses_limited_amount_line_50") == D("2080.05")
    assert figure(worksheet, "bc428_medical_expenses_over_limit_line_51") == D("0.00")
    assert figure(worksheet, "bc428_medical_expenses_line_53") == D("0.00")


@pytest.mark.parametrize("year", YEARS)
def test_line_51_is_line_46_less_the_threshold_and_line_53_adds_line_52(year: int) -> None:
    worksheet = sheet(
        FORM,
        year,
        bc428_medical_expenses_line_46="5000",
        bc428_other_dependants_medical_expenses_line_52="100.50",
    )

    assert figure(worksheet, "bc428_medical_expenses_over_limit_line_51") == D("2919.95")
    assert figure(worksheet, "bc428_medical_expenses_line_53") == D("3020.45")


@pytest.mark.parametrize("year", YEARS)
def test_line_51_is_0_when_line_46_is_below_the_threshold(year: int) -> None:
    worksheet = sheet(FORM, year, bc428_medical_expenses_line_46="2000")

    assert figure(worksheet, "bc428_medical_expenses_over_limit_line_51") == D("0.00")


@pytest.mark.parametrize("year", YEARS)
def test_line_52_alone_is_line_53_when_line_46_is_blank(year: int) -> None:
    worksheet = sheet(FORM, year, bc428_other_dependants_medical_expenses_line_52="750")

    assert figure(worksheet, "bc428_medical_expenses_line_53") == D("750.00")


@pytest.mark.parametrize("year", YEARS)
def test_line_53_reaches_line_54(year: int) -> None:
    blank = figure(sheet(FORM, year), "bc428_total_line_54")
    given = figure(
        sheet(FORM, year, bc428_other_dependants_medical_expenses_line_52="750"),
        "bc428_total_line_54",
    )

    assert given - blank == D("750.00")
