"""CA-ON 2025 end to end: return af."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADJUSTED_FAMILY_NET_INCOME,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
    ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987,
    ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989,
    ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999,
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    DEDUCTIONS_FROM_NET_INCOME,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
    NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION,
    NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM,
    NET_CAPITAL_LOSSES_OF_OTHER_YEARS,
    NET_INCOME,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    SCHEDULE_3_LINE_19900,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    LIFT_CREDIT,
    ONTARIO_TAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, Disposition, compute


def return_af(
    share_dispositions: tuple[Disposition, ...] = (("5000", "0", "0"),), **overrides: Any
) -> Worksheet:
    """Return AF's inputs, as in `returns/2025_return_af.yaml`: Return AE's filer, no political
    contributions, with a capital gain (one share row, proceeds 5000, a chosen figure) and
    unapplied net capital losses of other years.

    Employment income of 48000, a capital gain of 5000 (taxable capital gains of 2500.00),
    4800 deducted, unapplied net capital losses of 3000 from 1990 to 1999 and 1000 from 2001 to
    2024 (Form T1436 Chart A column A), and an amount claimed (line 7) of 2500.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "4800",
        "unapplied_net_capital_losses_1990_to_1999": "3000",
        "unapplied_net_capital_losses_2001_to_2024": "1000",
        "net_capital_losses_claimed": "2500",
    }
    return compute(
        "48000", share_dispositions, "0", "0", "8640", "0", "0", **{**inputs, **overrides}
    )


def test_a_share_loss_is_shown_on_schedule_3_line_26_and_not_on_line_12700() -> None:
    # Schedule 3 line 26 (box 19900) "Total taxable capital gains or net capital losses": shares
    # sold for 1000 with an adjusted cost base of 5000 are a loss of 4000 (line 21), line 24 is
    # -4000 x 50% = -2000.00 and line 25 is 0, so line 26 is -2000.00, the year's net capital
    # loss. T1 line 12700 is "If positive", so 0 ("Do not report your net capital loss for 2025 on
    # line 12700"): the loss is carried forward (or back, Form T1A), not used against this return.
    worksheet = return_af(
        share_dispositions=(("1000", "5000", "0"),), net_capital_losses_claimed="0"
    )

    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("-2000.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0")


def test_return_afs_line_26_is_line_12700_when_the_year_has_a_gain() -> None:
    worksheet = return_af()

    assert worksheet.get(SCHEDULE_3_LINE_19900).value == D("2500.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("2500.00")


def test_return_afs_claim_is_applied_to_the_oldest_row_first_and_lowers_taxable_income() -> None:
    # Form T1436 Chart A: a 1995 loss of 3000 (row "After 1989 and before 2000", column B 2/3) gives
    # column C 3000 x 2/3 = 2000.00; a 2010 loss of 1000 (row "After 2000 and before 2025", column B
    # 1) gives 1000 x 1 = 1000.00; the other two rows have no loss: 0.00. Line 4 is 3000.00 and line
    # 5, the taxable capital gains (line 12700), is 5000 x 50% = 2500.00, so line 6 is 2500.00. The
    # claim of 2500 (line 7) is at most line 6; line 8 is 3000.00 - 2500 = 500.00 and line 9, the
    # lesser of line 3 (0, lines 1 to 3 not completed), line 8 and $2,000, is 0, so line 10, T1 line
    # 25300, and line 13 are 2500 + 0 = 2500. It is applied oldest row first: column D is 0.00
    # for each of the first two rows, 2000.00 for the 1990 to 1999 row (of the 2500 left, 500.00
    # remains) and 500.00 for the 2001 to 2024 row.
    # Column E is column C less column D: 0.00, 0.00, 0.00 and 500.00; column G is column E x
    # column F (1, 4/3, 3/2 and 1): 0.00, 0.00, 0.00 and 500.00. Net income is 50500.00 - 445.00 =
    # 50055.00 (the deduction is below net income); line 25700 is 2500 and taxable income is
    # 47555.00. The LIFT credit's reduction is 5% x (50055.00 - 32500) = 877.75, more than 875, so
    # the credit is 0; the Ontario tax is 1606.81 + 450 = 2056.81 and the total payable is
    # 3909.94 + 2056.81 = 5966.75, against total credits of 4800.00: 1166.75 owing.
    worksheet = return_af()

    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("2500.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987).value == D("0.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989).value == D("0.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999).value == D("2000.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024).value == D("1000.00")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("3000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("2500.00")
    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("2500")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("500.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("0")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("2500")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("2500")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1985_TO_1987).value == D("0.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987).value == D("2500.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1988_AND_1989).value == D("0.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989).value == D("2500.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1990_TO_1999).value == D("2000.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999).value == D("500.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("500.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1985_TO_1987).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1988_AND_1989).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1990_TO_1999).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("500.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1985_TO_1987).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1988_AND_1989).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1990_TO_1999).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("500.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("2500")
    assert worksheet.get(NET_INCOME).value == D("50055.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("47555.00")
    assert worksheet.get(LIFT_CREDIT).value == D("0")
    assert worksheet.get(ONTARIO_TAX).value == D("2056.81")
    assert worksheet.get(TOTAL_PAYABLE).value == D("5966.75")
    assert worksheet.get(TOTAL_CREDITS).value == D("4800.00")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("1166.75")
    assert worksheet.get(REFUND).value == D("0")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "adjusted_gross_capital_losses_1990_to_1999: 2/3 of "
        "unapplied_net_capital_losses_1990_to_1999 3000 (half-up to 0.01)"
    ) in rendered
    assert (
        "adjusted_gross_capital_losses_2001_to_2024: 1/1 of "
        "unapplied_net_capital_losses_2001_to_2024 1000 (half-up to 0.01)"
    ) in rendered
    assert (
        "total_adjusted_net_capital_losses: adjusted_gross_capital_losses_before_may_23_1985 0 "
        "+ adjusted_gross_capital_losses_1985_to_1987 0 "
        "+ adjusted_gross_capital_losses_1988_and_1989 0 "
        "+ adjusted_gross_capital_losses_1990_to_1999 2000 "
        "+ adjusted_gross_capital_losses_2000 0 "
        "+ adjusted_gross_capital_losses_2001_to_2024 1000 = 3000"
    ) in rendered
    assert (
        "net_capital_losses_available_to_claim: lesser of total_adjusted_net_capital_losses 3000 "
        "and taxable_capital_gains 2500 = 2500"
    ) in rendered
    assert (
        "adjusted_net_capital_losses_applied: net_capital_losses_claimed 2500, "
        "at most net_capital_losses_available_to_claim 2500"
    ) in rendered
    assert (
        "unapplied_adjusted_net_capital_losses: total_adjusted_net_capital_losses 3000 "
        "less adjusted_net_capital_losses_applied 2500 = 500"
    ) in rendered
    assert (
        "net_capital_losses_additional_deduction: lesser of pre_1986_capital_loss_balance 0 "
        "and unapplied_adjusted_net_capital_losses 500 and 2000 (half-up to 0.01) = 0"
    ) in rendered
    assert (
        "net_capital_losses_of_other_years: adjusted_net_capital_losses_applied 2500 "
        "+ net_capital_losses_additional_deduction 0 = 2500"
    ) in rendered
    assert (
        "adjusted_losses_applied_1990_to_1999: lesser of "
        "adjusted_gross_capital_losses_1990_to_1999 2000 "
        "and adjusted_losses_left_after_1988_and_1989 2500 = 2000"
    ) in rendered
    assert (
        "adjusted_losses_applied_1985_to_1987: lesser of "
        "adjusted_gross_capital_losses_1985_to_1987 0 "
        "and adjusted_losses_left_after_before_may_23_1985 2500 = 0"
    ) in rendered
    assert (
        "adjusted_losses_left_after_1990_to_1999: adjusted_losses_left_after_1988_and_1989 2500 "
        "less adjusted_losses_applied_1990_to_1999 2000 = 500"
    ) in rendered
    assert (
        "adjusted_losses_applied_2001_to_2024: lesser of "
        "adjusted_gross_capital_losses_2001_to_2024 1000 "
        "and adjusted_losses_left_after_2000 500 = 500"
    ) in rendered
    assert (
        "remaining_adjusted_losses_2001_to_2024: adjusted_gross_capital_losses_2001_to_2024 1000 "
        "less adjusted_losses_applied_2001_to_2024 500 = 500"
    ) in rendered
    assert (
        "net_capital_loss_balance_2001_to_2024: 1/1 of remaining_adjusted_losses_2001_to_2024 500 "
        "(half-up to 0.01)"
    ) in rendered
    assert (
        "deductions_from_net_income: canadian_armed_forces_and_police_deduction 0 "
        "+ security_options_deductions 0 + other_payments_deduction 0 "
        "+ limited_partnership_losses_of_other_years_checked 0 "
        "+ non_capital_losses_on_line_25200 0 "
        "+ net_capital_losses_of_other_years 2500 + qbt_capital_gains_deduction 0 "
        "+ capital_gains_deduction 0 + northern_residents_deductions 0 "
        "+ additional_deductions_total 0 = 2500"
    ) in rendered
    assert (
        "taxable_income: net_income 50055 less deductions_from_net_income 2500, not below 0 = 47555"
    ) in rendered


def test_the_claim_lowers_taxable_income_and_leaves_net_income() -> None:
    # Guide T4037: applying a net capital loss of another year "will not change" net income, which
    # is used to calculate certain credits and benefits; it reduces taxable income only.
    claimed = return_af()
    unclaimed = return_af(net_capital_losses_claimed="0")

    assert claimed.get(NET_INCOME).value == D("50055.00")
    assert unclaimed.get(NET_INCOME).value == D("50055.00")
    assert claimed.get(ADJUSTED_FAMILY_NET_INCOME).value == D("50055.00")
    assert claimed.get(TAXABLE_INCOME).value == D("47555.00")
    assert unclaimed.get(TAXABLE_INCOME).value == D("50055.00")
    assert unclaimed.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")


def test_a_claim_above_the_lesser_of_the_losses_and_the_taxable_gains_is_refused() -> None:
    # Form T1436 line 7, note (3): "You can apply all or part of the amount from line 6": line 6 is
    # 2500.00 (the taxable capital gains, below the 3000.00 of losses), so 2500.01 is an input
    # error, not capped to 2500.00.
    with pytest.raises(InputAboveBoundError) as raised:
        return_af(net_capital_losses_claimed="2500.01")

    # The form T936 runs once before the return and holds its own copy of this check (Part 1 line 7
    # reads line 25300, and the copy of the check is in the form), so the instance named is ca/t936.
    assert str(raised.value) == (
        "ca/t936, instance 1: ca/net_capital_losses_claimed 2500.01 is above "
        "ca/net_capital_losses_available_to_claim 2500.00"
    )


def test_a_claim_with_no_taxable_capital_gains_is_refused_naming_both_kinds() -> None:
    # No capital gain: line 5 is 0.00, so line 6 is 0.00 whatever the losses, and a claim of 1 is
    # above it.
    with pytest.raises(InputAboveBoundError) as raised:
        compute(
            "48000",
            (),
            "0",
            "0",
            "8640",
            "0",
            "0",
            unapplied_net_capital_losses_2001_to_2024="1000",
            net_capital_losses_claimed="1",
        )

    # The form T936 runs once before the return and holds its own copy of this check (Part 1 line 7
    # reads line 25300, and the copy of the check is in the form), so the instance named is ca/t936.
    assert str(raised.value) == (
        "ca/t936, instance 1: "
        "ca/net_capital_losses_claimed 1 is above ca/net_capital_losses_available_to_claim 0"
    )


def test_a_claim_of_zero_with_no_taxable_capital_gains_is_allowed() -> None:
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        unapplied_net_capital_losses_2001_to_2024="1000",
    )

    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("0")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("1000.00")


def test_line_6_is_the_taxable_capital_gains_when_the_losses_are_larger() -> None:
    # Losses of 10000 from 2001 to 2024 (column C 10000.00) against taxable capital gains of
    # 2500.00: line 6 is 2500.00 and a claim of 2500 leaves 7500.00 for next year.
    worksheet = return_af(
        unapplied_net_capital_losses_1990_to_1999="0",
        unapplied_net_capital_losses_2001_to_2024="10000",
    )

    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("10000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("2500.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("2500.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("7500.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("7500.00")
    with pytest.raises(InputAboveBoundError):
        return_af(
            unapplied_net_capital_losses_1990_to_1999="0",
            unapplied_net_capital_losses_2001_to_2024="10000",
            net_capital_losses_claimed="2500.01",
        )


def test_line_6_is_the_total_of_column_c_when_the_taxable_gains_are_larger() -> None:
    # A capital gain of 20000 (taxable capital gains of 10000.00) against column C of 3000.00: line
    # 6 is 3000.00, the whole of both rows is applied and nothing is left to carry forward.
    worksheet = return_af(
        share_dispositions=(("20000", "0", "0"),), net_capital_losses_claimed="3000"
    )

    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("10000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("3000.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("3000")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1990_TO_1999).value == D("2000.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("1000.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1990_TO_1999).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("0.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("3000")


def test_a_partial_claim_uses_the_oldest_row_first_and_carries_the_rest_forward() -> None:
    # A claim of 1000 against column C of 2000.00 (1990 to 1999) and 1000.00 (2001 to 2024): all
    # of it comes off the older row, column D 1000.00 and 0.00; column E is 1000.00 for each;
    # column G is 1000.00 x 3/2 = 1500.00 for the older row and 1000.00 x 1 = 1000.00.
    worksheet = return_af(net_capital_losses_claimed="1000")

    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1990_TO_1999).value == D("1000.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999).value == D("0.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1990_TO_1999).value == D("1000.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("1000.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1990_TO_1999).value == D("1500.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("1000.00")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("1000")


def test_no_claim_keeps_every_loss_and_gives_back_the_unapplied_amounts() -> None:
    # Nothing claimed: column D is 0.00 everywhere, column E is column C, and column G is column E x
    # column F: 2000.00 x 3/2 = 3000.00 and 1000.00 x 1, the unapplied losses of column A again.
    worksheet = return_af(net_capital_losses_claimed="0")

    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("0")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_1990_TO_1999).value == D("0.00")
    assert worksheet.get(ADJUSTED_LOSSES_APPLIED_2001_TO_2024).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1990_TO_1999).value == D("2000.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1990_TO_1999).value == D("3000.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("1000.00")


def test_all_four_rows_are_applied_oldest_first_and_column_d_adds_up_to_line_13() -> None:
    # Column A: 100, 400, 600 and 500. Column C (x 1, 3/4, 2/3, 1): 100.00, 300.00, 400.00 and
    # 500.00; line 4 is 1300.00, below the taxable capital gains of 2500.00, so line 6 is 1300.00. A
    # claim of 700: column D is 100.00, 300.00, 300.00 and 0.00 (700 left, then 600.00, 300.00 and
    # 0.00 left after each of the first three), which add up to 700, line 13. Column E is 0.00,
    # 0.00, 100.00 and 500.00; column G (x 1, 4/3, 3/2 and 1) is 0.00, 0.00, 150.00 and 500.00.
    worksheet = return_af(
        unapplied_net_capital_losses_1985_to_1987="100",
        unapplied_net_capital_losses_1988_and_1989="400",
        unapplied_net_capital_losses_1990_to_1999="600",
        unapplied_net_capital_losses_2001_to_2024="500",
        net_capital_losses_claimed="700",
    )

    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987).value == D("100.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989).value == D("300.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999).value == D("400.00")
    assert worksheet.get(ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024).value == D("500.00")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("1300.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("1300.00")
    applied = [
        worksheet.get(kind).value
        for kind in (
            ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
            ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
            ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
            ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
        )
    ]
    assert applied == [D("100.00"), D("300.00"), D("300.00"), D("0.00")]
    assert sum(applied) == worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("700")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1985_TO_1987).value == D("600.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1988_AND_1989).value == D("300.00")
    assert worksheet.get(ADJUSTED_LOSSES_LEFT_AFTER_1990_TO_1999).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1985_TO_1987).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1988_AND_1989).value == D("0.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_1990_TO_1999).value == D("100.00")
    assert worksheet.get(REMAINING_ADJUSTED_LOSSES_2001_TO_2024).value == D("500.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1985_TO_1987).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1988_AND_1989).value == D("0.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_1990_TO_1999).value == D("150.00")
    assert worksheet.get(NET_CAPITAL_LOSS_BALANCE_2001_TO_2024).value == D("500.00")


@pytest.mark.parametrize(
    ("row", "loss", "adjusted", "balance"),
    [
        # The form prints 0.75 and 1.33, whose product is 0.9975; the exact fractions 3/4 and 4/3
        # give the loss back: 900 x 3/4 = 675.00 and 675.00 x 4/3 = 900.00.
        ("1988_and_1989", "900", "675.00", "900.00"),
        # The form prints 0.6667 and 1.5; the exact fractions 2/3 and 3/2: 900 x 2/3 = 600.00 and
        # 600.00 x 3/2 = 900.00.
        ("1990_to_1999", "900", "600.00", "900.00"),
        # Half-up to the cent at column C: 0.02 x 3/4 = 0.015 is 0.02, and at column G: 0.02 x 4/3
        # = 0.02666... is 0.03.
        ("1988_and_1989", "0.02", "0.02", "0.03"),
        # 1.01 x 2/3 = 0.67333... is 0.67 (not carried unrounded to column G); 0.67 x 3/2 = 1.005
        # is 1.01.
        ("1990_to_1999", "1.01", "0.67", "1.01"),
        # Factors of 1 change nothing: 1234.56 x 1.
        ("1985_to_1987", "1234.56", "1234.56", "1234.56"),
        ("2001_to_2024", "1234.56", "1234.56", "1234.56"),
    ],
)
def test_columns_c_and_g_use_the_exact_fractions_rounded_half_up_to_the_cent(
    row: str, loss: str, adjusted: str, balance: str
) -> None:
    kinds = {
        "1985_to_1987": (
            ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
            NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
        ),
        "1988_and_1989": (
            ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
            NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
        ),
        "1990_to_1999": (
            ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
            NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
        ),
        "2001_to_2024": (
            ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
            NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
        ),
    }
    column_c, column_g = kinds[row]
    losses: dict[str, Any] = {f"unapplied_net_capital_losses_{row}": loss}
    worksheet = compute("48000", (("20000", "0", "0"),), "0", "0", "8640", "0", "0", **losses)

    assert worksheet.get(column_c).value == D(adjusted)
    assert worksheet.get(column_g).value == D(balance)
