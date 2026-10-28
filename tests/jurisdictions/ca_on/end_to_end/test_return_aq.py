"""CA-ON 2025 end to end: return aq."""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FEDERAL_BASIC_TAX,
    NET_FEDERAL_TAX,
    REFUND_OR_BALANCE_OWING,
    TAXABLE_INCOME,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER,
    NET_REFUND,
    ONTARIO_BASIC_TAX,
    ONTARIO_HEALTH_PREMIUM,
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
    UNUSED_TUITION_CARRIED_FORWARD,
    UNUSED_TUITION_CLAIMED,
    UNUSED_TUITION_INCOME_CAP,
    UNUSED_TUITION_ROOM,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_aq(unused_tuition_amounts_brought_forward: str = "60000") -> Worksheet:
    """Return AQ's inputs, as in `returns/2025_return_aq.yaml`: one employee, no other income.

    Employment income of 60000 (a chosen figure) is below the EI maximum insurable earnings
    ($65,700) and the CPP first earnings ceiling ($71,300). The caller's line 1 is the figure on the
    2024 notice of assessment: 60000 (a chosen figure) unless the test says otherwise.
    """
    return compute(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        unused_tuition_amounts_brought_forward=unused_tuition_amounts_brought_forward,
    )


def test_line_5_is_line_4_not_line_1_and_line_8_carries_the_rest_forward() -> None:
    # Schedule ON(S11) with line 1 at 60000. Line 2: the taxable income (line 26000) is 59435.00
    # (total income 60000.00 less the enhanced CPP contributions, the first additional of 1% x
    # (60000 - 3500) = 565.00, line 22215), which is more than 52886, so the Ontario tax on taxable
    # income (ON428 line 8) is divided by 5.05%. Line 8 is column 2 of the chart: line 4 is
    # 59435.00 - 52886 = 6549.00; line 6 is 6549.00 x 9.15% = 599.2335; line 7 is the printed
    # 2670.74; line 8 is 2670.74 + 599.2335 = 3269.9735, rounded half-up to 3269.97. So line 2 is
    # 3269.97 / 0.0505 = 3269.97 x 2000 / 101 = 64751.8812, rounded to 64751.88.
    # Line 3 (ON428 line 31): the basic personal amount 12747.00 + the base CPP contributions
    # 4.95% x 56500 = 2796.75 + the EI premiums 1.64% x 60000 = 984.00 = 16527.75.
    # Line 4: 64751.88 - 16527.75 = 48224.13. Line 5: the lesser of line 1 (60000.00) and line 4,
    # 48224.13, so the claim is 48224.13, which ON428 line 33 and line 58560 takes into line 35.
    # Line 8: 60000.00 - 48224.13 = 11775.87 carried forward.
    worksheet = return_aq()

    assert worksheet.get(ONTARIO_BASIC_TAX).value == D("3269.97")
    assert worksheet.get(UNUSED_TUITION_INCOME_CAP).value == D("64751.88")
    assert worksheet.get(CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER).value == D("16527.75")
    assert worksheet.get(UNUSED_TUITION_ROOM).value == D("48224.13")
    assert worksheet.get(UNUSED_TUITION_CLAIMED).value == D("48224.13")
    assert worksheet.get(UNUSED_TUITION_CARRIED_FORWARD).value == D("11775.87")


def test_the_claim_is_added_to_the_ontario_credits_and_takes_the_ontario_tax_to_zero() -> None:
    # ON428 line 35 and line 44 (line 58800): 16527.75 + 48224.13 = 64751.88 non-refundable credit
    # amounts. Line 46 (line 58840): 64751.88 x 5.05% = 3269.96994, rounded to 3269.97, which is
    # the Ontario non-refundable tax credits (line 50). So the Ontario tax after credits (line 58)
    # is 3269.97 - 3269.97 = 0.00, and no surtax (line 68) applies. The Ontario tax reduction
    # (line 80) is 2 x 294.00 = 588.00 less line 79, which is 0, but line 81 "Line 73 minus
    # line 80 (if negative, enter "0")" floors at 0. The LIFT credit (line 85) cannot take
    # line 86 "Line 84 minus line 85 (if negative, enter "0")" below 0 either.
    # The Ontario health premium (ON428 line 89) is read from its chart on taxable income: 59435.00
    # is more than $48,600 but not more than $72,000, so it is $600.00, and the Ontario tax (line
    # 90) is 0.00 + 600.00 = 600.00.
    # The federal net tax (line 42000, T1 line 42000) is not affected by the claim: basic tax 14.5%
    # x 57375 + 20.5% x (59435 - 57375) = 8319.375 + 422.30 = 8741.675, rounded half-up to 8741.68;
    # the credits are 16129 + 2796.75 + 984.00 + 1471 = 21380.75 at 14.5% = 3100.20875, rounded to
    # 3100.21; so the federal tax after credits is 8741.68 - 3100.21 = 5641.47.
    # Total payable (line 43500) is 5641.47 + 600.00 = 6241.47. With no income tax deducted and no
    # Canada workers benefit (the adjusted family net income is far above its maximum threshold),
    # the refund or balance owing is 6241.47, a balance owing, so there is no net refund.
    worksheet = return_aq()

    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("64751.88")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("3269.97")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("0.00")
    assert worksheet.get(ONTARIO_HEALTH_PREMIUM).value == D("600.00")
    assert worksheet.get(ONTARIO_TAX).value == D("600.00")
    assert worksheet.get(NET_REFUND).value == D("0")
    assert worksheet.get(TAXABLE_INCOME).value == D("59435.00")
    assert worksheet.get(FEDERAL_BASIC_TAX).value == D("8741.68")
    assert worksheet.get(NET_FEDERAL_TAX).value == D("5641.47")
    assert worksheet.get(TOTAL_PAYABLE).value == D("6241.47")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("6241.47")


def test_line_1_of_5000_claims_5000_and_carries_nothing_forward() -> None:
    # Line 1 at 5000 is below line 4 (48224.13), so line 5 is line 1: 5000.00, and line 8 is
    # 5000.00 - 5000.00 = 0.00. Lines 2 to 4 do not depend on line 1, so they are as above. The
    # claim adds 5000.00 to the credit amounts: 16527.75 + 5000.00 = 21527.75, at 5.05% it is
    # 1087.151375, rounded to 1087.15, and the Ontario tax after credits is 3269.97 - 1087.15 =
    # 2182.82. The tax reduction (line 80) is 588.00 - 2182.82, negative, so 0 and line 81 is
    # 2182.82. The health premium is 600.00, so the Ontario tax is 2182.82 + 600.00 = 2782.82. The
    # federal side is as in the test above (5641.47), so the total payable is 5641.47 + 2782.82 =
    # 8424.29, a balance owing of 8424.29.
    worksheet = return_aq("5000")

    assert worksheet.get(UNUSED_TUITION_CLAIMED).value == D("5000")
    assert worksheet.get(UNUSED_TUITION_CARRIED_FORWARD).value == D("0")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("2182.82")
    assert worksheet.get(ONTARIO_TAX).value == D("2782.82")
    assert worksheet.get(TOTAL_PAYABLE).value == D("8424.29")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("8424.29")
