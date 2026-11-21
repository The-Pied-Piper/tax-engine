"""ON428 (2025) lines 36 to 43 and 47 to 49, the medical expenses and donations blocks, through the
real engine from a salary.

Form text (Form ON428, CRA 5006-c-25e.txt): line 37 "Amount from line 23600 of your return", line 38
"Applicable rate 3%", line 39 "Line 37 multiplied by the percentage from line 38 =", line 40 "Enter
whichever is less: $2,885 or the amount on line 39.", line 41 "Line 36 minus line 40 (if negative,
enter "0") =", line 43 "Line 41 plus line 42 =", line 47 "Amount from line 13 of your federal
Schedule 9 multiplied by 5.05% =", line 48 "Amount from line 14 of your federal Schedule 9
multiplied by 11.16% =" and line 49 "Line 47 plus line 48 =". Lines 36, 42 and the two Schedule 9
amounts are the caller's optional inputs; every other line is computed.

The hand figures are asserted (not a CRA example). A $70,000 salary has net income 69,335.00 (the
salary less the enhanced CPP deduction), so line 39 is 3% of it, 2,080.05, under the 2,885 cap.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on import catalog as on

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")


def _on428(salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_36": on.ON428_MEDICAL_EXPENSES_LINE_36,
        "line_42": on.ON428_OTHER_DEPENDANTS_MEDICAL_EXPENSES_LINE_42,
        "line_47": on.ON428_DONATIONS_AMOUNT_LINE_47,
        "line_48": on.ON428_DONATIONS_AMOUNT_LINE_48,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(ONTARIO, 2025, *artifacts)["ca-on/on428"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_medical_or_donations_claim() -> None:
    sheet = _on428("70000")

    assert _value(sheet, on.ON428_NET_INCOME_LINE_37) == D("69335.00")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_39) == D("2080.05")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_40) == D("2080.05")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41) == D("0.00")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_LINE_43) == D("0.00")
    assert _value(sheet, on.ON428_DONATIONS_CREDIT_LINE_49) == D("0.00")
    assert _value(sheet, on.ON428_NON_REFUNDABLE_CREDITS_LINE_50) == D("864.37")


def test_a_medical_claim_above_the_three_percent_threshold_adds_to_line_43() -> None:
    sheet = _on428("70000", line_36="5000", line_42="250.50")

    # Line 41 is 5,000.00 less 2,080.05; line 43 adds the 250.50 of line 42.
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41) == D("2919.95")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_LINE_43) == D("3170.45")
    # Line 44 is line 35 (17,116.23) plus line 43; line 46 is 5.05% of it, 1,024.48.
    assert _value(sheet, on.ON428_TOTAL_CREDIT_AMOUNTS_LINE_44) == D("20286.68")
    assert _value(sheet, on.ON428_NON_REFUNDABLE_CREDITS_LINE_50) == D("1024.48")


def test_a_claim_below_the_threshold_is_not_negative() -> None:
    sheet = _on428("70000", line_36="1000")

    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41) == D("0.00")


def test_line_40_stops_at_the_2885_cap() -> None:
    # A $150,000 salary: 3% of its net income is above 2,885.
    sheet = _on428("150000", line_36="4000")

    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_39) > D("2885")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_40) == D("2885.00")
    assert _value(sheet, on.ON428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_41) == D("1115.00")


def test_a_donations_claim_is_each_schedule_9_amount_at_its_own_rate() -> None:
    sheet = _on428("70000", line_47="200", line_48="1000")

    assert _value(sheet, on.ON428_DONATIONS_CREDIT_AT_RATE_LINE_47) == D("10.10")
    assert _value(sheet, on.ON428_DONATIONS_CREDIT_AT_RATE_LINE_48) == D("111.60")
    assert _value(sheet, on.ON428_DONATIONS_CREDIT_LINE_49) == D("121.70")
    # Line 50 is 5.05% of line 44 (864.37) plus line 49.
    assert _value(sheet, on.ON428_NON_REFUNDABLE_CREDITS_LINE_50) == D("986.07")
