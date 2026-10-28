"""CA-ON 2025 end to end: return fg."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMOUNTS_TRANSFERRED_FROM_SPOUSE,
    CREDIT_AMOUNTS_AT_CREDIT_RATE,
    FEDERAL_TAX_AFTER_CREDITS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND_OR_BALANCE_OWING,
    SPOUSE_ADJUSTED_TAXABLE_INCOME,
    SPOUSE_CREDITS_USED,
    SPOUSE_INCOME_FOR_TRANSFER,
    SPOUSE_TRANSFERABLE_AMOUNTS,
    SPOUSE_UNUSED_AMOUNTS,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_fg(**overrides: Any) -> Worksheet:
    """Return FG's inputs, as in `returns/2025_return_fg.yaml`.

    The filer is a 2025 Ontario resident with employment income of 40000 and income tax deducted
    of 5000, not separated from the spouse for 90 days or more including December 31, 2025; the
    filer has no tuition. The spouse's age amount is 9028, their designated tuition to the filer
    4000, their taxable income 18000, their line 30000 16129 and their federal tuition amount 800.
    On their Form ON428 the spouse's line 58080 is 6223, line 58040 12747 and line 58560 (the
    unused tuition amount they claimed) 600; their line 96 and line 24 are 0 (Schedule ON(S2)).
    """
    inputs: dict[str, Any] = {
        "employment_income": "40000",
        "share_dispositions": (),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "income_tax_deducted": "5000",
        "spouse_return_age_amount": "9028",
        "spouse_designated_tuition": "4000",
        "spouse_return_taxable_income": "18000",
        "spouse_return_basic_personal_amount": "16129",
        "spouse_return_federal_tuition_amount": "800",
        "spouse_not_separated_90_days": 1,
        "spouse_return_ontario_age_amount": "6223",
        "spouse_return_ontario_basic_personal_amount": "12747",
        "spouse_return_ontario_unused_tuition_amount": "600",
    }
    return compute(**{**inputs, **overrides})


def test_the_spouses_federal_amounts_on_schedule_2_are_11957_for_the_filer() -> None:
    # Schedule 2. Line 6 is 9028 + 0 + 0 + 0 + 4000 = 13028.00; their taxable income of 18000 is
    # at or below 57375, so line 7 is 18000.00; line 11 is 16129 + 0 + 800 = 16929.00; line 12 is
    # 18000.00 - 16929.00 = 1071.00 and line 13 is 13028.00 - 1071.00 = 11957.00; not separated,
    # line 32600 is 11957.00 x 1 = 11957.00.
    worksheet = return_fg()

    assert worksheet.get(SPOUSE_TRANSFERABLE_AMOUNTS).value == D("13028.00")
    assert worksheet.get(SPOUSE_INCOME_FOR_TRANSFER).value == D("18000.00")
    assert worksheet.get(SPOUSE_CREDITS_USED).value == D("16929.00")
    assert worksheet.get(SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("1071.00")
    assert worksheet.get(SPOUSE_UNUSED_AMOUNTS).value == D("11957.00")
    assert worksheet.get(AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("11957.00")


def test_the_spouses_ontario_amounts_on_schedule_on_s2_are_1570_on_line_58640() -> None:
    # Schedule ON(S2). Line 4 is 6223 + 0 + 0 = 6223.00; their taxable income of 18000 is at or
    # below 52886, so line 5 is 18000.00; line 9 is 12747 + 0 + 600 = 13347.00; line 10 is
    # 18000.00 - 13347.00 = 4653.00 and line 11 is 6223.00 - 4653.00 = 1570.00; not separated,
    # ON428 line 34 and line 58640 is 1570.00 x 1 = 1570.00.
    worksheet = return_fg()

    assert worksheet.get(ontario.SPOUSE_TRANSFERABLE_AMOUNTS).value == D("6223.00")
    assert worksheet.get(ontario.SPOUSE_INCOME_FOR_TRANSFER).value == D("18000.00")
    assert worksheet.get(ontario.SPOUSE_CREDITS_USED).value == D("13347.00")
    assert worksheet.get(ontario.SPOUSE_ADJUSTED_TAXABLE_INCOME).value == D("4653.00")
    assert worksheet.get(ontario.SPOUSE_UNUSED_AMOUNTS).value == D("1570.00")
    assert worksheet.get(ontario.AMOUNTS_TRANSFERRED_FROM_SPOUSE).value == D("1570.00")


def test_the_credit_amounts_on_line_33500_include_the_spouses_11957() -> None:
    # Line 33500 is 20062.75 (T1 line 101, 16129.00 + 1806.75 + 656.00 + 1471.00) + 11957.00 =
    # 32019.75, and line 33800 is 32019.75 x 14.5% = 4642.86375, half-up to the cent: 4642.86.
    # The federal tax on 39635.00 is 39635.00 x 14.5% = 5747.075, half-up to 5747.08, so the
    # federal tax after credits is 5747.08 - 4642.86 = 1104.22.
    worksheet = return_fg()

    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("32019.75")
    assert worksheet.get(CREDIT_AMOUNTS_AT_CREDIT_RATE).value == D("4642.86")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("1104.22")


def test_the_refund_is_2809_84_once_the_ontario_spouse_amount_is_in_the_credits() -> None:
    # The Ontario tax after credits is 2001.57 - 847.38 = 1154.19, where 847.38 is 16779.75
    # (ON428 line 44: 12747 + 1806.75 + 656.00 + 1570.00) x 5.05%, rounded half-up. The LIFT credit
    # 518.25 leaves 635.94 and the health premium 450 gives an Ontario tax of 1085.94. The total
    # payable is 1104.22 + 1085.94 = 2190.16 and the refund or balance owing is 2190.16 - 5000 =
    # -2809.84, a refund of 2809.84.
    worksheet = return_fg()

    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2809.84")
