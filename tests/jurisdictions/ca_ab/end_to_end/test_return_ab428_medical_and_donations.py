"""AB428 (2025) lines 44 to 51 and 55 to 57, the medical expenses and donations blocks, through
the real engine from a salary.

Form text (Form AB428, CRA 5009-c-25e.txt): line 45 "Amount from line 23600 of your return", line
46 "Applicable rate 3%", line 47 "Line 45 multiplied by the percentage from line 46 =", line 48
"Enter whichever is less: $2,884 or the amount from line 47.", line 49 "Line 44 minus line 48 (if
negative, enter "0") =", line 51 "Line 49 plus line 50 =", line 55 "Amount from line 13 of your
federal Schedule 9 multiplied by 60% =", line 56 "Amount from line 14 of your federal Schedule 9
multiplied by 21% =" and line 57 "Line 55 plus line 56 =". Lines 44, 50 and Schedule 9 line 12
are the caller's optional inputs; every other line is computed.

The hand figures are asserted (not a CRA example). A $70,000 salary has net income 69,335.00 (the
salary less the enhanced CPP deduction), so line 47 is 3% of it, 2,080.05, under the 2,884 ceiling.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import DONATIONS_AND_GIFTS_LINE_12
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab import catalog as ab

D = Decimal
ALBERTA = JurisdictionCode("CA-AB")


def _ab428(salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_44": ab.AB428_MEDICAL_EXPENSES_LINE_44,
        "line_50": ab.AB428_ALLOWABLE_MEDICAL_EXPENSES_FOR_OTHER_DEPENDANTS_LINE_50,
        "line_12": DONATIONS_AND_GIFTS_LINE_12,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    (sheet,) = build_tax_computation().compute(ALBERTA, 2025, *artifacts)["ca-ab/ab428_credits"]
    return sheet


def _value(sheet: Worksheet, kind: AmountKind) -> Decimal:
    value = sheet.get(kind).value
    assert isinstance(value, Decimal)
    return value


def test_a_salary_only_caller_has_no_medical_or_donations_claim() -> None:
    sheet = _ab428("70000")

    assert _value(sheet, ab.AB428_NET_INCOME_LINE_45) == D("69335.00")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_47) == D("2080.05")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_48) == D("2080.05")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_49) == D("0.00")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_LINE_51) == D("0.00")
    assert _value(sheet, ab.AB428_DONATIONS_CREDIT_LINE_57) == D("0.00")
    assert _value(sheet, ab.AB428_CREDITS_TOTAL_LINE_52) == D("26692.23")
    assert _value(sheet, ab.AB428_NON_REFUNDABLE_CREDITS_LINE_58) == D("2135.38")


def test_a_medical_claim_above_the_three_percent_threshold_adds_to_line_51() -> None:
    sheet = _ab428("70000", line_44="5000", line_50="250.50")

    # Line 49 is 5,000.00 less 2,080.05; line 51 adds the 250.50 of line 50.
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_49) == D("2919.95")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_LINE_51) == D("3170.45")
    # Line 52 is line 43 (26,692.23) plus line 51; line 54 is 8% of it, 2,389.01.
    assert _value(sheet, ab.AB428_CREDITS_TOTAL_LINE_52) == D("29862.68")
    assert _value(sheet, ab.AB428_CREDITS_AT_RATE_LINE_54) == D("2389.01")


def test_a_claim_below_the_threshold_is_not_negative() -> None:
    sheet = _ab428("70000", line_44="1000")

    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_49) == D("0.00")


def test_line_48_stops_at_the_2884_ceiling() -> None:
    # A $150,000 salary: 3% of its net income is above 2,884.
    sheet = _ab428("150000", line_44="4000")

    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_RATE_AMOUNT_LINE_47) > D("2884")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_LIMITED_AMOUNT_LINE_48) == D("2884.00")
    assert _value(sheet, ab.AB428_MEDICAL_EXPENSES_OVER_LIMIT_LINE_49) == D("1116.00")


def test_a_donations_claim_is_each_schedule_9_amount_at_its_own_rate() -> None:
    sheet = _ab428("70000", line_12="1200")

    assert _value(sheet, ab.AB428_DONATIONS_CREDIT_AT_FIRST_RATE_LINE_55) == D("120.00")
    assert _value(sheet, ab.AB428_DONATIONS_CREDIT_AT_SECOND_RATE_LINE_56) == D("210.00")
    assert _value(sheet, ab.AB428_DONATIONS_CREDIT_LINE_57) == D("330.00")
    # Line 58 is line 54 (2,135.38) plus line 57.
    assert _value(sheet, ab.AB428_NON_REFUNDABLE_CREDITS_LINE_58) == D("2465.38")
