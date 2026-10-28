"""CA-ON 2025 end to end: return ax."""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.ei_excluded_slips_net_income import (
    EiExcludedSlipsNetIncome,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_EARNINGS_SUBJECT_TO_PREMIUM,
    EI_EXCLUDED_SLIPS_NET_INCOME,
    EI_INSURABLE_EARNINGS_REMAINING,
    EI_NET_SELF_EMPLOYMENT_INCOME,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_PREMIUMS_ON_SELF_EMPLOYMENT,
    EI_SELF_EMPLOYMENT_BEFORE_SLIPS,
    EI_SELF_EMPLOYMENT_EARNINGS,
    NET_SELF_EMPLOYMENT_INCOME,
    PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS,
    SELF_EMPLOYED_EI_PREMIUMS,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Return AX's inputs beyond the all-zero ones `compute` defaults: Return U's net business income
# (T1 line 13500, now T2125 line 9946) of 50000, entered as T2125 gross sales (amount 3A) of
# 50000 with no expenses, which is all of total income (line 15000, through line 27); Schedule 8
# Part 4 completed and the agreement for EI special benefits, each a count of 1; and one T4 slip
# for self-employment income with EI premiums in box 18 that reports 20000 of that net income.
RETURN_AX: dict[str, Any] = {
    "business_income": "50000",
    "cpp_part_4_completed": 1,
    "ei_special_benefits_agreement": 1,
    "ei_excluded_slips": ("20000",),
}


def business_statement(business_income: str) -> dict[str, str]:
    """A T2125 whose line 9946, and so T1 line 13500, is `business_income`: all gross sales (amount
    3A) for income, all advertising (amount 4B) for a loss."""
    amount = D(business_income)
    if amount >= 0:
        return {"gross_sales": business_income}
    return {"advertising": str(-amount)}


def return_ax(**changes: Any) -> Worksheet:
    """Return AX's inputs, as in `returns/2025_return_ax.yaml`, with `changes` to them;
    `business_income` is the net business income the T2125 is entered to give."""
    inputs = {**RETURN_AX, **changes}
    business = business_statement(inputs.pop("business_income"))
    return compute(
        "0", (), "0", "0", "0", "0", "0", business_statements=({"business": business},), **inputs
    )


def test_return_axs_schedule_13_line_1_leaves_out_the_slips_net_income() -> None:
    # Line 1 is line 12200 (0) plus line 27 (50000), less the 20000 reported for the slip: 30000.
    worksheet = return_ax()

    assert worksheet.get(NET_SELF_EMPLOYMENT_INCOME).value == D("50000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_BEFORE_SLIPS).value == D("50000")
    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("20000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("30000.00")
    assert isinstance(worksheet.producer_of(EI_SELF_EMPLOYMENT_BEFORE_SLIPS), Sum)
    assert isinstance(worksheet.producer_of(EI_EXCLUDED_SLIPS_NET_INCOME), EiExcludedSlipsNetIncome)
    assert isinstance(worksheet.producer_of(EI_SELF_EMPLOYMENT_EARNINGS), SubtractNotBelowZero)


def test_return_axs_line_9_is_492_00() -> None:
    # Line 4 is 30000 + 0 + 0, line 7 is 65700.00 - 0, line 8 is the lesser of 30000 and
    # 65700.00 and line 9 is 30000 x 1.64% = 492.00, lines 31217 and 42120.
    worksheet = return_ax()

    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("30000")
    assert worksheet.get(EI_INSURABLE_EARNINGS_REMAINING).value == D("65700.00")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("30000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("492.00")
    assert worksheet.get(EI_PREMIUMS_ON_SELF_EMPLOYMENT).value == D("492.00")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("492.00")


def test_return_axs_slip_does_not_change_schedule_8_part_4() -> None:
    # Schedule 8 Part 4 line 1 is line 12200 plus line 27 and does not leave the slip out.
    worksheet = return_ax()

    assert worksheet.get(PENSIONABLE_NET_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT).value == D("5533.50")


def test_return_axs_total_payable_reads_the_premiums_of_492_00() -> None:
    # 4037.60 net federal tax + 2026.99 Ontario tax + 5533.50 CPP + 492.00 EI.
    assert return_ax().get(TOTAL_PAYABLE).value == D("12090.09")


def test_return_axs_trace_shows_the_slip_and_the_subtraction() -> None:
    rendered = EnglishTraceRenderer().render_all(return_ax().trace)

    for line in (
        "ei_self_employment_before_slips: net_partnership_income 0 "
        "+ net_self_employment_income 50000 = 50000",
        "ei_excluded_slips_net_income: item 1 ei_excluded_slip_net_income 20000 = 20000",
        "ei_self_employment_earnings: ei_self_employment_before_slips 50000 "
        "less ei_excluded_slips_net_income 20000, not below 0 = 30000",
        "self_employed_ei_premiums: 1.64% of ei_earnings_subject_to_premium between 0 and 65700 "
        "(30000), at most 1077.48 (half-up to 0.01)",
    ):
        assert line in rendered, line


def test_no_slips_leave_line_1_at_the_total_of_line_12200_and_line_27() -> None:
    worksheet = return_ax(ei_excluded_slips=())

    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("0")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("50000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("820.00")
    assert "ei_excluded_slips_net_income: no items = 0" in EnglishTraceRenderer().render_all(
        worksheet.trace
    )


def test_several_slips_are_each_left_out() -> None:
    # 20000 + 5000 = 25000 off 50000: line 1 is 25000 and line 9 is 25000 x 1.64% = 410.00.
    worksheet = return_ax(ei_excluded_slips=("20000", "5000"))

    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("25000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("25000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("410.00")


def test_slips_that_exceed_line_1_floor_it_at_0() -> None:
    # Slips reporting 60000 against a line 1 of 50000 (for example net income on lines 13700 to
    # 14300 that the line 12200 plus line 27 total also carries): "if negative, enter "0"", so line
    # 1 is 0, line 4 is 0, line 8 is 0 and line 9 is 0.
    worksheet = return_ax(ei_excluded_slips=("60000",))

    assert worksheet.get(EI_SELF_EMPLOYMENT_BEFORE_SLIPS).value == D("50000")
    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("60000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("0")
    assert worksheet.get(EI_NET_SELF_EMPLOYMENT_INCOME).value == D("0")
    assert worksheet.get(EI_EARNINGS_SUBJECT_TO_PREMIUM).value == D("0")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("0")
    assert worksheet.get(EI_PAYABLE_ON_SELF_EMPLOYMENT).value == D("0")


def test_a_slip_with_a_net_loss_adds_to_line_1() -> None:
    # "do not include any net income (or net loss)": a slip reporting a net loss of 5000 is
    # taken out of line 1 too, so line 1 is 50000 - (20000 - 5000) = 35000 and line 9 is
    # 35000 x 1.64% = 574.00.
    worksheet = return_ax(ei_excluded_slips=("20000", "-5000"))

    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("15000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("35000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("574.00")


def test_a_net_loss_slip_alone_raises_line_1_above_the_total_of_line_12200_and_line_27() -> None:
    worksheet = return_ax(ei_excluded_slips=("-5000",))

    assert worksheet.get(EI_EXCLUDED_SLIPS_NET_INCOME).value == D("-5000")
    assert worksheet.get(EI_SELF_EMPLOYMENT_EARNINGS).value == D("55000")
    assert worksheet.get(SELF_EMPLOYED_EI_PREMIUMS).value == D("902.00")
