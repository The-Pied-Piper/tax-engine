"""CA-ON 2025 end to end: return y."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ALLOWABLE_BUSINESS_INVESTMENT_LOSS,
    BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION,
    BUSINESS_INVESTMENT_LOSS_REDUCTION,
    CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION,
    CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024,
    CHILD_CARE_EXPENSES,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_SIGNED,
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    RPP_DEDUCTION,
    SECURITY_OPTIONS_DEDUCTIONS,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
    UNION_DUES,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    CARE_ADJUSTED_INCOME,
    CARE_CREDIT,
    CARE_CREDIT_PERCENTAGE,
    CARE_FAMILY_ADJUSTED_INCOME,
    CARE_SUPPORTING_PERSONS_ADJUSTED_INCOME,
    ONTARIO_CREDITS_SUBTOTAL,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    compute,
    return_f_with_credits,
    routed_statement,
)


def test_return_ys_supporting_person_lowers_the_care_credit_to_1650() -> None:
    # Return Y is Return F with a supporting person's adjusted income of 30000 (Schedule ON479-A
    # column 2 line 4, line 63047). Line 4 is 54435.00 + 5000 = 59435.00, line 5 is 59435.00 +
    # 30000 = 89435.00, in "more than $88,800 but not more than $92,400: 33%", so line 7 is 33%
    # (Return F's 51%) and line 8 is 5000 x 33% = 1650.00. Line 18 and T1 line 47900 are 1650.00,
    # the total credits 8000 + 0 + 1650.00 = 9650.00 and line 167 is 4240.69 - 9650.00 =
    # -5409.31, Return F's -6309.31 plus the 900.00 the supporting person takes off the credit.
    return_f = return_f_with_credits("0", "0")
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
    )

    assert worksheet.get(CARE_SUPPORTING_PERSONS_ADJUSTED_INCOME).value == D("30000")
    assert worksheet.get(CHILD_CARE_EXPENSES).value == D("5000")
    assert worksheet.get(CARE_ADJUSTED_INCOME).value == D("59435.00")
    assert worksheet.get(CARE_FAMILY_ADJUSTED_INCOME).value == D("89435.00")
    assert worksheet.get(CARE_CREDIT_PERCENTAGE).value == Rate(D("0.33"))
    assert worksheet.get(CARE_CREDIT).value == D("1650.00")
    assert worksheet.get(ONTARIO_CREDITS_SUBTOTAL).value == D("1650.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("1650.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4240.69")
    assert worksheet.get(TOTAL_CREDITS).value == D("9650.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-5409.31")
    assert return_f.get(CARE_CREDIT_PERCENTAGE).value == Rate(D("0.51"))
    assert return_f.get(CARE_FAMILY_ADJUSTED_INCOME).value == D("59435.00")
    assert return_f.get(REFUND_OR_BALANCE_OWING).value - worksheet.get(
        REFUND_OR_BALANCE_OWING
    ).value == D("-900.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "care_family_adjusted_income: care_adjusted_income 59435 "
        "+ care_supporting_persons_adjusted_income 30000 = 89435"
    ) in rendered
    assert (
        "care_credit_percentage: care_family_adjusted_income 89435, "
        "more than 88800 but not more than 92400: 33%"
    ) in rendered
    assert (
        "care_credit: care_credit_percentage 33% of child_care_expenses 5000 (half-up to 0.01)"
    ) in rendered
    assert (
        "ontario_credits_subtotal: fertility_credit 0 + care_credit 1650 "
        "+ seniors_care_credit 0 + seniors_transit_credit 0 + political_credit 0 "
        "+ flow_through_share_credit 0 = 1650"
    ) in rendered


def test_a_family_adjusted_income_of_0_is_taxed_at_75_percent() -> None:
    # Schedule ON479-A line 7: "If your family adjusted income on line 5 is "0", enter 75%." No
    # income and no supporting person: line 4 is 0, line 5 is 0, line 7 is 75% and, with no child
    # care expenses (line 6, 0), line 8 is 0 x 75% = 0.00.
    worksheet = compute("0", (), "0", "0", "0", "0", "0")

    assert worksheet.get(CARE_ADJUSTED_INCOME).value == D("0")
    assert worksheet.get(CARE_FAMILY_ADJUSTED_INCOME).value == D("0")
    assert worksheet.get(CARE_CREDIT_PERCENTAGE).value == Rate(D("0.75"))
    assert worksheet.get(CARE_CREDIT).value == D("0.00")


def test_a_family_adjusted_income_on_a_row_limit_takes_that_rows_rate() -> None:
    # Schedule ON479-A line 5 is the supporting person's 30000 alone: "more than $27,500 but not
    # more than $30,000: 67%" includes 30,000, so line 7 is 67%, not the next row's 65%.
    worksheet = compute(
        "0", (), "0", "0", "0", "0", "0", care_supporting_persons_adjusted_income="30000"
    )

    assert worksheet.get(CARE_FAMILY_ADJUSTED_INCOME).value == D("30000")
    assert worksheet.get(CARE_CREDIT_PERCENTAGE).value == Rate(D("0.67"))
    assert worksheet.get(CARE_CREDIT).value == D("0.00")


def test_a_net_income_below_zero_is_floored_at_zero_on_line_4() -> None:
    # Schedule ON479-A line 4 "Add lines 1 to 3 (if negative, enter "0")": line 1 is the
    # TOSI-adjusted net income, 0 + line 23600 before its floor, 0 - a business loss of 1000 =
    # -1000.00 (line 23500 is 0), line 2 is 0 and line 3 is 0, so line 4 is 0, not -1000.00, and
    # line 5 is 0 with no supporting person.
    worksheet = compute(
        "0", (), "0", "0", "0", "0", "0", business_statements=(routed_statement("-1000", 1),)
    )

    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("-1000.00")
    assert worksheet.get(NET_INCOME_SIGNED).value == D("-1000.00")
    assert worksheet.get(NET_INCOME).value == D("0")
    assert worksheet.get(CARE_ADJUSTED_INCOME).value == D("0")
    assert worksheet.get(CARE_FAMILY_ADJUSTED_INCOME).value == D("0")
    assert worksheet.get(CARE_CREDIT_PERCENTAGE).value == Rate(D("0.75"))
    assert (
        "care_adjusted_income: tosi_adjusted_net_income -1000 + child_care_expenses 0 "
        "+ social_benefits_repayment 0, not below 0 = 0"
    ) in EnglishTraceRenderer().render_all(worksheet.trace)


def test_return_y_business_investment_loss_multiplies_the_1990_to_1999_amount_by_1_3333() -> None:
    # Return Y, with the supporting person's 30000 as in the return. The 1990 to 1999 amount is the
    # line 254 total, 10000, and line 4 prints it "x 1.3333": 13333.00. Line 7 is 13333.00 and line
    # 15 is the same less nothing in line 14; line 17 is the lesser of that and the loss of 20000,
    # 13333.00; line 18 is 20000 less 13333.00, 6667.00; and line 20 is 6667.00 x 50%, 3333.50. The
    # deduction is 1666.50 less than the 5000.00 that reading 10000 as printed gave, so the refund,
    # -6456.35, is 538.21 less negative than the -6994.56 of that reading.
    line_4 = ArtifactRegistry.shared().kind("ca/capital_gains_deductions_line_4")
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        eligible_dependants=1,
        cwb_eligible_dependants=1,
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
        care_supporting_persons_adjusted_income="30000",
        capital_gains_deductions_1990_to_1999="10000",
        business_investment_loss="20000",
    )

    assert worksheet.get(line_4).value == D("13333.00")
    assert worksheet.get(CAPITAL_GAINS_DEDUCTIONS_CLAIMED_1985_TO_2024).value == D("13333.00")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_REDUCTION).value == D("13333.00")
    assert worksheet.get(BUSINESS_INVESTMENT_LOSS_AFTER_REDUCTION).value == D("6667")
    assert worksheet.get(ALLOWABLE_BUSINESS_INVESTMENT_LOSS).value == D("3333.50")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6456.35")


# The T4 slip deductions are taken as typed: the guide prints no limit on lines 20700, 21200, 24400
# and 24900, so an amount above the income is not refused or capped and reads as entered.


def test_an_rpp_deduction_above_the_wages_is_read_as_typed() -> None:
    # Guide 5000-G line 20700 "Generally, you can deduct the total of all amounts from box 20 of
    # your T4 slips, box 032 of your T4A slips, and your union or RPP receipts": 40000 against 30000
    # of employment income is the amount the filer enters, and the deductions read it.
    worksheet = compute("30000", (), "0", "0", "0", "0", "0", rpp_deduction="40000")

    assert worksheet.get(RPP_DEDUCTION).value == D("40000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value >= D("40000")


def test_a_union_dues_amount_above_the_wages_is_read_as_typed() -> None:
    # Guide 5000-G line 21200 "Claim the total of the following amounts that you paid (or that were
    # paid for you and reported as income) in the year related to your employment": 40000 against
    # 30000 of wages is read as entered.
    worksheet = compute("30000", (), "0", "0", "0", "0", "40000")

    assert worksheet.get(UNION_DUES).value == D("40000")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value >= D("40000")


def test_an_armed_forces_and_police_deduction_above_the_wages_is_read_as_typed() -> None:
    # Guide 5000-G line 24400 "Claim on line 24400 of your return the total of the amounts shown in
    # box 43 of your T4 slips": 40000 against 30000 of wages is read as entered.
    worksheet = compute(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        canadian_armed_forces_and_police_deduction="40000",
    )

    assert worksheet.get(CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION).value == D("40000")


def test_a_security_options_deduction_above_the_wages_is_read_as_typed() -> None:
    # Guide 5000-G line 24900 "Claim on line 24900 of your return the total of the amounts shown in
    # boxes 39, 41, 91, and 92 of your T4 slips": box 39 of 40000 against 30000 of wages is read as
    # entered, and the line 24900 sum reads it.
    worksheet = compute(
        "30000", (), "0", "0", "0", "0", "0", t4_security_options_boxes_39_and_91="40000"
    )

    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("40000")


def test_zero_rpp_union_and_t4_security_deductions_are_accepted() -> None:
    # Zero is read as zero, with no deduction claimed.
    worksheet = compute("60000", (), "0", "0", "0", "0", "0")

    assert worksheet.get(RPP_DEDUCTION).value == D("0")
    assert worksheet.get(UNION_DUES).value == D("0")
    assert worksheet.get(CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION).value == D("0")
    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("0")


# A business loss larger than the other income makes total income negative. The T4 slip deductions
# are read as typed whether or not a loss is present. Employment income of 20000 with a business
# loss of 50000 (a T2125 net of -50000, routed to line 13500) gives a total income of -30000.00.
# Each entry is the input name and the kind it is read as; the security options deduction line
# 24900 is computed from the T4 boxes 39 and 91, so its input is the box.
LOSS_DEDUCTIONS = (
    ("rpp_deduction", RPP_DEDUCTION),
    ("union_dues", UNION_DUES),
    ("canadian_armed_forces_and_police_deduction", CANADIAN_ARMED_FORCES_AND_POLICE_DEDUCTION),
    ("t4_security_options_boxes_39_and_91", SECURITY_OPTIONS_DEDUCTIONS),
)


def return_with_a_loss(union_dues: str = "0", **overrides: Any) -> Worksheet:
    return compute(
        "20000",
        (),
        "0",
        "0",
        "0",
        "0",
        union_dues,
        business_statements=(routed_statement("-50000", 1),),
        **overrides,
    )


@pytest.mark.parametrize(("name", "kind"), LOSS_DEDUCTIONS)
def test_a_zero_t4_deduction_is_accepted_when_a_loss_makes_total_income_negative(
    name: str, kind: ArtifactKind[Decimal]
) -> None:
    worksheet = return_with_a_loss(**{name: "0"})

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(kind).value == D("0")


@pytest.mark.parametrize(("name", "kind"), LOSS_DEDUCTIONS)
def test_a_real_t4_deduction_is_accepted_when_a_loss_makes_total_income_negative(
    name: str, kind: ArtifactKind[Decimal]
) -> None:
    worksheet = return_with_a_loss(**{name: "1000"})

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(kind).value == D("1000")


@pytest.mark.parametrize(("name", "kind"), LOSS_DEDUCTIONS)
def test_a_deduction_above_the_income_before_losses_is_read_as_typed_with_a_loss(
    name: str, kind: ArtifactKind[Decimal]
) -> None:
    worksheet = return_with_a_loss(**{name: "20000.01"})

    assert worksheet.get(TOTAL_INCOME).value == D("-30000.00")
    assert worksheet.get(kind).value == D("20000.01")
