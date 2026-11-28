"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10), "Tax Credit for Career Extension", lines 10 to
50, as the Quebec take-home manifest wires them, one step per printed line (the form is its own
form, `ca-qc/tp752_pc`, so that TP-1 line 391 can read its line 50).

Form text (confirmed, 2026-10 edition): "Eligible work income (see the information on page 2) 10";
"Subtract line 11 from line 10. If the result is $7,655 or less, you are not entitled to the tax
credit. = 12"; "Subtract line 13 from line 12. = 14"; "- 15 7,655 00"; "Subtract $7,655 from line 14
(maximum $12,755). = 16"; "x 14% Multiply line 16 by 14%. = 35"; "Net income (line 275 of your
return; see the information on page 2) 36"; "- 37 57,660 00"; "Subtract $57,660 from line 36. If the
result is negative, enter 0. = 38"; "x 7% Multiply line 38 by 7%. = 39"; "Subtract line 39 from line
35. If the result is negative, enter 0. = 40"; "Income tax on taxable income (line 401 of your
return) 47"; "Add lines 359 through 367 of your return. x 14% - 48"; "Subtract line 48 from line 47.
If the result is negative, enter 0. = 49"; "Enter the amount from line 40 or line 49, whichever is
less. Carry this amount to line 391 of your return. Tax credit for career extension 50". The 2025-10
edition prints 7,500 / $12,500 / 56,500. The expected figures are computed in `tp752_pc_support.py`
from the printed lines (not a Revenu Quebec example).

Eligibility ("65 or over on December 31") is the `ca-qc/t1_birth_year.age_65_or_older` flag, applied
as Schedule B line 22 does: line 10 is the work income times the flag, so a filer born in 1962 or
later (2026), in 1961 or later (2025) or with no birth year has 0.00 on lines 10 to 14, no credit.
The "not entitled" test of line 12 is not a step: line 14 at or below 7,655 gives a line 16 at or
below 0, so line 40 and line 50 are 0.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca_qc.catalog import TP752_PC_LINE_11, TP752_PC_LINE_13
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.tp752_pc_support import FORM, lines_of, part

D = Decimal


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["7500", "7501", "7655", "7656", "12000", "20000", "70000"])
def test_every_printed_line_of_a_filer_born_in_1955_is_the_printed_arithmetic(
    take_home_service: TakeHomeService, year: int, salary: str
) -> None:
    actual, expected = lines_of(take_home_service, salary, year, 1955)

    assert actual == expected


@pytest.mark.parametrize(
    ("year", "line_15", "maximum", "line_35", "line_37"),
    [
        (2026, "7655.00", "12755.00", "1785.70", "57660.00"),
        (2025, "7500.00", "12500.00", "1750.00", "56500.00"),
    ],
)
def test_the_take_home_at_70000_born_1955_has_the_printed_figures_on_lines_10_to_37(
    take_home_service: TakeHomeService,
    year: int,
    line_15: str,
    maximum: str,
    line_35: str,
    line_37: str,
) -> None:
    # Line 14 less line 15 is 62,345.00 (2026) or 62,500.00 (2025): over the maximum, so line 16 is
    # the printed 12,755 or 12,500, and line 35 is 14% of it.
    actual, _ = lines_of(take_home_service, "70000", year, 1955)

    assert [str(actual[line]) for line in (10, 12, 14, 15, 16, 35, 37)] == [
        "70000.00",
        "70000.00",
        "70000.00",
        line_15,
        maximum,
        line_35,
        line_37,
    ]


@pytest.mark.parametrize(
    ("year", "salary", "line_16", "line_35"),
    [
        (2026, "7655", "0.00", "0.00"),
        (2026, "7656", "1.00", "0.14"),
        (2025, "7500", "0.00", "0.00"),
        (2025, "7501", "1.00", "0.14"),
    ],
)
def test_the_line_12_boundary_the_credit_starts_one_dollar_above_the_printed_figure(
    take_home_service: TakeHomeService, year: int, salary: str, line_16: str, line_35: str
) -> None:
    actual, _ = lines_of(take_home_service, salary, year, 1955)

    assert (str(actual[16]), str(actual[35])) == (line_16, line_35)


def test_line_16_and_line_35_are_signed_below_line_15_and_line_40_is_0(
    take_home_service: TakeHomeService,
) -> None:
    actual, expected = lines_of(take_home_service, "5000", 2026, 1955)

    assert str(actual[16]) == "-2655.00"
    assert str(actual[35]) == "-371.70"
    assert (actual[40], actual[50]) == (D("0.00"), D("0.00"))
    assert actual == expected


@pytest.mark.parametrize(("year", "born"), [(2026, 1961), (2025, 1960)])
def test_the_last_birth_year_of_the_age_65_flag_is_eligible(
    take_home_service: TakeHomeService, year: int, born: int
) -> None:
    actual, expected = lines_of(take_home_service, "70000", year, born)

    assert actual[10] == D("70000.00")
    assert actual[50] > 0
    assert actual == expected


@pytest.mark.parametrize(("year", "born"), [(2026, 1962), (2025, 1961), (2026, None), (2025, None)])
def test_a_younger_filer_or_a_blank_birth_year_has_no_work_income_and_no_credit(
    take_home_service: TakeHomeService, year: int, born: int | None
) -> None:
    actual, expected = lines_of(take_home_service, "70000", year, born)

    assert [actual[line] for line in (10, 12, 14, 40, 50)] == [D("0.00")] * 5
    assert actual == expected


def test_lines_11_and_13_are_subtracted_before_the_maximum(
    take_home_service: TakeHomeService,
) -> None:
    given = (
        Artifact(TP752_PC_LINE_11, D("5000.50")),
        Artifact(TP752_PC_LINE_13, D("1000.25")),
    )
    actual, expected = lines_of(take_home_service, "20000", 2026, 1955, *given)

    # 20,000.00 less 5,000.50 is 14,999.50 (line 12); less 1,000.25 is 13,999.25 (line 14); less
    # 7,655.00 is 6,344.25 (line 16, under the 12,755 maximum); at 14% 888.20 (line 35, half-up).
    assert [str(actual[line]) for line in (12, 14, 16, 35)] == [
        "14999.50",
        "13999.25",
        "6344.25",
        "888.20",
    ]
    assert actual == expected


def test_a_line_11_above_line_10_leaves_line_12_signed_and_the_credit_0(
    take_home_service: TakeHomeService,
) -> None:
    given = (Artifact(TP752_PC_LINE_11, D("5000")),)
    actual, expected = lines_of(take_home_service, "3000", 2026, 1955, *given)

    assert str(actual[12]) == "-2000.00"
    assert actual[50] == D("0.00")
    assert actual == expected


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_50_is_the_lesser_of_line_40_and_line_49(
    take_home_service: TakeHomeService, salary: str
) -> None:
    actual, _ = lines_of(take_home_service, salary, 2026, 1955)

    assert actual[50] == min(actual[40], actual[49])


def test_line_50_is_line_49_when_the_tax_is_the_lesser(take_home_service: TakeHomeService) -> None:
    # At $12,000 the tax on taxable income is under 14% of lines 359 and 361, so line 49 is 0.
    actual, _ = lines_of(take_home_service, "12000", 2026, 1955)

    assert actual[40] > 0
    assert actual[49] == D("0.00")
    assert actual[50] == D("0.00")


def test_the_form_is_the_career_extension_form_that_exports_line_50() -> None:
    declared = part("tp752_pc.yaml")

    assert declared["form"] == {
        "name": FORM,
        "title": "Tax Credit for Career Extension",
        "required": True,
        "exports": ["ca-qc/tp752_pc_line_50"],
    }
    assert declared["capabilities"] == []
