"""CA-ON 2025 end to end: return ba (net capital losses from before May 23, 1985)."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
    ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
    ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
    ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_LOSSES_LEFT_AFTER_2000,
    ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    DEDUCTIONS_FROM_NET_INCOME,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
    NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
    NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_INCOME,
    PRE_1986_CAPITAL_LOSS_BALANCE,
    PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
    PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
    PRE_1986_DEDUCTIONS_ADJUSTED_2000,
    PRE_1986_DEDUCTIONS_TOTAL,
    REFUND_OR_BALANCE_OWING,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
)
from tax_calculator.jurisdictions.ca_on.catalog import LIFT_CREDIT, ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Chart A's kinds by column, oldest row first.
COLUMN_C = (
    ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
)
COLUMN_D = (
    ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
)
LEFT_AFTER = (
    ADJUSTED_LOSSES_LEFT_AFTER_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
    ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_LOSSES_LEFT_AFTER_2000,
)
COLUMN_E = (
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
)
COLUMN_G = (
    NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
)


def return_ba(**overrides: Any) -> Worksheet:
    """Return BA's inputs, as in `returns/2025_return_ba.yaml`: Return AF's filer with a pre-1986
    balance.

    Employment income of 48000, a capital gain of 20000 (taxable capital gains of 10000.00),
    4800 deducted, unapplied net capital losses of 6000 from before May 23, 1985 (Form T1436 line
    1), a capital gains deduction of 500 claimed before 1988 (amount A) and of 300 in 2000
    (amount D, at an inclusion rate of 0.666666), unapplied net capital losses of 4000 from 1988
    and 6000 from 1990 (Chart A column A) and an amount claimed (line 7) of 10000.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "4800",
        "net_capital_losses_before_may_23_1985": "6000",
        "pre_1986_deductions_before_1988": "500",
        "pre_1986_deductions_2000": "300",
        "t657_inclusion_rate_2000": "0.666666",
        "unapplied_net_capital_losses_1988_and_1989": "4000",
        "unapplied_net_capital_losses_1990_to_1999": "6000",
        "net_capital_losses_claimed": "10000",
    }
    return compute(
        "48000",
        (("20000", "0", "0"),),
        "0",
        "0",
        "8640",
        "0",
        "0",
        **{**inputs, **overrides},
    )


def values(worksheet: Worksheet, kinds: tuple[Any, ...]) -> list[Any]:
    return [worksheet.get(kind).value for kind in kinds]


def test_return_bas_pre_1986_balance_is_applied_first_and_the_extra_2000_is_line_9() -> None:
    # Form T1436 line 1 is 6000 and the capital gains deductions are A = 500 before 1988, D = 300
    # in 2000 at an inclusion rate of 0.666666 (Guide T4037's 2/3), 300 x 1/(0.666666 x 2) =
    # 300 / 1.333332 = 225.000225, 225.00, and none in the other periods, so line 2 is 500 +
    # 0.00 + 0.00 + 225.00 + 0 = 725.00 and line 3 is 6000 - 725.00 = 5275.00. Chart A column A:
    # 5275.00 (row "Before May 23, 1985", line 3), 0, 4000, 6000, 0 (2000) and 0; column C (x 1,
    # 1, 3/4, 2/3, 1/(IR x 2), 1): 5275.00, 0.00, 3000.00, 4000.00, 0.00 and 0.00. Line 4 is
    # 12275.00; line 5, the taxable capital gains, is 20000 x 50% = 10000.00 and line 6 is
    # 10000.00. Line 7, the claim, is 10000. Line 8 is 12275.00 - 10000 = 2275.00. Line 9 is the
    # least of line 3 (5275.00), line 8 (2275.00) and $2,000: 2000. Line 10, T1 line 25300, is
    # 10000 + 2000 = 12000, and line 13 is 12000. Column D, oldest first, is 5275.00 (6725.00 of
    # line 13 left), 0.00 (6725.00 left), 3000.00 (3725.00 left), 3725.00 (0.00 left), 0.00 and
    # 0.00, which add up to 12000.00 = line 13. Column E, column C less column D, is 0.00, 0.00,
    # 0.00, 275.00, 0.00 and 0.00; column G, column E x column F (1, 1, 4/3, 3/2, 2 x IR and 1),
    # is 0.00, 0.00, 0.00, 412.50, 0.00 and 0.00. Net income is 58000.00 - 445.00 = 57555.00
    # (the deduction is below net income) and taxable income is 57555.00 - 12000 = 45555.00. The
    # federal tax after credits is 6605.48 - 2985.54 = 3619.94 (45555.00 x 14.5% = 6605.475);
    # the Ontario tax is 2300.53 - 794.72 = 1505.81 plus the health premium of 450 (taxable
    # income between 38500 and 48000), 1955.81; the LIFT credit is 0 (5% x (57555.00 - 32500) =
    # 1252.75 is more than 875). The total payable is 3619.94 + 1955.81 = 5575.75 against total
    # credits of 4800.00: 775.75 owing.
    worksheet = return_ba()

    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("10000.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989).value == D("0.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999).value == D("0.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_2000).value == D("225.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_TOTAL).value == D("725.00")
    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("5275.00")
    assert values(worksheet, COLUMN_C) == [
        D("5275.00"),
        D("0.00"),
        D("3000.00"),
        D("4000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("12275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("10000.00")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("10000")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("2275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("2000")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("12000")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("12000")
    assert values(worksheet, COLUMN_D) == [
        D("5275.00"),
        D("0.00"),
        D("3000.00"),
        D("3725.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, LEFT_AFTER) == [
        D("6725.00"),
        D("6725.00"),
        D("3725.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_E) == [
        D("0.00"),
        D("0.00"),
        D("0.00"),
        D("275.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_G) == [
        D("0.00"),
        D("0.00"),
        D("0.00"),
        D("412.50"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("12000")
    assert worksheet.get(NET_INCOME).value == D("57555.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("45555.00")
    assert worksheet.get(LIFT_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_TAX).value == D("1955.81")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5575.75")
    assert worksheet.get(TOTAL_CREDITS).value == D("4800.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("775.75")


def test_return_bas_trace_names_the_pre_1986_lines() -> None:
    rendered = EnglishTraceRenderer().render_all(return_ba().trace)

    assert (
        "pre_1986_deductions_adjusted_2000: pre_1986_deductions_2000 300 "
        "× net_capital_loss_numerator_one_2000 1 / net_capital_loss_twice_ir_2000 1.333332 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "pre_1986_deductions_total: pre_1986_deductions_before_1988 500 "
        "+ pre_1986_deductions_adjusted_1988_and_1989 0 "
        "+ pre_1986_deductions_adjusted_1990_to_1999 0 "
        "+ pre_1986_deductions_adjusted_2000 225 "
        "+ pre_1986_deductions_2001_to_2024 0 = 725"
    ) in rendered
    assert (
        "pre_1986_capital_loss_balance: net_capital_losses_before_may_23_1985 6000 "
        "less pre_1986_deductions_total 725 = 5275"
    ) in rendered
    assert (
        "adjusted_gross_capital_losses_before_may_23_1985: 1/1 of pre_1986_capital_loss_balance "
        "5275 (half-up to 0.01)"
    ) in rendered
    assert (
        "total_adjusted_net_capital_losses: "
        "adjusted_gross_capital_losses_before_may_23_1985 5275 "
        "+ adjusted_gross_capital_losses_1985_to_1987 0 "
        "+ adjusted_gross_capital_losses_1988_and_1989 3000 "
        "+ adjusted_gross_capital_losses_1990_to_1999 4000 "
        "+ adjusted_gross_capital_losses_2000 0 "
        "+ adjusted_gross_capital_losses_2001_to_2024 0 = 12275"
    ) in rendered
    assert (
        "adjusted_net_capital_losses_applied: net_capital_losses_claimed 10000, "
        "at most net_capital_losses_available_to_claim 10000"
    ) in rendered
    assert (
        "unapplied_adjusted_net_capital_losses: total_adjusted_net_capital_losses 12275 "
        "less adjusted_net_capital_losses_applied 10000 = 2275"
    ) in rendered
    assert (
        "net_capital_losses_additional_deduction: lesser of pre_1986_capital_loss_balance 5275 "
        "and unapplied_adjusted_net_capital_losses 2275 and 2000 (half-up to 0.01) = 2000"
    ) in rendered
    assert (
        "net_capital_losses_of_other_years: adjusted_net_capital_losses_applied 10000 "
        "+ net_capital_losses_additional_deduction 2000 = 12000"
    ) in rendered
    assert (
        "total_adjusted_net_capital_losses_applied: adjusted_net_capital_losses_applied 10000 "
        "+ net_capital_losses_additional_deduction 2000 = 12000"
    ) in rendered
    assert (
        "adjusted_losses_applied_before_may_23_1985: lesser of "
        "adjusted_gross_capital_losses_before_may_23_1985 5275 "
        "and total_adjusted_net_capital_losses_applied 12000 = 5275"
    ) in rendered
    assert (
        "adjusted_losses_left_after_before_may_23_1985: total_adjusted_net_capital_losses_applied "
        "12000 less adjusted_losses_applied_before_may_23_1985 5275 = 6725"
    ) in rendered
    assert (
        "adjusted_losses_applied_1985_to_1987: lesser of "
        "adjusted_gross_capital_losses_1985_to_1987 0 "
        "and adjusted_losses_left_after_before_may_23_1985 6725 = 0"
    ) in rendered
    assert (
        "adjusted_losses_left_after_1985_to_1987: adjusted_losses_left_after_before_may_23_1985 "
        "6725 less adjusted_losses_applied_1985_to_1987 0 = 6725"
    ) in rendered
    assert (
        "net_capital_loss_balance_1990_to_1999: 3/2 of remaining_adjusted_losses_1990_to_1999 275 "
        "(half-up to 0.01)"
    ) in rendered


def test_the_total_of_column_d_is_line_13_and_the_balances_are_next_years_losses() -> None:
    # Note (4): "The total for column D must equal the amount from line 13."
    worksheet = return_ba()

    assert sum(values(worksheet, COLUMN_D)) == D("12000.00")
    assert (
        sum(values(worksheet, COLUMN_D))
        == worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value
    )


def test_line_9_is_line_8_when_line_8_is_the_least() -> None:
    # A loss of 6000 becomes 3000 from 1990: column C is 5275.00, 0.00, 3000.00, 2000.00, 0.00 and
    # 0.00, line 4 is 10275.00, line 6 is 10000.00 and line 7 (the claim) is 10000, so line 8 is
    # 275.00, less than line 3 (5275.00) and $2,000: line 9 is 275.00, line 10 and line 13 are
    # 10275.00. Column D is 5275.00 (5000.00 left), 0.00 (5000.00 left), 3000.00 (2000.00 left),
    # 2000.00 (0.00 left), 0.00 and 0.00; nothing remains in column E or G. Taxable income is
    # 57555.00 - 10275.00 = 47280.00.
    worksheet = return_ba(unapplied_net_capital_losses_1990_to_1999="3000")

    assert values(worksheet, COLUMN_C) == [
        D("5275.00"),
        D("0.00"),
        D("3000.00"),
        D("2000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("10275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("10000.00")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("10275.00")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("10275.00")
    assert values(worksheet, COLUMN_D) == [
        D("5275.00"),
        D("0.00"),
        D("3000.00"),
        D("2000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, LEFT_AFTER) == [
        D("5000.00"),
        D("5000.00"),
        D("2000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_E) == [D("0.00")] * 6
    assert values(worksheet, COLUMN_G) == [D("0.00")] * 6
    assert worksheet.get(TAXABLE_INCOME).value == D("47280.00")


def test_line_9_is_line_3_when_line_3_is_the_least() -> None:
    # Line 1 of 2000 less the deductions of 500 and 225.00 is a line 3 of 1275.00; with 4000 from
    # 1988 (column C 3000.00) line 4 is 1275.00 + 3000.00 = 4275.00, line 6 is 4275.00 and a claim
    # of 1000 (line 7) leaves line 8 of 3275.00: line 9 is the least of 1275.00, 3275.00 and
    # $2,000, 1275.00, so line 10 and line 13 are 1000 + 1275.00 = 2275.00. Column D is 1275.00
    # (1000.00 left), 0.00 (1000.00 left), 1000.00 (0.00 left), 0.00, 0.00 and 0.00; column E is
    # 0.00, 0.00, 2000.00, 0.00, 0.00 and 0.00 and column G for 1988 and 1989 is 2000.00 x 4/3 =
    # 2666.67 (rounded half-up to the cent). Taxable income is 57555.00 - 2275.00 = 55280.00.
    worksheet = return_ba(
        net_capital_losses_before_may_23_1985="2000",
        unapplied_net_capital_losses_1990_to_1999="0",
        net_capital_losses_claimed="1000",
    )

    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("1275.00")
    assert values(worksheet, COLUMN_C) == [
        D("1275.00"),
        D("0.00"),
        D("3000.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("4275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("4275.00")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("3275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("1275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("2275.00")
    assert values(worksheet, COLUMN_D) == [
        D("1275.00"),
        D("0.00"),
        D("1000.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, LEFT_AFTER) == [
        D("1000.00"),
        D("1000.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_E) == [
        D("0.00"),
        D("0.00"),
        D("2000.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_G) == [
        D("0.00"),
        D("0.00"),
        D("2666.67"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(TAXABLE_INCOME).value == D("55280.00")


def test_every_capital_gains_deduction_amount_lowers_line_3() -> None:
    # Line 1 is 6000 and the deductions are A 500, B 400 x 3/4 = 300.00, C 600 x 2/3 = 400.00, D
    # 300 x 1/(0.666666 x 2) = 225.00 and E 100: line 2 is 500 + 300.00 + 400.00 + 225.00 + 100 =
    # 1525.00 and line 3 is 4475.00. Column C is 4475.00, 0.00, 3000.00, 4000.00, 0.00 and 0.00,
    # so line 4 is 11475.00 and line 6 is 10000.00; a claim of 10000 leaves line 8 of 1475.00, the
    # least of line 3 (4475.00), line 8 and $2,000, so line 9 is 1475.00 and line 10 and line 13
    # are 11475.00. Column D is 4475.00 (7000.00 left), 0.00 (7000.00 left), 3000.00 (4000.00
    # left), 4000.00 (0.00 left), 0.00 and 0.00; nothing remains. Taxable income is 57555.00 -
    # 11475.00 = 46080.00.
    worksheet = return_ba(
        pre_1986_deductions_1988_and_1989="400",
        pre_1986_deductions_1990_to_1999="600",
        pre_1986_deductions_2001_to_2024="100",
    )

    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989).value == D("300.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999).value == D("400.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_2000).value == D("225.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_TOTAL).value == D("1525.00")
    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("4475.00")
    assert values(worksheet, COLUMN_C) == [
        D("4475.00"),
        D("0.00"),
        D("3000.00"),
        D("4000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("11475.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("10000.00")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("1475.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("1475.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("11475.00")
    assert values(worksheet, COLUMN_D) == [
        D("4475.00"),
        D("0.00"),
        D("3000.00"),
        D("4000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, LEFT_AFTER) == [
        D("7000.00"),
        D("7000.00"),
        D("4000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_G) == [D("0.00")] * 6
    assert worksheet.get(TAXABLE_INCOME).value == D("46080.00")


@pytest.mark.parametrize(
    ("amount", "ir", "adjusted"),
    [
        # IR 0.75 (3/4): 1/(0.75 x 2) = 2/3, so 300 x 2/3 = 200.00.
        ("300", "0.75", "200.00"),
        # IR 0.5: 1/(0.5 x 2) = 1, so 300 as it is.
        ("300", "0.5", "300.00"),
        # IR 0.6667: 300 / 1.3334 = 224.98875..., half-up 224.99.
        ("300", "0.6667", "224.99"),
        # No rate entered (0): the step yields 0 and the amount adds nothing to line 2.
        ("300", "0", "0.00"),
    ],
)
def test_amount_d_adds_to_line_2_over_twice_the_2000_inclusion_rate(
    amount: str, ir: str, adjusted: str
) -> None:
    # Line 2 is A 500 + D (the other amounts are 0): 500 + D; line 3 is 6000 less it.
    worksheet = return_ba(pre_1986_deductions_2000=amount, t657_inclusion_rate_2000=ir)

    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_2000).value == D(adjusted)
    assert worksheet.get(PRE_1986_DEDUCTIONS_TOTAL).value == D("500") + D(adjusted)
    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("5500") - D(adjusted)


def test_the_2000_is_taken_even_when_nothing_is_claimed_on_line_7() -> None:
    # A claim (line 7) of 0: line 8 is line 4, 12275.00, and line 9 is the least of 5275.00,
    # 12275.00 and $2,000, 2000, so line 10 and line 13 are 0 + 2000 = 2000. Column D, oldest
    # first, is 2000.00 (0.00 left), then 0.00 for each row; column E is 3275.00, 0.00, 3000.00,
    # 4000.00, 0.00 and 0.00 and column G (x 1, 1, 4/3, 3/2, 2 x IR, 1) is 3275.00, 0.00, 4000.00,
    # 6000.00, 0.00 and 0.00. Net income stays 57555.00 and taxable income is 57555.00 - 2000 =
    # 55555.00.
    worksheet = return_ba(net_capital_losses_claimed="0")

    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("0")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("12275.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("2000")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("2000")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("2000")
    assert values(worksheet, COLUMN_D) == [
        D("2000.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, LEFT_AFTER) == [D("0.00")] * 5
    assert values(worksheet, COLUMN_E) == [
        D("3275.00"),
        D("0.00"),
        D("3000.00"),
        D("4000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert values(worksheet, COLUMN_G) == [
        D("3275.00"),
        D("0.00"),
        D("4000.00"),
        D("6000.00"),
        D("0.00"),
        D("0.00"),
    ]
    assert worksheet.get(NET_INCOME).value == D("57555.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("55555.00")


def test_without_a_pre_1986_balance_line_9_is_zero() -> None:
    # Lines 1 to 3 not completed: line 3 is 0 (line 1 of 0 less line 2 of 0.00, 0.00), so column C
    # of the row "Before May 23, 1985" is 0.00 and line 9, the least of 0.00, line 8 and $2,000, is
    # 0. Losses of 3000 from 1990 to 1999 and 1000 from 2001 to 2024 (column C 2000.00 and
    # 1000.00) against taxable capital gains of 10000.00: line 4 is 3000.00 and line 6 is 3000.00;
    # a claim (line 7) of 2500 leaves line 8 of 500.00, and line 10 and line 13 are 2500 + 0 =
    # 2500. Column D is 0.00, 0.00, 0.00, 2000.00 and 500.00; column E is 500.00 for the last row
    # (1000.00 - 500.00). Taxable income is 57555.00 - 2500 = 55055.00.
    worksheet = return_ba(
        net_capital_losses_before_may_23_1985="0",
        pre_1986_deductions_before_1988="0",
        pre_1986_deductions_2000="0",
        unapplied_net_capital_losses_1988_and_1989="0",
        unapplied_net_capital_losses_1990_to_1999="3000",
        unapplied_net_capital_losses_2001_to_2024="1000",
        net_capital_losses_claimed="2500",
    )

    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("0.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985).value == D("0.00")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("3000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("3000.00")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("500.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("0")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("2500")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("2500")
    assert values(worksheet, COLUMN_D) == [
        D("0.00"),
        D("0.00"),
        D("0.00"),
        D("2000.00"),
        D("0.00"),
        D("500.00"),
    ]
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("500.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("55055.00")


@pytest.mark.parametrize("claim", ["10000.01", "12000"])
def test_a_claim_above_line_6_is_refused_the_extra_2000_is_not_part_of_line_7(claim: str) -> None:
    # Line 6 is the lesser of line 4 (12275.00) and line 5 (10000.00): 10000.00. Line 9 is not a
    # claim, so a claim of 12000 (line 7 plus line 9) is an input error.
    with pytest.raises(InputAboveBoundError) as raised:
        return_ba(net_capital_losses_claimed=claim)

    # The form T936 runs once before the return and holds its own copy of this check (Part 1 line 7
    # reads line 25300, and the copy of the check is in the form), so the instance named is ca/t936.
    assert str(raised.value) == (
        f"ca/t936, instance 1: ca/net_capital_losses_claimed {claim} is above "
        "ca/net_capital_losses_available_to_claim 10000.00"
    )


def test_the_pre_1986_balance_counts_in_line_4_and_so_in_line_6() -> None:
    # Without the pre-1986 balance line 4 is 3000.00 + 4000.00 = 7000.00 and a claim of 10000 is
    # above line 6 (7000.00); with it, line 4 is 12275.00 and line 6 is 10000.00.
    with pytest.raises(InputAboveBoundError) as raised:
        return_ba(
            net_capital_losses_before_may_23_1985="0",
            pre_1986_deductions_before_1988="0",
            pre_1986_deductions_2000="0",
        )

    # The form T936 runs once before the return and holds its own copy of this check (Part 1 line 7
    # reads line 25300, and the copy of the check is in the form), so the instance named is ca/t936.
    assert str(raised.value) == (
        "ca/t936, instance 1: ca/net_capital_losses_claimed 10000 is above "
        "ca/net_capital_losses_available_to_claim 7000.00"
    )
    assert return_ba().get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("10000.00")


def test_with_nothing_unapplied_and_nothing_claimed_nothing_is_deducted() -> None:
    # Nothing at all: every row of Chart A is 0.00 and the deduction is 0.
    worksheet = return_ba(
        net_capital_losses_before_may_23_1985="0",
        pre_1986_deductions_before_1988="0",
        pre_1986_deductions_2000="0",
        unapplied_net_capital_losses_1988_and_1989="0",
        unapplied_net_capital_losses_1990_to_1999="0",
        net_capital_losses_claimed="0",
    )

    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("0")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("0")
    assert values(worksheet, COLUMN_C) == [D("0.00")] * 6
    assert values(worksheet, COLUMN_G) == [D("0.00")] * 6
    assert worksheet.get(TAXABLE_INCOME).value == D("57555.00")
