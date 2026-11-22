"""SK428 (2025) lines 43 to 57 and 75 to 82, the medical expenses, donations and venture capital
blocks, through the real registered engine from a salary.

Form text (Form SK428, CRA 5008-c-25e.txt): line 43 "Amount from line 33099 of your return", line 44
"Amount from line 23600 of your return", line 45 "Applicable rate 3%", line 46 "Line 44 multiplied
by the percentage from line 45 =", line 47 "Enter whichever is less: $2,681 or the amount on line
46.", line 48 "Line 43 minus line 47 (if negative, enter "0") =", line 49 "Allowable amount of
medical expenses for other dependants from line 33199 of your return", line 50 "Line 48 plus line
49 =", line 54 "Amount from line 13 of your federal Schedule 9 multiplied by 10.5% =", line 55
"Amount from line 14 of your federal Schedule 9 multiplied by 14.5% =", line 56 "Line 54 plus line
55 =" and line 77 "Line 75 plus line 76 (maximum $875) =". The medical amounts of lines 43 and 49,
the Schedule 9 amounts of lines 54 and 55 and the T2C slip amounts of lines 75 and 76 are the
caller's optional inputs; every other line is computed.

The figures are derived by hand below with Decimal, not read from the engine (not a CRA example).
A $70,000 salary has net income 69,335.00, so line 46 is 3% of it, 2,080.05, under the 2,681 limit
of line 47.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
SASKATCHEWAN = JurisdictionCode("CA-SK")
SK428 = "ca-sk/sk428"
SK428_CREDITS = "ca-sk/sk428_credits"
LINE_50 = "ca-sk/sk428_medical_expenses_line_50"
LINE_56 = "ca-sk/sk428_donations_credit_line_56"
LINE_57 = "ca-sk/sk428_non_refundable_credits_line_57"
LINE_77 = "ca-sk/sk428_labour_sponsored_credit_checked_line_77"
LINE_82 = "ca-sk/sk428_saskatchewan_tax_line_82"
INPUTS = {
    "line_43": "ca-sk/sk428_medical_expenses_line_43",
    "line_49": "ca-sk/sk428_other_dependants_medical_expenses_line_49",
    "line_12": "ca/donations_and_gifts_line_12",
    "line_75": "ca-sk/sk428_venture_capital_credit_saskatchewan_line_75",
    "line_76": "ca-sk/sk428_venture_capital_credit_federal_line_76",
}
# The salary-only Saskatchewan tax at $70,000 before this change (test_sk428.py pins it too).
SALARY_ONLY_TAX = D("5092.30")
# Line 51 of a salary-only caller at $70,000: the basic personal amount, the CPP and the EI amounts.
LINE_42 = D("19491") + D("3291.75") + D("1077.48")
LINE_57_SALARY_ONLY = D("2505.32")
NET_INCOME = D("69335.00")


def _kind(name: str) -> AmountKind:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return kind


def _sheets(salary: str, **given: str) -> tuple[Worksheet, Worksheet]:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(_kind(INPUTS[name]), D(value)) for name, value in given.items()]
    worksheets = build_tax_computation().compute(SASKATCHEWAN, 2025, *artifacts)
    (credits_sheet,) = worksheets[SK428_CREDITS]
    (sk428,) = worksheets[SK428]
    return credits_sheet, sk428


def _value(sheet: Worksheet, name: str) -> Decimal:
    value = sheet.get(_kind(name)).value
    assert isinstance(value, Decimal)
    return value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


@pytest.mark.parametrize("name", [LINE_50, LINE_56, LINE_57, LINE_77, LINE_82])
def test_a_salary_only_caller_has_no_claim_on_the_three_lines(name: str) -> None:
    credits_sheet, sk428 = _sheets("70000")
    expected = {LINE_57: LINE_57_SALARY_ONLY, LINE_82: SALARY_ONLY_TAX}.get(name, D("0.00"))

    assert _value(sk428 if name in (LINE_77, LINE_82) else credits_sheet, name) == expected


def test_a_medical_donations_and_venture_capital_return_at_70000() -> None:
    credits_sheet, sk428 = _sheets(
        "70000",
        line_43="5000",
        line_49="250.50",
        line_12="2200",
        line_75="400.00",
        line_76="300.00",
    )

    # Line 50: line 48 (5,000.00 less the 2,080.05 of line 47) plus 250.50 of line 49.
    line_47 = min(_cents(NET_INCOME * D("0.03")), D("2681"))
    line_50 = max(D("5000") - line_47, D(0)) + D("250.50")
    assert line_47 == D("2080.05")
    assert line_50 == D("3170.45")
    # Line 12 is 2,200: line 13 is the printed 200 and line 14 is 2,000. Line 56: 200 at 10.5% plus
    # 2,000 at 14.5%.
    line_56 = _cents(D("200") * D("0.105")) + _cents(D("2000") * D("0.145"))
    assert line_56 == D("311.00")
    # Line 57: line 53 (line 51 at 10.5%) plus line 56.
    line_57 = _cents((LINE_42 + line_50) * D("0.105")) + line_56
    assert line_57 == D("3149.22")
    # Line 77: 400.00 plus 300.00, under the 875 maximum. Tax: 7,597.62 less line 66 (line 57,
    # no line 64 or 65) less line 77.
    line_77 = D("400.00") + D("300.00")
    tax = D("7597.62") - line_57 - line_77
    assert tax == D("3748.40")

    assert _value(credits_sheet, LINE_50) == line_50
    assert _value(credits_sheet, LINE_56) == line_56
    assert _value(credits_sheet, LINE_57) == line_57
    assert _value(sk428, LINE_77) == line_77
    assert _value(sk428, LINE_82) == tax
    assert tax != SALARY_ONLY_TAX
