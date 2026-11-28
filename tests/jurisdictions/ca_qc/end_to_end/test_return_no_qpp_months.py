"""The Quebec return charges no QPP to a filer with no QPP months.

TP-1 lines 98, 98.1 and 98.2 (the slip figures a salary-only caller leaves blank) are computed on
Schedule 8 lines 7, 2 and 4, which hold the months of line A. A filer under 18 all year has no QPP
months, so those lines, Schedule U and the deduction of TP-1 line 248 are all 0; a full-year filer
keeps the figures of the printed rates, and a part-year filer (months typed in) is prorated. The
tests run the real engine over the whole Quebec return; the expected figures are hand-computed from
the printed rates (6.40% of the earnings above $3,500 to $71,300, 4% from $71,300 to $81,200).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_MONTHS
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.kinds import bundled_kinds

D = Decimal
QUEBEC = JurisdictionCode("CA-QC")
# (form, kind) of the figures under test.
LINE_98 = ("ca-qc/tp1_income", "ca-qc/tp1_qpp_contribution_line_98")
LINE_98_1 = ("ca-qc/tp1_income", "ca-qc/tp1_pensionable_salary_line_98_1")
LINE_98_2 = ("ca-qc/tp1_income", "ca-qc/tp1_additional_qpp_contribution_line_98_2")
LINE_248 = ("ca-qc/tp1_net_income", "ca-qc/tp1_qpp_deduction_line_248")


def figure(
    year: int,
    salary: str,
    where: tuple[str, str],
    birth_year: int | None = None,
    months: int | None = None,
) -> Decimal:
    given: list[Artifact[Decimal] | Artifact[int]] = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    if months is not None:
        given.append(Artifact(CPP_MONTHS, months))
    worksheets = build_tax_computation().compute(TaxCalculationRequest(QUEBEC, year, tuple(given)))
    value = worksheets[where[0]][0].get(bundled_kinds().kind(where[1])).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("where", [LINE_98, LINE_98_1, LINE_98_2, LINE_248])
@pytest.mark.parametrize("salary", ["3000", "25000", "75000", "100000"])
@pytest.mark.parametrize(("year", "birth_year"), [(2025, 2009), (2026, 2010)])
def test_a_filer_under_18_all_year_has_no_qpp_lines(
    year: int, birth_year: int, salary: str, where: tuple[str, str]
) -> None:
    assert figure(year, salary, where, birth_year) == D("0")


@pytest.mark.parametrize(
    ("where", "expected"),
    [(LINE_98, "4339.20"), (LINE_98_1, "75000.00"), (LINE_98_2, "148.00")],
)
def test_a_full_year_filer_keeps_the_printed_rates(where: tuple[str, str], expected: str) -> None:
    assert figure(2025, "75000", where, 1980) == D(expected)


def test_a_filer_without_a_birth_year_is_a_full_year_filer() -> None:
    assert figure(2025, "75000", LINE_98) == D("4339.20")


def test_the_deduction_of_line_248_is_not_zero_for_a_full_year_filer() -> None:
    assert figure(2025, "75000", LINE_248) > D("0")


@pytest.mark.parametrize(
    ("where", "expected"),
    # Six months: line B 35,650.00, line D 40,600.00, line E 1,750.00.
    # Line 98: 6.40% of (35,650 - 1,750); line 98.1: 40,600; line 98.2: 4% of (40,600 - 35,650).
    [(LINE_98, "2169.60"), (LINE_98_1, "40600.00"), (LINE_98_2, "198.00")],
)
def test_a_part_year_filer_is_prorated_by_the_months(where: tuple[str, str], expected: str) -> None:
    assert figure(2025, "75000", where, 1980, months=6) == D(expected)
