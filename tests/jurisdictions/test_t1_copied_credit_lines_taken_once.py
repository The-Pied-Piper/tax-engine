"""T1 (5006-R, 2025) lines 87, 102, 107 to 112 and 124, the lines the T1 copies from the T1
lines copied by provinces form, through the real engine from a salary.

Form text (T1 General 5006-R, CRA 5006-R-25E.txt, Step 5 Part B and Part C): "Line 87 and line
31000: on self-employment income and other earnings", "Line 96: Add lines 86 to 95.", "Line 102 and
line 31900: Interest paid on your student loans", "Line 106: Add lines 101 to 105.", "Line 107 and
line 33099: Medical expenses for self, spouse or common-law partner and your dependent children
under 18 years of age", "Line 108: Amount from line 23600 multiplied by 3%", "Line 109: Enter
whichever is less: $2,834 or the amount from line 108.", "Line 110: Line 107 minus line 109 (if
negative, enter "0")", "Line 111 and line 33199: Allowable amount of medical expenses for other
dependants (use Federal Worksheet)", "Line 112 and line 33200: Line 110 plus line 111", "Line 113
and line 33500: Line 106 plus line 112", "Line 124 and line 40427: Minimum tax carryover (complete
Form T691)" and "Line 125: Add lines 122 to 124."

The five inputs are the caller's optional inputs (the T1 lines copied by provinces form owns them);
every other line is computed. The hand figures are asserted (not a CRA example). A $70,000 salary
has net income 69,335.00, so line 108 is 2,080.05 (under the 2,834 ceiling) and line 33500 without
the five lines is 21,969.23 (16,129.00 + 5,840.23). With line 31000 of 500.00, line 31900 of
300.00, line 33099 of 5,000.00 and line 40427 of 200.00: line 96 is 5,840.23 + 500.00 = 6,340.23,
line 106 is 21,969.23 + 500.00 + 300.00 = 22,769.23, line 110 is 5,000.00 - 2,080.05 = 2,919.95,
line 33500 is 22,769.23 + 2,919.95 = 25,689.18, line 33800 and line 35000 are 14.5% of it,
3,724.93, and line 125 is 3,724.93 + 200.00 = 3,924.93."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.credits_against_federal_tax import MINIMUM_TAX_CARRYOVER
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.non_refundable_credits import (
    SELF_EMPLOYMENT_CPP_QPP_CONTRIBUTIONS,
    STUDENT_LOAN_INTEREST,
)
from tax_engine.jurisdictions.ca.catalog.personal_amounts import (
    MEDICAL_EXPENSES,
    OTHER_DEPENDANTS_MEDICAL_EXPENSES,
)
from tests.kinds import bundled_kinds

D = Decimal
FORM = "ca/t1_tax_and_credits"
PROVINCES = ["CA-ON", "CA-AB", "CA-BC", "CA-MB", "CA-NB", "CA-NL", "CA-PE", "CA-SK"]


def _t1(province: str, salary: str, **given: str) -> Worksheet:
    inputs = {
        "line_31000": SELF_EMPLOYMENT_CPP_QPP_CONTRIBUTIONS,
        "line_31900": STUDENT_LOAN_INTEREST,
        "line_33099": MEDICAL_EXPENSES,
        "line_33199": OTHER_DEPENDANTS_MEDICAL_EXPENSES,
        "line_40427": MINIMUM_TAX_CARRYOVER,
    }
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    artifacts += [Artifact(inputs[name], D(value)) for name, value in given.items()]
    worksheets = build_tax_computation().compute(
        TaxCalculationRequest(JurisdictionCode(province), 2025, tuple(artifacts))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    value = sheet.get(bundled_kinds().kind(identifier)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("province", PROVINCES)
def test_a_salary_only_caller_has_no_change_to_the_federal_credits(province: str) -> None:
    sheet = _t1(province, "70000")

    assert _value(sheet, "ca/cpp_base_contributions_line_87") == D("0.00")
    assert _value(sheet, "ca/credits_subtotal_line_96") == D("5840.23")
    assert _value(sheet, "ca/student_loan_interest_line_102") == D("0.00")
    assert _value(sheet, "ca/credit_amounts_line_106") == D("21969.23")
    assert _value(sheet, "ca/medical_net_income_share") == D("2080.05")
    assert _value(sheet, "ca/medical_threshold") == D("2080.05")
    assert _value(sheet, "ca/other_dependants_medical_expenses_line_111") == D("0.00")
    assert _value(sheet, "ca/medical_claim") == D("0.00")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("21969.23")
    assert _value(sheet, "ca/non_refundable_tax_credits") == D("3185.54")
    assert _value(sheet, "ca/credits_against_basic_federal_tax") == D("3185.54")


@pytest.mark.parametrize("province", PROVINCES)
def test_the_four_lines_reach_the_federal_sums(province: str) -> None:
    sheet = _t1(
        province,
        "70000",
        line_31000="500",
        line_31900="300",
        line_33099="5000",
        line_40427="200",
    )

    assert _value(sheet, "ca/cpp_base_contributions_line_87") == D("500.00")
    assert _value(sheet, "ca/credits_subtotal_line_96") == D("6340.23")
    assert _value(sheet, "ca/student_loan_interest_line_102") == D("300.00")
    assert _value(sheet, "ca/credit_amounts_line_106") == D("22769.23")
    assert _value(sheet, "ca/medical_expenses_line_107") == D("5000.00")
    assert _value(sheet, "ca/medical_expenses_over_threshold") == D("2919.95")
    assert _value(sheet, "ca/medical_claim") == D("2919.95")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("25689.18")
    assert _value(sheet, "ca/non_refundable_tax_credits") == D("3724.93")
    assert _value(sheet, "ca/minimum_tax_carryover_line_124") == D("200.00")
    assert _value(sheet, "ca/credits_against_basic_federal_tax") == D("3924.93")


@pytest.mark.parametrize("province", PROVINCES)
def test_line_33199_reaches_line_111_and_line_112(province: str) -> None:
    # $70,000: line 110 is 2,919.95 with 5,000.00 on line 33099; line 111 is the 800.00 typed on
    # line 33199, so line 112 is 2,919.95 + 800.00 = 3,719.95 and line 33500 is
    # 21,969.23 + 3,719.95 = 25,689.18.
    sheet = _t1(province, "70000", line_33099="5000", line_33199="800")

    assert _value(sheet, "ca/medical_expenses_over_threshold") == D("2919.95")
    assert _value(sheet, "ca/other_dependants_medical_expenses_line_111") == D("800.00")
    assert _value(sheet, "ca/medical_claim") == D("3719.95")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("25689.18")


def test_the_medical_threshold_is_the_printed_ceiling_when_three_percent_is_more() -> None:
    # $150,000: net income 148,926.00, 3% is 4,467.78, above the 2,834 ceiling.
    sheet = _t1("CA-ON", "150000", line_33099="9000")

    assert _value(sheet, "ca/medical_net_income_share") == D("4467.78")
    assert _value(sheet, "ca/medical_threshold") == D("2834.00")
    assert _value(sheet, "ca/medical_expenses_over_threshold") == D("6166.00")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("28199.58")


def test_medical_expenses_below_the_threshold_give_nothing() -> None:
    # $70,000: threshold 2,080.05; expenses of 1,000.00 are under it, line 110 floors at 0.
    sheet = _t1("CA-ON", "70000", line_33099="1000")

    assert _value(sheet, "ca/medical_expenses_over_threshold") == D("0.00")
    assert _value(sheet, "ca/non_refundable_credit_amounts") == D("21969.23")


def test_the_minimum_tax_carryover_lowers_the_basic_federal_tax() -> None:
    # $70,000: line 126 is 7,585.64 without the carryover; 200.00 lowers it to 7,385.64.
    without = _t1("CA-ON", "70000")
    with_carryover = _t1("CA-ON", "70000", line_40427="200")

    assert _value(without, "ca/federal_tax_after_credits") == D("7585.64")
    assert _value(with_carryover, "ca/federal_tax_after_credits") == D("7385.64")
