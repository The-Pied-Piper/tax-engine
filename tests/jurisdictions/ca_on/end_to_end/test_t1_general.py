"""The Ontario take-home calculator end to end: the real manifest, the gross salary alone.

Every form has its own end-to-end module in this folder. This one composes the whole take-home
manifest (the real header `manifest.yaml`, the form-less `return.yaml`, `salary.yaml` and every
form's part files: Schedule 8, T2204, ca/t1_taxable_income, ON428-A, ON428, Schedule 6 and the
T1 General) and types in only the gross salary (`ca/employment_income`). It pins the T1 General
(CRA 5006-R, 2025, Ontario edition) lines the salary-only filer fills, the return's one output
(T1 line 167, refund or balance owing) and the CPP and EI figures the calculator reads from
Schedule 8 and T2204. It is not a worked return: no return file, no slips, tax withheld 0.

Oracles: the figures at $70,000 are the CRA Return DD figures traced line by line in the form
audits (`take-home/validation/`); the other salaries are checked against the same chain and, for
the payroll figures, against T4127 (121st edition). T1 line 167 is the balance owing (positive)
or the refund (negative); the take-home subtraction (salary less CPP, EI and tax) lives in the
calculator, outside the engine.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.deductions import (
    SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
)
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.net_tax import PROVINCIAL_TAX_LINE_42800
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import (
    CREDIT_AMOUNTS_LINE_84,
    CREDIT_AMOUNTS_LINE_98,
    CREDIT_AMOUNTS_LINE_106,
    FEDERAL_TAX_AFTER_CREDITS,
    NON_REFUNDABLE_TAX_CREDITS,
)
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    BASIC_PERSONAL_AMOUNT,
    CPP_BASE_CONTRIBUTIONS_LINE_86,
    CREDITS_SUBTOTAL_LINE_96,
    EI_PREMIUMS_LINE_88,
    FEDERAL_BASIC_TAX,
    FEDERAL_TAX_TAXABLE_INCOME_LINE_70,
)
from tax_engine.jurisdictions.ca.catalog.refund import (
    CWB_LINE_45300,
    EI_OVERPAYMENT_LINE_45000,
    REFUND_OR_BALANCE_OWING,
    T2204_PREMIUMS_DEDUCTED,
)
from tax_engine.jurisdictions.ca_on.catalog import (
    ON428_ONTARIO_TAX_LINE_90,
    ON428_TAX_ON_TAXABLE_INCOME_LINE_8,
    ON428_TAXABLE_INCOME_LINE_1,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
CODE = JurisdictionCode("CA-ON")
# The two files that are not parts of a form: the real header and the form-less return.
HEADER = (TAKE_HOME / "manifest.yaml").read_text(encoding="utf-8")
RETURN = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)

# T1 General lines by kind, at $70,000 (Return DD). The label is the form line the kind is.
T1_AT_70000: dict[str, tuple[AmountKind, str]] = {
    "30000": (BASIC_PERSONAL_AMOUNT, "16129.00"),
    "76": (FEDERAL_BASIC_TAX, "10771.18"),
    "84": (CREDIT_AMOUNTS_LINE_84, "16129.00"),
    "86": (CPP_BASE_CONTRIBUTIONS_LINE_86, "3291.75"),
    "88": (EI_PREMIUMS_LINE_88, "1077.48"),
    "96": (CREDITS_SUBTOTAL_LINE_96, "5840.23"),
    "98": (CREDIT_AMOUNTS_LINE_98, "21969.23"),
    "106": (CREDIT_AMOUNTS_LINE_106, "21969.23"),
    "33800": (NON_REFUNDABLE_TAX_CREDITS, "3185.54"),
    "42800": (PROVINCIAL_TAX_LINE_42800, "3911.45"),
    "42900": (FEDERAL_TAX_AFTER_CREDITS, "7585.64"),
    "45000": (EI_OVERPAYMENT_LINE_45000, "0.00"),
    "45300": (CWB_LINE_45300, "0.00"),
    "167": (REFUND_OR_BALANCE_OWING, "11497.09"),
}

# The return's line 167 and the payroll figures the calculator reads, by salary, with sources:
# (salary, line 167, federal tax after credits, Ontario tax line 90, CPP base + enhanced, EI, CWB).
# $70,000: Return DD (fed 7,585.64 + ON428 line 90 3,911.45); CPP and EI from T4127 (121st ed.),
# confirmed against the PDOC check of 7 Nov 2026. $20,000: PDOC check; the Canada workers benefit
# (1,633.00) exceeds the tax, so line 167 is a refund. $275,000: PDOC check; CPP is capped (4,034.10
# = 3,356.10 + 678.00) and CPP2 is 396.00, so the line 22215 figure is 1,074.00. $2,010: ticket
# #377 (CPP 0.00, EI 32.96, T2204 line 15 refund 22.96 of premiums not due).
ANCHORS: list[tuple[str, str, str, str, str, str, str]] = [
    ("70000", "11497.09", "7585.64", "3911.45", "3956.75", "1077.48", "0.00"),
    ("20000", "-1474.91", "158.09", "0.00", "981.75", "328.00", "1633.00"),
    ("275000", "101743.28", "62204.64", "39538.64", "4430.10", "1077.48", "0.00"),
    ("2010", "-22.96", "0.00", "0.00", "0.00", "32.96", "0.00"),
]

# Printed bracket columns: (more than, rate, line 75 / line 7 constant). A taxable income equal to
# a column's upper bound belongs to that column ("not more than"), so the edge is in the lower one.
FEDERAL_COLUMNS = (  # T1 General line 75 (CRA 5000-D1), taxable income at line 26000
    ("0", "0.145", "0.00"),
    ("57375", "0.205", "8319.38"),
    ("114750", "0.26", "20081.25"),
    ("177882", "0.29", "36495.57"),
    ("253414", "0.33", "58399.85"),
)
ONTARIO_COLUMNS = (  # ON428 Part A line 7 (CRA 5006-C)
    ("0", "0.0505", "0.00"),
    ("52886", "0.0915", "2670.74"),
    ("105775", "0.1116", "7510.09"),
    ("150000", "0.1216", "12445.60"),
    ("220000", "0.1316", "20957.60"),
)


def cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def tax_on(taxable: Decimal, columns: tuple[tuple[str, str, str], ...]) -> Decimal:
    """The form's own arithmetic: pick the column ("more than" its start); line 4 or 72 is the
    excess, line 6 or 74 the excess times the printed rate to the cent, plus the constant."""
    start, rate, constant = [c for c in columns if taxable > D(c[0]) or c[0] == "0"][-1]
    return cents((taxable - D(start)) * D(rate)) + D(constant)


def enhanced_cpp_deduction(salary: Decimal) -> Decimal:
    """T1 line 22215 for a salary alone: Schedule 8 line 12 (1% of earnings between the 3,500
    exemption and the 71,300 ceiling) and line 28 from 81,200 up (CPP2 396.00, ceiling 81,200).
    Only salaries up to 71,300 or from 81,200 are used below, so no partial CPP2 is needed."""
    assert salary <= D("71300") or salary >= D("81200")
    if salary >= D("81200"):
        return D("1074.00")
    return cents(max(salary - D("3500"), D("0")) * D("0.01"))


# A salary inside every federal and every Ontario column, and the exact edge of each column with
# the salary one cent or one dollar above. Salaries are chosen so that taxable income (line 26000 =
# salary less the line 22215 deduction) is exactly the printed bound: for example 115,824.00 less
# 1,074.00 is 114,750.00 (federal edge, the 20,081.26 case) and 53,384.85 less 498.85 is 52,886.00.
BRACKET_SALARIES = [
    "0", "30000", "53384.85", "53385.86", "57919.19", "57920.20", "70000", "115824", "115825",
    "106849", "106850", "130000", "151074", "151075", "160000", "178956", "178957", "200000",
    "221074", "221075", "240000", "254488", "254489", "275000",
]  # fmt: skip


def run(take_home_service: TakeHomeService, salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return take_home_service(HEADER, RETURN, *PARTS).compute(
        CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def sheet(worksheets: dict[str, tuple[Worksheet, ...]], form: str) -> Worksheet:
    (found,) = worksheets[form]
    return found


def test_every_t1_line_at_seventy_thousand_matches_return_dd(
    take_home_service: TakeHomeService,
) -> None:
    t1 = sheet(run(take_home_service, "70000"), "ca/t1_tax_and_credits")

    assert {line: t1.get(kind).value for line, (kind, _) in T1_AT_70000.items()} == {
        line: D(figure) for line, (_, figure) in T1_AT_70000.items()
    }


@pytest.mark.parametrize(("salary", "line_167", "federal", "ontario", "cpp", "ei", "cwb"), ANCHORS)
def test_the_return_and_its_payroll_figures(
    take_home_service: TakeHomeService,
    salary: str,
    line_167: str,
    federal: str,
    ontario: str,
    cpp: str,
    ei: str,
    cwb: str,
) -> None:
    worksheets = run(take_home_service, salary)
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    # The return's one output is T1 line 167, and line 167 is federal tax plus Ontario tax less
    # the credits the filer has (here only the Canada workers benefit and the EI overpayment).
    assert sheet(worksheets, "ca-on/return").get(REFUND_OR_BALANCE_OWING).value == D(line_167)
    assert t1.get(FEDERAL_TAX_AFTER_CREDITS).value == D(federal)
    assert t1.get(PROVINCIAL_TAX_LINE_42800).value == D(ontario)
    assert t1.get(CWB_LINE_45300).value == D(cwb)
    schedule_8 = sheet(worksheets, "ca/schedule_8")
    assert (
        schedule_8.get(SCHEDULE_8_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value
        + schedule_8.get(SCHEDULE_8_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value
    ) == D(cpp)
    assert sheet(worksheets, "ca/t2204").get(T2204_PREMIUMS_DEDUCTED).value == D(ei)


def test_line_167_adds_the_ontario_tax_once_and_never_the_health_premium_again(
    take_home_service: TakeHomeService,
) -> None:
    # ON428 line 90 already holds the Ontario health premium (line 89, 600.00 at $70,000), so
    # line 167 is exactly line 42900 plus line 42800.
    worksheets = run(take_home_service, "70000")
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")

    assert sheet(worksheets, "ca-on/on428").get(ON428_ONTARIO_TAX_LINE_90).value == D("3911.45")
    assert t1.get(REFUND_OR_BALANCE_OWING).value == (
        t1.get(FEDERAL_TAX_AFTER_CREDITS).value + t1.get(PROVINCIAL_TAX_LINE_42800).value
    )


@pytest.mark.parametrize("salary", BRACKET_SALARIES)
def test_the_bracket_lines_follow_the_printed_columns_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    # Federal line 76 and ON428 line 8 are the printed-constant arithmetic of the taxable income
    # (salary less the line 22215 deduction); line 167 is the federal tax after credits plus the
    # Ontario tax (line 90, which holds the health premium and surtax), and it has two decimals.
    worksheets = run(take_home_service, salary)
    t1 = sheet(worksheets, "ca/t1_tax_and_credits")
    on428 = sheet(worksheets, "ca-on/on428")
    taxable = D(salary) - enhanced_cpp_deduction(D(salary))

    assert t1.get(FEDERAL_TAX_TAXABLE_INCOME_LINE_70).value == taxable
    assert on428.get(ON428_TAXABLE_INCOME_LINE_1).value == taxable
    assert t1.get(FEDERAL_BASIC_TAX).value == tax_on(taxable, FEDERAL_COLUMNS)
    assert on428.get(ON428_TAX_ON_TAXABLE_INCOME_LINE_8).value == tax_on(taxable, ONTARIO_COLUMNS)
    line_167 = sheet(worksheets, "ca-on/return").get(REFUND_OR_BALANCE_OWING).value
    assert (
        line_167
        == t1.get(FEDERAL_TAX_AFTER_CREDITS).value
        + on428.get(ON428_ONTARIO_TAX_LINE_90).value
        - t1.get(CWB_LINE_45300).value
        - t1.get(EI_OVERPAYMENT_LINE_45000).value
    )
    assert line_167.as_tuple().exponent == -2


def test_the_federal_edge_at_114750_belongs_to_the_lower_column(
    take_home_service: TakeHomeService,
) -> None:
    # T1 line 75 prints "more than 57,375 but not more than 114,750": the lower column applies at
    # exactly 114,750, so line 74 is 20.5% of 57,375.00 = 11,761.875 -> 11,761.88 and line 76 is
    # 8,319.38 + 11,761.88 = 20,081.26 (the next column's constant is 20,081.25).
    t1 = sheet(run(take_home_service, "115824"), "ca/t1_tax_and_credits")

    assert t1.get(FEDERAL_BASIC_TAX).value == D("20081.26")


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        run(take_home_service, "-1")
