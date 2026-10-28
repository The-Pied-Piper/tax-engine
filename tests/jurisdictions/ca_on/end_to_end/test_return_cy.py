"""CA-ON 2025 end to end: return cy."""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.capabilities.lesser_of import LesserOf
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_DEDUCTIONS_TOTAL,
    CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED,
    CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED,
    CLERGY_QUALIFYING_EMPLOYMENT_INCOME,
    CLERGY_RESIDENCE_DEDUCTION,
    CLERGY_RESIDENCE_LINE_2,
    CLERGY_RESIDENCE_LINE_4,
    CLERGY_RESIDENCE_LINE_5,
    CLERGY_RESIDENCE_LINE_8,
    CLERGY_RESIDENCE_LINE_9,
    CLERGY_RESIDENCE_LINE_10,
    CLERGY_RESIDENCE_MONTHS_AMOUNT,
    CLERGY_RESIDENCE_PART_B_COMPLETED,
    CLERGY_RESIDENCE_TOTAL,
    CLERGY_RESIDENCE_TOTAL_LIMITED,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
    NET_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_cy(employment: str = "45000", **overrides: Any) -> Worksheet:
    """Return CY's inputs, as in `returns/2025_return_cy.yaml`, over the keyword overrides given.

    A clergy member with employment income of 45000 (the qualifying employment of Form T1223 line
    1) for 12 months, rent and utilities of 14000, nothing claimed by anyone else for the
    accommodation, so Part C (B) is completed (its months and rent say so) and the deduction is
    14000 and not limited by line 1.
    """
    inputs: dict[str, Any] = {
        "clergy_qualifying_employment_income": "45000",
        "clergy_months_in_qualifying_employment": 12,
        "clergy_accommodation_cost": "14000",
    }
    inputs.update(overrides)
    return compute(employment, (), "0", "0", "0", "0", "0", **inputs)


def test_line_2_is_a_third_of_line_1_and_line_4_is_the_months_amount_capped_at_10000() -> None:
    worksheet = return_cy()

    assert worksheet.get(CLERGY_RESIDENCE_LINE_2).value == D("15000.00")
    # Line 4 "Line 3 multiplied by $1,000 (maximum $10,000)": 12 months is 12000, capped.
    assert worksheet.get(CLERGY_RESIDENCE_MONTHS_AMOUNT).value == D("12000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_4).value == D("10000.00")
    # Line 5 "Enter whichever is more: line 2 or line 4."
    assert worksheet.get(CLERGY_RESIDENCE_LINE_5).value == D("15000.00")


def test_lines_8_to_10_and_line_23100_are_14000() -> None:
    worksheet = return_cy()

    # Line 8 "Line 6 minus line 7 =": 14000 less nothing.
    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("14000.00")
    # Line 9 "Enter whichever is less: Line 5 or line 8.": 14000, not the 15000 of line 5.
    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("14000.00")
    # Line 10 "Enter whichever is less: Line 1 or line 9.": 14000, not the 45000 of line 1.
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("14000.00")
    # (A) plus (B) is 14000 and is not more than line 1, so line 23100 is 14000.
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL).value == D("14000.00")
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL_LIMITED).value == D("14000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("14000.00")


def test_line_23300_takes_the_deduction_and_net_income_is_below_the_employment_income() -> None:
    worksheet = return_cy()

    # Line 23300 is the 14000 of line 23100 plus the enhanced CPP of 415.00 (line 22200).
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("14415.00")
    assert worksheet.get(NET_INCOME).value == D("30585.00")


def test_the_refundable_medical_expense_supplement_and_the_amt_read_the_computed_line() -> None:
    worksheet = return_cy()

    # Federal Worksheet "Line 45200": the employment income less lines 20700, 21200, 22900 and
    # 23100 (14000 here), read from the computed line 23100.
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS).value == D("14000")
    assert worksheet.get(AMT_DEDUCTIONS_TOTAL).value == D("14415.00")


def test_with_the_employers_residence_alone_line_23100_is_the_benefit() -> None:
    # (A) alone: the residence was provided by the employer, so (B) is not completed and the
    # deduction is the T4 box 30 value of 9000.
    # The benefit is reported on line 10400, so it is at most `ca/other_employment_income` (9000);
    # the 45000 of employment is split between lines 10100 and 10400 so that the total is unchanged.
    worksheet = return_cy(
        employment="36000",
        clergy_employer_residence_benefit="9000",
        other_employment_income="9000",
        clergy_qualifying_employment_income="0",
        clergy_months_in_qualifying_employment=0,
        clergy_accommodation_cost="0",
    )

    assert worksheet.get(CLERGY_RESIDENCE_PART_B_COMPLETED).value == 0
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL).value == D("9000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("9000.00")


def test_return_y_style_with_part_c_b_filled_is_limited_to_line_1() -> None:
    # Employment income of 100000, line 1 of 15000 (qualifying employment) and 6 months, rent of
    # 12000 and an employer benefit (A) of 12000. Form T1223 Part C (B), by line:
    #   line 2  "Amount from line 1 multiplied by 1/3"                  15000 / 3 = 5000
    #   line 4  "Line 3 multiplied by $1,000 (maximum $10,000)"         6 x 1000 = 6000
    #   line 5  "Enter whichever is more: line 2 or line 4."            6000
    #   line 8  "Line 6 minus line 7 ="                                 12000 - 0 = 12000
    #   line 9  "Enter whichever is less: Line 5 or line 8."            6000
    #   line 10 "Enter whichever is less: Line 1 or line 9."            6000
    # (C): (A) plus (B) is 12000 + 6000 = 18000, more than line 1, so line 23100 is 15000.
    worksheet = return_cy(
        employment="100000",
        other_employment_income="12000",
        clergy_qualifying_employment_income="15000",
        clergy_months_in_qualifying_employment=6,
        clergy_accommodation_cost="12000",
        clergy_employer_residence_benefit="12000",
    )

    assert worksheet.get(CLERGY_RESIDENCE_PART_B_COMPLETED).value == 1
    assert worksheet.get(CLERGY_RESIDENCE_LINE_2).value == D("5000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_4).value == D("6000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_5).value == D("6000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("12000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("6000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("6000.00")
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL).value == D("18000.00")
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL_LIMITED).value == D("15000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("15000.00")


def test_a_only_with_line_1_of_10000_is_not_limited_by_line_1() -> None:
    # Line 1 of 10000 and the employer's residence benefit (A) of 12000, with no (B) figures: the
    # form says "do not complete (B)", so the count is 0 and line 23100 is the 12000 of (A). The
    # total limited to line 1 (10000) is not the deduction.
    worksheet = return_cy(
        employment="100000",
        other_employment_income="12000",
        clergy_qualifying_employment_income="10000",
        clergy_months_in_qualifying_employment=0,
        clergy_accommodation_cost="0",
        clergy_employer_residence_benefit="12000",
    )

    assert worksheet.get(CLERGY_RESIDENCE_PART_B_COMPLETED).value == 0
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL).value == D("12000.00")
    assert worksheet.get(CLERGY_RESIDENCE_TOTAL_LIMITED).value == D("10000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("12000.00")


def test_a_spouses_claim_on_line_7_comes_off_the_accommodation() -> None:
    # Line 7 of 5000 with line 6 of 14000: line 8 is 9000, line 9 is the lesser of line 5 (15000)
    # and line 8, so 9000, and line 10 is the lesser of line 1 (45000) and line 9, so 9000.
    worksheet = return_cy(clergy_other_accommodation_claims="5000")

    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("9000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("9000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("9000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("9000.00")


def test_with_b_completed_line_10_is_not_more_than_line_1() -> None:
    # Line 1 of 8000 (and employment income of 8000): line 9 is 10000 here, so line 10 is the 8000
    # of line 1, and line 23100 is not more than line 1.
    worksheet = return_cy(employment="8000", clergy_qualifying_employment_income="8000")

    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("10000.00")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("8000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("8000.00")


def test_line_10_is_the_lesser_of_line_1_and_line_9_when_line_9_is_14000() -> None:
    # Line 1 of 8000 and line 9 of 14000 (the form's cap, not a figure this return can reach):
    # line 10 "Enter whichever is less: Line 1 or line 9." is 8000.
    capability = LesserOf(
        (CLERGY_QUALIFYING_EMPLOYMENT_INCOME, CLERGY_RESIDENCE_LINE_9),
        CLERGY_RESIDENCE_LINE_10,
    )

    result = capability.compute(
        (
            Artifact(CLERGY_QUALIFYING_EMPLOYMENT_INCOME, D("8000")),
            Artifact(CLERGY_RESIDENCE_LINE_9, D("14000")),
        )
    )

    assert result.outputs == (Artifact(CLERGY_RESIDENCE_LINE_10, D("8000")),)


def test_an_employer_residence_benefit_above_line_10400_is_refused_not_capped() -> None:
    # The T4 box 30 value is reported on line 10400, so a benefit of 10400.01 against line 10400 of
    # 10400.00 is refused, not capped to 10400.
    message = (
        "ca/clergy_employer_residence_benefit 10400.01 is above ca/other_employment_income 10400"
    )

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_cy(clergy_employer_residence_benefit="10400.01", other_employment_income="10400")


def test_an_employer_residence_benefit_equal_to_line_10400_is_accepted() -> None:
    # Equal is accepted: the benefit of 10400 against line 10400 of 10400 is checked and summed,
    # and with (A) alone the deduction on line 23100 is the 10400.

    worksheet = return_cy(
        employment="34600",
        clergy_employer_residence_benefit="10400",
        other_employment_income="10400",
        clergy_qualifying_employment_income="0",
        clergy_months_in_qualifying_employment=0,
        clergy_accommodation_cost="0",
    )

    assert worksheet.get(CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED).value == D("10400")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("10400.00")


def test_a_claim_on_line_7_above_line_6_is_refused_not_capped() -> None:
    # Line 6 of 0 (no rent) and line 7 of 5000, with no months, no qualifying income and no
    # employer benefit: line 7 is more than line 6, an input error. The check refuses the return;
    # the line 8 "Line 6 minus line 7" it would otherwise give (-5000) is never computed.
    message = "ca/clergy_other_accommodation_claims 5000 is above ca/clergy_accommodation_cost 0"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_cy(
            clergy_qualifying_employment_income="0",
            clergy_months_in_qualifying_employment=0,
            clergy_accommodation_cost="0",
            clergy_other_accommodation_claims="5000",
        )


def test_a_claim_on_line_7_above_line_6_is_refused_with_the_employers_benefit_too() -> None:
    # The same line 6 of 0 and line 7 of 5000 with the employer's residence benefit (A) of 12000,
    # which is at most line 10400 (12000): the benefit is accepted, and line 7 is still refused.
    message = "ca/clergy_other_accommodation_claims 5000 is above ca/clergy_accommodation_cost 0"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_cy(
            clergy_qualifying_employment_income="0",
            clergy_months_in_qualifying_employment=0,
            clergy_accommodation_cost="0",
            clergy_other_accommodation_claims="5000",
            clergy_employer_residence_benefit="12000",
            other_employment_income="12000",
        )


def test_a_claim_on_line_7_equal_to_line_6_is_accepted_and_line_8_is_0() -> None:
    # Line 6 and line 7 both 14000: equal is accepted, the claim is passed on as 14000, and line 8
    # "Line 6 minus line 7 =" is 0, so line 9 and line 10 are 0 and line 23100 is 0.
    worksheet = return_cy(clergy_other_accommodation_claims="14000")

    assert worksheet.get(CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED).value == D("14000")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("0")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_9).value == D("0")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_10).value == D("0")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("0")


def test_a_claim_on_line_7_below_line_6_is_passed_on_and_line_8_is_the_difference() -> None:
    # Line 6 of 14000 and line 7 of 5000: the claim is passed on as 5000 and line 8 is the
    # difference, 9000, which line 9 and line 10 then carry to line 23100.
    worksheet = return_cy(clergy_other_accommodation_claims="5000")

    assert worksheet.get(CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED).value == D("5000")
    assert worksheet.get(CLERGY_RESIDENCE_LINE_8).value == D("9000.00")
    assert worksheet.get(CLERGY_RESIDENCE_DEDUCTION).value == D("9000.00")
