"""CA-ON 2025 end to end: return ah."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace import (
    SumLine,
    ThresholdGateLine,
)
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_OVERPAYMENT,
    DISABILITY_SUPPORTS_DEDUCTION,
    EI_OVERPAYMENT,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    MEDICAL_CLAIM,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
    MEDICAL_SUPPLEMENT_IF_RESIDENT,
    MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET,
    MEDICAL_SUPPLEMENT_INCOME_THRESHOLD,
    MEDICAL_SUPPLEMENT_LINE_6,
    MEDICAL_SUPPLEMENT_LINE_8,
    MEDICAL_SUPPLEMENT_LINE_11,
    MEDICAL_SUPPLEMENT_LINE_13,
    MEDICAL_SUPPLEMENT_LINE_14,
    MEDICAL_SUPPLEMENT_LINE_15,
    MEDICAL_SUPPLEMENT_LINE_16,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_WORKING_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    TOTAL_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ah(employment: str = "4390", union_dues: str = "0", **overrides: Any) -> Worksheet:
    """Return AH's inputs, as in `returns/2025_return_ah.yaml`, over the keyword overrides given.

    The helper supplies one copy of Form T929 (`t929_copies` 1), which the worked return file does
    not carry; that file has no copy, so its line 21500 is 0, and the tests here measure line 21500
    with the copy.

    Lina, 30, resident in Canada throughout 2025: employment income of 4390 (the working income,
    exactly the $4,390 the supplement asks), other income of 15618.90 so that the net income is
    20000.00 after the enhanced CPP contributions of 8.90, and medical expenses of 6600, of which
    3% of the net income, 600.00, comes off: a medical claim (line 33200) of 6000.00.
    """
    inputs: dict[str, Any] = {
        "other_income": "15618.90",
        "medical_expenses": "6600",
        "income_tax_deducted": "500",
        "t929_copies": 1,
    }
    inputs.update(overrides)
    return compute(employment, (), "0", "0", "0", "0", union_dues, **inputs)


def test_return_ah_claims_the_refundable_medical_expense_supplement_of_1500_on_line_45200() -> None:
    worksheet = return_ah()

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("20000.00")
    assert worksheet.get(MEDICAL_CLAIM).value == D("6000.00")
    # "your employment income from lines 10100 and 10400" less lines 20700, 21200, 22900 and
    # 23100: 4390 less 0; no net self-employment income: exactly the 4,390 the worksheet asks.
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME).value == D("4390")
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS).value == D("4390")
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME).value == D("4390")
    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_WORKING_INCOME).value == D("4390")
    # Lines 1 to 5 of the two columns: the filer's net income, the spouse's column 0.
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3).value == D("20000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5).value == D("20000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D("20000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_INCOME_THRESHOLD).value == D("33294.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_8).value == D("0")
    # 21500 + 33200 = 0 + 6000.00, 25% = 1500.00, under the 1,504 maximum, no reduction.
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_11).value == D("6000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_13).value == D("1500.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_14).value == D("1500.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_15).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_16).value == D("1500.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET).value == D("1500.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_IF_RESIDENT).value == D("1500.00")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("1500.00")
    # Line 166 adds it to the income tax deducted of 500.
    assert worksheet.get(TOTAL_CREDITS).value >= D("2000.00")
    (total,) = [
        line
        for line in worksheet.trace
        if isinstance(line, SumLine) and line.output == TOTAL_CREDITS
    ]
    assert total.parts[:4] == (
        (INCOME_TAX_DEDUCTED_AFTER_ELECTION, D("500")),
        (CPP_OVERPAYMENT, D("0")),
        (EI_OVERPAYMENT, D("0")),
        (REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT, D("1500.00")),
    )


def test_return_ahs_trace_names_the_gate_and_the_two_counts() -> None:
    worksheet = return_ah()
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert (
        "medical_supplement_if_working_income_met: medical_supplement_line_16 1500 "
        "if medical_supplement_working_income 4390 is at least 4390 (half-up to 0.01) = 1500"
    ) in rendered
    assert (
        "medical_supplement_if_resident: medical_supplement_if_working_income_met 1500 "
        "for each of 1 resident_in_canada_throughout_2025_checked = 1500"
    ) in rendered
    assert (
        "refundable_medical_expense_supplement: medical_supplement_if_resident 1500 "
        "for each of 1 aged_18_or_older_at_end_of_2025_checked = 1500"
    ) in rendered
    assert any(
        isinstance(line, ThresholdGateLine)
        and line.output == MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET
        for line in worksheet.trace
    )


def supplement_only_if(worksheet: Worksheet, met: bool) -> None:
    """Line 16 is positive; the supplement is it when the conditions are met and 0 otherwise."""
    line_16 = worksheet.get(MEDICAL_SUPPLEMENT_LINE_16).value
    assert line_16 > 0
    expected = line_16 if met else D("0")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == expected


@pytest.mark.parametrize(
    ("business_profit", "met"),
    [("389.99", False), ("390", True), ("390.01", True)],
)
def test_the_working_income_of_4390_or_more_includes_the_net_self_employment_income(
    business_profit: str, met: bool
) -> None:
    # Employment income of 4000 plus the net business income of one T2125 statement (line 13500):
    # 4,389.99 does not meet "must be $4,390 or more", 4,390 and 4,390.01 do.
    worksheet = return_ah(
        "4000", business_statements=({"business": {"gross_sales": business_profit}},)
    )

    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D(business_profit)
    supplement_only_if(worksheet, met)


def test_each_of_the_five_self_employment_lines_counts_toward_the_working_income() -> None:
    worksheet = return_ah(
        "4000",
        business_statements=(
            {"business": {"gross_sales": "100"}},
            {"business": {"gross_sales": "90"}, "business_income_line": 2},
            {"business": {"gross_sales": "80"}, "business_income_line": 3},
        ),
        farm_statements=({"farm": {"wheat": "70"}},),
        fish_statements=({"fish": {"fish_products": "50"}},),
    )

    assert worksheet.get(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME).value == D("390")
    assert worksheet.get(MEDICAL_SUPPLEMENT_WORKING_INCOME).value == D("4390")
    supplement_only_if(worksheet, True)


@pytest.mark.parametrize(("wage_loss", "met"), [("0", True), ("0.01", False), ("4390", False)])
def test_wage_loss_replacement_plan_amounts_do_not_count_toward_the_working_income(
    wage_loss: str, met: bool
) -> None:
    worksheet = return_ah(wage_loss_replacement_plan_income=wage_loss)

    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS).value == D(
        "4390"
    ) - D(wage_loss)
    supplement_only_if(worksheet, met)


@pytest.mark.parametrize(
    "deduction",
    ["t777_other_expenses", "clergy_employer_residence_benefit"],
)
@pytest.mark.parametrize(("amount", "met"), [("100", True), ("100.01", False)])
def test_lines_22900_and_23100_come_off_the_employment_income(
    deduction: str, amount: str, met: bool
) -> None:
    # Employment income of 4490 less 100 is exactly 4390; a cent more comes off and it is short.
    # Line 23100 is the employer residence benefit (A) when the (B) part is not completed. The
    # benefit is reported on line 10400, so it is at most `ca/other_employment_income` (the amount):
    # the 4490 of employment is split between lines 10100 and 10400 so that the working income is
    # still 4490.
    employment, overrides = "4490", {deduction: amount}
    if deduction == "clergy_employer_residence_benefit":
        employment = str(D("4490") - D(amount))
        overrides["other_employment_income"] = amount
    worksheet = return_ah(employment, **overrides)

    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS).value == D(amount)
    supplement_only_if(worksheet, met)


def test_the_deductions_of_lines_20700_and_21200_come_off_the_employment_income() -> None:
    # Union dues of 100 (line 21200) leave 4390 of 4490; the registered pension plan deduction
    # (line 20700) of a cent more leaves 4389.99.
    assert_met = return_ah("4490", union_dues="100")
    assert assert_met.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS).value == D("100")
    supplement_only_if(assert_met, True)
    short = return_ah("4490", union_dues="100", rpp_deduction="0.01")
    assert short.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME).value == D("4389.99")
    supplement_only_if(short, False)


def test_a_negative_employment_part_is_zero_and_does_not_reduce_the_self_employment_part() -> None:
    # "(if the result is negative, consider it as "0")": 4000 less 5000 is 0, not -1000, so the
    # 4390 of net business income alone meets the condition.
    worksheet = return_ah(
        "4000",
        t777_other_expenses="5000",
        business_statements=({"business": {"gross_sales": "4390"}},),
    )

    assert worksheet.get(MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_WORKING_INCOME).value == D("4390")
    supplement_only_if(worksheet, True)


@pytest.mark.parametrize(
    ("resident", "aged_18_or_older", "met"),
    [(1, 1, True), (0, 1, False), (1, 0, False), (0, 0, False)],
)
def test_the_residence_and_age_conditions_are_counts_of_one(
    resident: int, aged_18_or_older: int, met: bool
) -> None:
    worksheet = return_ah(
        resident_in_canada_throughout_2025=resident,
        aged_18_or_older_at_end_of_2025=aged_18_or_older,
    )

    supplement_only_if(worksheet, met)


def test_line_21500_alone_gives_the_supplement_without_a_medical_claim() -> None:
    # "You entered an amount on line 21500 or line 33200": line 9 of 6000 with no line 33200.
    worksheet = return_ah(
        medical_expenses="0",
        t929_expenses_paid="6000",
        t929_net_research_grants="1610",
    )

    assert worksheet.get(MEDICAL_CLAIM).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_11).value == D("6000")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("1500.00")


def test_lines_21500_and_33200_are_added_before_the_rate() -> None:
    worksheet = return_ah(medical_expenses="1600", t929_expenses_paid="3000")

    # Line 21500 is 3000.00 (the lesser of the 3000 paid and the 4390 earned income), which comes
    # off the net income: 20008.90 - 8.90 (enhanced CPP) - 3000.00 = 17000.00. Line 33200 is 1600
    # less 3% of 17000.00 (510.00), 1090.00. Line 11 is 3000.00 + 1090.00 = 4090.00, 25% of it is
    # 1022.50, under the 1504 maximum, and the supplement is that 1022.50.
    assert worksheet.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("3000.00")
    assert worksheet.get(NET_INCOME).value == D("17000.00")
    assert worksheet.get(MEDICAL_CLAIM).value == D("1090.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_11).value == D("4090.00")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("1022.50")


def test_no_amount_on_line_21500_or_line_33200_gives_no_supplement() -> None:
    worksheet = return_ah(medical_expenses="0")

    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_11).value == D("0")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("0")


def test_the_supplement_is_at_most_1504() -> None:
    # 25% of 8000 is 2000.00, line 14 is the 1,504 maximum.
    worksheet = return_ah(medical_expenses="8600")

    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_13).value == D("2000.00")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_14).value == D("1504")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("1504.00")


@pytest.mark.parametrize(
    ("spouse_net_income", "line_6", "supplement"),
    [
        # Line 6 adds the two columns' line 5; line 8 is line 6 over 33,294.00 and line 15 5% of it;
        # with medical expenses of 6616 line 14 is the 1,504 maximum.
        ("0", "20000.00", "1504.00"),
        ("13294", "33294.00", "1504.00"),
        ("13295", "33295.00", "1503.95"),
        ("43373", "63373.00", "0.05"),
        # "Your adjusted family net income is less than $63,374": no step of its own, as at 63,374
        # line 15 is 5% x 30,080 = 1,504.00 and line 16 is 0.
        ("43374", "63374.00", "0"),
        ("43375", "63375.00", "0"),
    ],
)
def test_the_spouses_column_is_added_to_the_adjusted_family_net_income(
    spouse_net_income: str, line_6: str, supplement: str
) -> None:
    worksheet = return_ah(
        medical_expenses="6616", spouse_net_income_before_adjustments=spouse_net_income
    )

    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_14).value == D("1504")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D(line_6)
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D(supplement)


def test_a_spouse_with_a_net_loss_shown_in_brackets_adds_nothing_to_line_6() -> None:
    # Column 2 line 1 may be negative ("if negative, show in brackets"); line 5 is "0" then.
    worksheet = return_ah(spouse_net_income_before_adjustments="-5000")

    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3).value == D("-5000")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5).value == D("0")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D("20000.00")


def test_the_spouses_repayments_are_added_and_the_spouses_uccb_and_rdsp_income_taken_off() -> None:
    worksheet = return_ah(
        spouse_net_income_before_adjustments="30000",
        spouse_uccb_repayment="100",
        spouse_rdsp_income_repayment="50",
        spouse_universal_child_care_benefit="1000",
        spouse_rdsp_income="200",
    )

    # Line 2 100 + 50, line 3 30000 + 150, line 4 1000 + 200, line 5 30150 - 1200.
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2).value == D("150")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3).value == D("30150")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4).value == D("1200")
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5).value == D("28950")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_6).value == D("48950.00")
    # Line 8 = 48950.00 - 33294.00 = 15656.00, line 15 = 782.80, line 16 = 1500.00 - 782.80.
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_15).value == D("782.80")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("717.20")


def test_the_filers_uccb_and_rdsp_amounts_adjust_column_1() -> None:
    worksheet = return_ah(uccb_repayment="100", rdsp_income_repayment="50", other_deductions="50")

    # The repayments are deductions of line 23300 (UCCB) and a part of line 23200 caller input;
    # column 1 line 2 adds both to the net income before adjustments.
    assert worksheet.get(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3).value == (
        worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value + D("150")
    )
