"""The Quebec return computes TP-752.PC-V, "Tax Credit for Career Extension" (2025-10, 2026-10),
and TP-1 line 391 carries its line 50 ("Carry this amount to line 391 of your return").

The tests run the real engine over the whole Quebec return. A filer 65 or over on December 31 (born
in 1960 or earlier for 2025, in 1961 or earlier for 2026) takes the credit: line 10 is the work
income (Work Chart 201 line 6, the salary when nothing else is given), line 16 is line 14 less 7,500
(2025) or 7,655 (2026) at most 12,500 or 12,755, line 35 is 14% of it, line 38 is line 36 (TP-1 line
275) over 56,500 or 57,660 (not below 0), line 39 is 7% of that, line 40 is line 35 less line 39
(not below 0), line 48 is 14% of lines 359 and 361, line 49 is line 47 (line 401) less line 48 (not
below 0) and line 50 is the lesser of lines 40 and 49. The expected figures are computed by
`tp752_pc_support.printed_form` from the printed lines and from the figures the form reads in the
same return (lines 275, 401, 359 and 361), not from a Revenu Quebec example.

Take-home: born 1955, salary $70,000, 2026: line 35 is 14% of 12,755 = 1,785.70 and line 39 is 7% of
line 36 over 57,660, so line 40 is 1,785.70 less that; line 49 is far larger (the tax is over
$10,000), so line 50 is line 40. In 2025 line 35 is 14% of 12,500 = 1,750.00. "Net income $83,170 or
more" (2026; $81,500 in 2025) is no credit: 14% of the maximum equals 7% of the 25,510 (25,000 in
2025) above the threshold, so line 39 equals line 35 there.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    LAST_BIRTH_YEAR,
    NO_CREDIT_FROM_LINE_36,
    Reads,
    printed_form,
)
from tests.kinds import bundled_kinds

D = Decimal
QUEBEC = JurisdictionCode("CA-QC")
FORM = "ca-qc/tp752_pc"
PART_A = "ca-qc/tp1_credits_lines_350_to_361"
PRINTED_LINES = (10, 12, 14, 15, 16, 35, 36, 37, 38, 39, 40, 47, 48, 49, 50)


class Run:
    """One run of the whole Quebec return."""

    def __init__(self, year: int, salary: str, born: int | None) -> None:
        given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
        if born is not None:
            given.append(Artifact(BIRTH_YEAR, born))
        self.year, self.salary, self.born = year, salary, born
        self.sheets = build_tax_computation().compute(
            TaxCalculationRequest(QUEBEC, year, tuple(given))
        )

    def get(self, form: str, identifier: str) -> Decimal:
        value = self.sheets[form][0].get(bundled_kinds().kind(identifier)).value
        assert isinstance(value, Decimal)
        return value

    def form_line(self, line: int) -> Decimal:
        return self.get(FORM, f"ca-qc/tp752_pc_line_{line}")

    def reads(self) -> Reads:
        return Reads(
            work_income=D(self.salary),
            net_income=self.get("ca-qc/tp1_net_income", "ca-qc/tp1_net_income_line_275"),
            income_tax=self.get("ca-qc/tp1_tax", "ca-qc/tp1_income_tax_on_taxable_income_line_401"),
            line_359=self.get(PART_A, "ca-qc/tp1_line_359"),
            line_361=self.get(PART_A, "ca-qc/tp1_age_living_alone_retirement_amount_line_361"),
        )

    def printed(self) -> dict[int, Decimal]:
        return printed_form(self.year, self.reads(), born=self.born)


def salary_with_net_income(year: int, born: int, target: int) -> str:
    """The salary whose TP-1 line 275 is `target`: above the QPP and work deduction maximums each
    extra dollar of salary is a dollar of net income, so one probe finds it."""
    probe = target + 5000
    net = Run(year, str(probe), born).reads().net_income
    salary = probe + (target - int(net))
    assert Run(year, str(salary), born).reads().net_income == D(target)
    return str(salary)


@pytest.mark.parametrize(("year", "born"), [(2026, 1955), (2025, 1955)])
@pytest.mark.parametrize("salary", ["7500", "7501", "7655", "7656", "12000", "20000", "70000"])
def test_every_printed_line_is_the_printed_arithmetic_for_a_filer_born_in_1955(
    year: int, born: int, salary: str
) -> None:
    run = Run(year, salary, born)

    assert {line: run.form_line(line) for line in PRINTED_LINES} == {
        line: value for line, value in run.printed().items() if line in PRINTED_LINES
    }


@pytest.mark.parametrize(("year", "line_35"), [(2026, "1785.70"), (2025, "1750.00")])
def test_the_take_home_at_70000_born_1955_is_line_35_less_7_percent_of_line_36_over_the_threshold(
    year: int, line_35: str
) -> None:
    run = Run(year, "70000", 1955)
    threshold = {2026: D("57660"), 2025: D("56500")}[year]
    line_36 = run.form_line(36)

    assert str(run.form_line(35)) == line_35
    assert line_36 > threshold
    expected = D(line_35) - ((line_36 - threshold) * D("0.07")).quantize(D("0.01"), ROUND_HALF_UP)
    assert run.form_line(40) == expected
    assert run.form_line(49) > run.form_line(40)
    assert run.form_line(50) == expected


@pytest.mark.parametrize("year", [2026, 2025])
def test_line_391_is_line_50_and_line_399_adds_it(year: int) -> None:
    run = Run(year, "70000", 1955)
    credits = "ca-qc/tp1_credits"

    assert run.form_line(50) > 0
    assert run.get(credits, "ca-qc/tp1_line_391") == run.form_line(50)
    assert run.get(credits, "ca-qc/tp1_non_refundable_tax_credits_line_399") == (
        run.get(credits, "ca-qc/tp1_line_377_1")
        + run.get(credits, "ca-qc/tp1_line_389")
        + run.get(credits, "ca-qc/tp1_union_dues_credit_line_397")
        + run.form_line(50)
    )


@pytest.mark.parametrize("year", [2026, 2025])
def test_a_net_income_at_the_printed_no_credit_figure_gives_0_and_one_dollar_under_gives_7_cents(
    year: int,
) -> None:
    last = NO_CREDIT_FROM_LINE_36[year]
    born = LAST_BIRTH_YEAR[year]
    results = {}
    for net_income in (last - 1, last, last + 1):
        run = Run(year, salary_with_net_income(year, born, int(net_income)), born)
        assert run.form_line(36) == net_income
        assert {line: run.form_line(line) for line in PRINTED_LINES} == {
            line: value for line, value in run.printed().items() if line in PRINTED_LINES
        }
        results[int(net_income - last)] = run.form_line(50)

    assert results == {-1: D("0.07"), 0: D("0.00"), 1: D("0.00")}


@pytest.mark.parametrize(
    ("year", "born", "credit"),
    [(2026, 1961, True), (2026, 1962, False), (2025, 1960, True), (2025, 1961, False)],
)
def test_the_credit_is_for_a_filer_65_or_over_on_december_31_of_the_tax_year(
    year: int, born: int, credit: bool
) -> None:
    run = Run(year, "70000", born)

    assert (run.form_line(50) > 0) is credit
    assert run.form_line(10) == (D("70000.00") if credit else D("0.00"))
    assert run.get("ca-qc/tp1_credits", "ca-qc/tp1_line_391") == run.form_line(50)


@pytest.mark.parametrize("year", [2026, 2025])
def test_a_blank_birth_year_has_no_credit_and_line_391_is_0(year: int) -> None:
    run = Run(year, "70000", None)

    assert run.form_line(10) == D("0.00")
    assert run.form_line(50) == D("0.00")
    assert run.get("ca-qc/tp1_credits", "ca-qc/tp1_line_391") == D("0.00")
