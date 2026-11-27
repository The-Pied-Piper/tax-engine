"""Form PE428 (2025, Prince Edward Island tax, single filer) from the salary alone: the real Prince
Edward Island manifest composed end to end.

Every PE428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real Prince Edward Island 2025
manifest, with the gross salary (`ca/employment_income`) the only input and every optional input
left blank. It asserts the Prince Edward Island tax of PE428 line 97, the CPP and EI amounts and
the take-home at salaries of $20,000, $30,000 and $70,000.

Form text (Form PE428, CRA 5002-C): line 97 "Line 97: Line 93 minus line 96 (if negative, enter
"0") Enter this amount on line 42800 of your return. Prince Edward Island tax =".

The line 97 figures are 33.83 / 1,261.72 / 6,355.92. Each is derived apart from the engine in
`test_line_97_follows_from_the_printed_figures`, from the printed form alone: the column of lines 2
to 8 that the taxable income falls in (printed rate and constant), the credits base (line 9, the
basic personal amount $14,650, plus the CPP and EI amounts) at the printed 9.5%, and the low-income
tax reduction of lines 66 to 88 ($350 less 5% of the adjusted family income above $22,650). The
taxable income is the salary less the CPP enhanced contribution (1% of the salary over $3,500). The
figures are not a CRA example.

The take-home is the salary less income tax (T1 line 43500), EI, CPP and CPP2; the federal part of
T1 line 43500 is the figure of the federal chain (pinned by the federal tests; not re-derived
here), and the take-home totals below are worked from it: 20,000 less (158.09 + 33.83), 328.00 and
981.75 is 18,498.33; 30,000 less (1,498.04 + 1,261.72), 492.00 and 1,576.75 is 25,171.49; 70,000
less (7,585.64 + 6,355.92), 1,077.48 and 3,956.75 is 51,024.21.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
PRINCE_EDWARD_ISLAND = JurisdictionCode("CA-PE")
PE428 = "ca-pe/pe428"
T1 = "ca/t1_tax_and_credits"
LINE_1 = "ca-pe/pe428_taxable_income_line_1"
LINE_8 = "ca-pe/pe428_tax_on_taxable_income_line_8"
LINE_87 = "ca-pe/pe428_low_income_tax_reduction_line_87"
LINE_97 = "ca-pe/pe428_prince_edward_island_tax_line_97"
CPP_BASE = ("ca/schedule_8", "ca/schedule_8_cpp_base_contributions_on_return")
CPP_ENHANCED = ("ca/schedule_8", "ca/cpp_part_3_line_12")
CPP2 = ("ca/schedule_8", "ca/cpp_part_3_line_22")
EI = ("ca/t2204", "ca/t2204_line_16")
TOTAL_PAYABLE = (T1, "ca/total_payable")
# Salary, line 97, CPP (base plus enhanced), EI, T1 line 43500, take-home.
CASES = [
    ("20000", "33.83", "981.75", "328.00", "191.92", "18498.33"),
    ("30000", "1261.72", "1576.75", "492.00", "2759.76", "25171.49"),
    ("70000", "6355.92", "3956.75", "1077.48", "13941.56", "51024.21"),
]


def _figure(worksheets: dict[str, tuple[Worksheet, ...]], form: str, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return worksheets[form][0].get(kind).value


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        TaxCalculationRequest(PRINCE_EDWARD_ISLAND, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


@pytest.mark.parametrize(("salary", "line_97", "cpp", "ei", "payable", "take_home"), CASES)
def test_the_prince_edward_island_tax_cpp_ei_and_take_home_at_each_salary(
    salary: str, line_97: str, cpp: str, ei: str, payable: str, take_home: str
) -> None:
    worksheets = _worksheets(salary)

    assert _figure(worksheets, PE428, LINE_97) == D(line_97)
    assert _figure(worksheets, *CPP_BASE) + _figure(worksheets, *CPP_ENHANCED) == D(cpp)
    assert _figure(worksheets, *EI) == D(ei)
    assert _figure(worksheets, *TOTAL_PAYABLE) == D(payable)
    assert _figure(worksheets, *CPP2) == D("0.00")
    assert (
        D(salary)
        - _figure(worksheets, *TOTAL_PAYABLE)
        - _figure(worksheets, *EI)
        - _figure(worksheets, *CPP_BASE)
        - _figure(worksheets, *CPP_ENHANCED)
        - _figure(worksheets, *CPP2)
    ) == D(take_home)


@pytest.mark.parametrize(("salary", "line_97", "cpp", "ei", "payable", "take_home"), CASES)
def test_line_97_follows_from_the_printed_figures(
    salary: str, line_97: str, cpp: str, ei: str, payable: str, take_home: str
) -> None:
    income = D(salary)
    enhanced = _cents((income - D("3500")) * D("0.01"))
    taxable_income = income - enhanced
    # Lines 2 to 8: the column (printed lower bound, rate and constant of line 7).
    columns = [
        ("0", "0.095", "0"),
        ("33328", "0.1347", "3166.16"),
        ("64656", "0.166", "7386.04"),
        ("105000", "0.1762", "14083.15"),
        ("140000", "0.19", "20250.15"),
    ]
    lower, rate, constant = [c for c in columns if D(c[0]) < taxable_income][-1]
    line_8 = _cents((taxable_income - D(lower)) * D(rate)) + D(constant)
    # Line 9 plus the CPP base and EI amounts, at the printed 9.5%.
    base = D(cpp) - enhanced
    credits = _cents((D("14650") + base + D(ei)) * D("0.095"))
    # Lines 66 to 88: the reduction of 350 less 5% of the net income (the taxable income here) over
    # 22,650.
    over_base = max(D("0"), taxable_income - D("22650"))
    reduction = max(D("0"), D("350") - _cents(over_base * D("0.05")))
    expected = max(D("0"), line_8 - credits - reduction)

    assert expected == D(line_97)


def test_the_reduction_of_line_87_is_350_at_20000_and_gone_at_30000() -> None:
    assert _figure(_worksheets("20000"), PE428, LINE_87) == D("350.00")
    assert _figure(_worksheets("30000"), PE428, LINE_87) == D("0.00")
