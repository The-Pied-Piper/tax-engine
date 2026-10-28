"""CA-ON 2025 end to end: return a dependant credits."""

from __future__ import annotations

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.trace import (
    AtMostLine,
    CappedAmountLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    ELIGIBLE_DEPENDANT_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT,
    FEDERAL_TAX_AFTER_CREDITS,
    INFIRM_CHILDREN,
    INFIRM_CHILDREN_AMOUNT,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    PROVINCIAL_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM,
    FERTILITY_CREDIT,
    FERTILITY_CREDIT_BEFORE_MAXIMUM,
    ONTARIO_CREDITS,
    SENIORS_TRANSIT_AMOUNT_PAID_CHECKED,
    SENIORS_TRANSIT_CREDIT,
    SENIORS_TRANSIT_MAXIMUM,
    SENIORS_TRANSIT_PAID,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute, return_f_with_credits


def test_the_fertility_credit_below_its_maximum_is_25_percent_of_the_expenses() -> None:
    # 12000 x 25% = 3000.00, below the maximum of 5000, so line 1 is 3000.00 and the credits are
    # 3000.00 with no transit amount; with the care credit of 2550.00 line 18 is 5550.00.
    worksheet = return_f_with_credits("12000", "0")

    assert worksheet.get(FERTILITY_CREDIT_BEFORE_MAXIMUM).value == D("3000.00")
    assert worksheet.get(FERTILITY_CREDIT).value == D("3000.00")
    assert worksheet.get(SENIORS_TRANSIT_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS).value == D("5550.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("5550.00")
    assert worksheet.get(TOTAL_CREDITS).value == D("13550.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-9309.31")


def test_the_transit_amount_paid_of_3000_is_taken_then_the_rate() -> None:
    # 3000 paid, the most ON479 line 14 takes ("(maximum $3,000)" before the percentage):
    # 3000 x 15% = 450.00; with the care credit of 2550.00 line 18 is 3000.00.
    worksheet = return_f_with_credits("0", "3000")

    assert worksheet.get(SENIORS_TRANSIT_AMOUNT_PAID_CHECKED).value == D("3000")
    assert worksheet.get(SENIORS_TRANSIT_CREDIT).value == D("450.00")
    assert worksheet.get(FERTILITY_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_CREDITS).value == D("3000.00")
    assert worksheet.get(PROVINCIAL_CREDITS).value == D("3000.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-6759.31")
    (checked_paid,) = [
        line
        for line in worksheet.trace
        if isinstance(line, AtMostLine) and line.output == SENIORS_TRANSIT_AMOUNT_PAID_CHECKED
    ]
    assert checked_paid == AtMostLine(
        output=SENIORS_TRANSIT_AMOUNT_PAID_CHECKED,
        amount_kind=SENIORS_TRANSIT_PAID,
        amount_value=D("3000"),
        bound=SENIORS_TRANSIT_MAXIMUM,
        bound_value=D("3000.00"),
    )


def test_the_transit_amount_paid_above_3000_is_refused_not_capped() -> None:
    # 3500 paid is above ON479 line 14's "(maximum $3,000)": an input error, not 3000 x 15%.
    with pytest.raises(InputAboveBoundError, match="seniors_transit_paid 3500 is above"):
        return_f_with_credits("0", "3500")


def test_the_fertility_credit_is_capped_after_the_rate() -> None:
    # 24000 x 25% = 6000.00 is above 5000, so line 1 is the maximum, whereas capping the expenses
    # at 5000 first would give 1250.00.
    worksheet = return_f_with_credits("24000", "0")

    (capped,) = [
        line
        for line in worksheet.trace
        if isinstance(line, CappedAmountLine) and line.output == FERTILITY_CREDIT
    ]
    assert capped == CappedAmountLine(
        FERTILITY_CREDIT,
        FERTILITY_CREDIT_BEFORE_MAXIMUM,
        D("6000.00"),
        Amount(D("5000")),
        CENT,
        D("5000"),
    )


def test_the_dependants_net_income_comes_off_both_amounts() -> None:
    # Return F's amounts with a dependant's net income of 1500 (Schedule 5 line 4, ON428 line
    # 15): line 5 is 16129.00 - 1500 = 14629.00, and ON428 line 16 is 11905.00 - 1500 =
    # 10405.00, below the $10,823 maximum, so kept. Line 33500 is 16129 + 14629.00 + 0 +
    # 2796.75 + 984.00 + 1471 = 36009.75; ON428 line 58800 is 12747 + 10405.00 + 2796.75 +
    # 984.00 = 26932.75.
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
        dependant_net_income="1500",
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
    )

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("14629.00")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("10405.00")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("10405.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("36009.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("26932.75")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "eligible_dependant_amount_before_count: eligible_dependant_amount_basis 16129 "
        "less dependant_net_income 1500, not below 0 = 14629"
    ) in rendered
    assert (
        "eligible_dependant_amount_before_count: lesser of "
        "eligible_dependant_amount_before_maximum 10405 and 10823 (half-up to 0.01)"
    ) in rendered


def test_a_dependant_with_more_income_than_the_amounts_adds_nothing() -> None:
    # Schedule 5 line 5 and ON428 line 16 "(if negative, enter "0")": a dependant's net income
    # of 20000 is above both 16129.00 and 11905.00, so each amount is 0 and the totals are those
    # without a dependant: 16129 + 0 + 0 + 2796.75 + 984.00 + 1471 = 21380.75 and 12747 + 0 +
    # 2796.75 + 984.00 = 16527.75.
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
        dependant_net_income="20000",
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
    )

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("0")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_MAXIMUM).value == D("0")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("21380.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("16527.75")


def test_no_eligible_dependant_claims_nothing_whatever_the_dependants_income() -> None:
    # Return F's amounts with no eligible dependant claimed for but a dependant's net income of
    # 1500 entered: Schedule 5 line 5 is still 14629.00, but line 30400 claims it for 0
    # eligible dependants, so it is 0, and so is line 58160.
    worksheet = compute(
        "60000",
        (),
        "0",
        "0",
        "10800",
        "0",
        "0",
        dependent_children=1,
        dependant_net_income="1500",
        child_care_expenses_paid="6000",
        children_seven_to_sixteen=1,
        income_tax_deducted="8000",
    )

    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("14629.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT).value == D("10405.00")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("21380.75")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("16527.75")


def test_infirm_children_add_2687_each_to_the_federal_amounts_only() -> None:
    # Return A's amounts with two infirm children (T1 line 30499): line 30500 is 2 x 2687 =
    # 5374, so line 33500 is 22033.58 + 5374 = 27407.58, line 35000 27407.58 x 14.5% =
    # 3974.0991, rounded half-up to the cent: 3974.10, and the federal tax after credits
    # 20146.25 - 3974.10 = 16172.15. ON428 has
    # no such line here (its caregiver amount, line 58185, is not triggered), so its total is
    # unchanged at 17180.58.
    worksheet = compute(
        "110000", (("20000", "0", "0"),), "0", "1926", "19800", "1926", "2000", infirm_children=2
    )

    assert worksheet.get(INFIRM_CHILDREN).value == 2
    assert worksheet.get(INFIRM_CHILDREN_AMOUNT).value == D("5374")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("27407.58")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("3974.10")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("16172.15")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("17180.58")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "infirm_children_amount: 2687 for each of 2 infirm_children = 5374 (half-up to 0.01)"
        in (rendered)
    )
