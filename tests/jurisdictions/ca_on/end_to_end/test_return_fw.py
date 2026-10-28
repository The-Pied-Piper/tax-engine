"""CA-ON 2025 end to end: return FW, the social benefits chart floored at 0 and pre-1986 balance.

Return FW is `returns/2025_return_fw.yaml`: an Ontario filer with OAS of 4000, EI benefits of 20000,
RDSP income of 100000 and a capital gain of 20000 (taxable capital gains of 10000). The OAS
overpayment recovered (5000) is above the OAS pension (line 3), so line 5 is floored at 0. The RDSP
income makes line 11 negative (-6000), so line 17 is floored at 0 and line 19 is 0; no EI repayment
arises, so line 21 and the repayment are 0. The Form T1436 balance from before May 23, 1985 (9000)
and the capital gains deductions claimed before 1988, in 1988 and 1989, from 1990 to 1999 and from
2001 to 2024 are non-zero, and so is the 1985 to 1987 row of Chart A. The figures are chosen and
worked out by hand from the form text, as no CRA example exists for these charts. The tests check
the hand figure of each line; the tax figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

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
    ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    DEDUCTIONS_FROM_NET_INCOME,
    DEDUCTIONS_FROM_TOTAL_INCOME,
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
    NET_INCOME_BEFORE_ADJUSTMENTS,
    OAS_AND_FEDERAL_SUPPLEMENTS,
    OAS_BENEFITS_BASE_AMOUNT,
    PRE_1986_CAPITAL_LOSS_BALANCE,
    PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989,
    PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999,
    PRE_1986_DEDUCTIONS_ADJUSTED_2000,
    PRE_1986_DEDUCTIONS_TOTAL,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    SHARE_PROCEEDS,
    SOCIAL_BENEFITS_LINE_5,
    SOCIAL_BENEFITS_LINE_6,
    SOCIAL_BENEFITS_LINE_10,
    SOCIAL_BENEFITS_LINE_11,
    SOCIAL_BENEFITS_LINE_14,
    SOCIAL_BENEFITS_LINE_15,
    SOCIAL_BENEFITS_LINE_17,
    SOCIAL_BENEFITS_LINE_18,
    SOCIAL_BENEFITS_LINE_19,
    SOCIAL_BENEFITS_LINE_21,
    SOCIAL_BENEFITS_REPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_APPLIES,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES,
    TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED,
    TOTAL_INCOME,
    UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute

# Chart A rows, from "Before May 23, 1985" to "After 2000 and before 2025".
# Column C: adjusted gross capital losses (column A times column B).
COLUMN_C = (
    ADJUSTED_GROSS_CAPITAL_LOSSES_BEFORE_MAY_23_1985,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1985_TO_1987,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1988_AND_1989,
    ADJUSTED_GROSS_CAPITAL_LOSSES_1990_TO_1999,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2000,
    ADJUSTED_GROSS_CAPITAL_LOSSES_2001_TO_2024,
)
# Column D: losses applied from line 13, oldest row first.
COLUMN_D = (
    ADJUSTED_LOSSES_APPLIED_BEFORE_MAY_23_1985,
    ADJUSTED_LOSSES_APPLIED_1985_TO_1987,
    ADJUSTED_LOSSES_APPLIED_1988_AND_1989,
    ADJUSTED_LOSSES_APPLIED_1990_TO_1999,
    ADJUSTED_LOSSES_APPLIED_2000,
    ADJUSTED_LOSSES_APPLIED_2001_TO_2024,
)
# Column E: column C less column D.
COLUMN_E = (
    REMAINING_ADJUSTED_LOSSES_BEFORE_MAY_23_1985,
    REMAINING_ADJUSTED_LOSSES_1985_TO_1987,
    REMAINING_ADJUSTED_LOSSES_1988_AND_1989,
    REMAINING_ADJUSTED_LOSSES_1990_TO_1999,
    REMAINING_ADJUSTED_LOSSES_2000,
    REMAINING_ADJUSTED_LOSSES_2001_TO_2024,
)
# Column G: column E times column F, the net capital loss balance carried forward.
COLUMN_G = (
    NET_CAPITAL_LOSS_BALANCE_BEFORE_MAY_23_1985,
    NET_CAPITAL_LOSS_BALANCE_1985_TO_1987,
    NET_CAPITAL_LOSS_BALANCE_1988_AND_1989,
    NET_CAPITAL_LOSS_BALANCE_1990_TO_1999,
    NET_CAPITAL_LOSS_BALANCE_2000,
    NET_CAPITAL_LOSS_BALANCE_2001_TO_2024,
)


def return_fw(**overrides: Any) -> Worksheet:
    """The worksheet of return FW, the inputs of `returns/2025_return_fw.yaml`.

    The filer has OAS of 4000, EI benefits of 20000 and RDSP income of 100000, a capital gain of
    20000 (shares, no adjusted cost base, no outlays), other deductions of 40000 (including the OAS
    overpayment recovered of 5000) and income tax deducted of 25000. The pre-1986 balance is 9000,
    the capital gains deductions claimed are 500 (before 1988), 400 (1988 and 1989), 600 (1990 to
    1999), 300 (2000, at an inclusion rate of 0.666666) and 100 (2001 to 2024), the unapplied net
    capital losses are 1000 (1985 to 1987) and the amount claimed (line 7) is 5000.
    """
    inputs: dict[str, Any] = {
        "old_age_security": "4000",
        "ei_and_other_benefits": "20000",
        "rdsp_income": "100000",
        "other_deductions": "40000",
        "oas_overpayment_recovered": "5000",
        "income_tax_deducted": "25000",
        "unapplied_net_capital_losses_1985_to_1987": "1000",
        "unapplied_net_capital_losses_2000": "0",
        "net_capital_losses_before_may_23_1985": "9000",
        "pre_1986_deductions_before_1988": "500",
        "pre_1986_deductions_1988_and_1989": "400",
        "pre_1986_deductions_1990_to_1999": "600",
        "pre_1986_deductions_2000": "300",
        "t657_inclusion_rate_2000": "0.666666",
        "pre_1986_deductions_2001_to_2024": "100",
        "net_capital_losses_claimed": "5000",
    }
    return compute(
        "0",
        (("20000", "0", "0"),),
        "0",
        "0",
        "0",
        "0",
        "0",
        resident_in_canada_throughout_2025=1,
        aged_18_or_older_at_end_of_2025=1,
        cpp_months=12,
        qpp_months=12,
        **{**inputs, **overrides},
    )


def values(worksheet: Worksheet, kinds: tuple[Any, ...]) -> list[Any]:
    return [worksheet.get(kind).value for kind in kinds]


def test_total_income_is_134000_and_net_income_before_adjustments_is_94000() -> None:
    # Total income: OAS 4,000 + EI 20,000 + RDSP income 100,000 + taxable capital gains 10,000 =
    # 134,000 (line 15000). Deductions from total income: other deductions 40,000 (line 23300). Line
    # 23400: 134,000 - 40,000 = 94,000.
    worksheet = return_fw()

    assert worksheet.get(TOTAL_INCOME).value == D("134000.00")
    assert worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("40000.00")
    assert worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("94000.00")


def test_share_proceeds_of_20000_give_taxable_capital_gains_of_10000() -> None:
    # Proceeds 20,000 less an adjusted cost base of 0 and outlays of 0 is a gain of 20,000; half is
    # taxable: 10,000 (Schedule 3).
    worksheet = return_fw()

    assert worksheet.get(SHARE_PROCEEDS).value == D("20000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("10000.00")


def test_chart_line_5_is_0_because_the_oas_recovered_is_above_line_3() -> None:
    # Line 3: OAS pension 4,000 + net federal supplements 0 = 4,000. Line 5: 4,000 - line 4 (the OAS
    # overpayment recovered, 5,000) = -1,000, which the form sets to "0" (if negative, enter "0").
    # The unfloored -1,000 would differ, so the zero is what this test pins.
    worksheet = return_fw()

    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT_APPLIES).value == 1
    assert worksheet.get(OAS_AND_FEDERAL_SUPPLEMENTS).value == D("4000")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_5).value != D("4000") - D("5000")


def test_line_11_is_minus_6000_with_no_floor() -> None:
    # Line 6: net income before adjustments, 94,000. Line 10: line 7 (EI repayment, 0) + line 8
    # (UCCB, 0) + line 9 (RDSP income, 100,000) = 100,000. Line 11: 94,000 - 100,000 = -6,000. The
    # form prints no floor on line 11, so the negative figure stands, and line 15 (line 11 + line
    # 14, 0) is -6,000.
    worksheet = return_fw()

    assert worksheet.get(SOCIAL_BENEFITS_LINE_6).value == D("94000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_10).value == D("100000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_11).value == D("-6000.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_14).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_15).value == D("-6000.00")


def test_line_17_and_line_19_are_0_because_line_15_is_below_the_oas_base() -> None:
    # Line 17: line 15 (-6,000) minus the OAS benefits base amount (93,343) is -99,343, which the
    # form sets to "0" (if negative, enter "0"). Line 18 is 0 x 15% = 0. Line 19 is the lesser of
    # line 5 (0) and line 18 (0): 0. Had line 5 not been floored (-1,000), line 19 would be -1,000
    # and the repayment -1,000 as well, so the zeros are what this test pins.
    worksheet = return_fw()

    assert worksheet.get(OAS_BENEFITS_BASE_AMOUNT).value == D("93343.00")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_17).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_18).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_LINE_19).value == D("0")


def test_line_21_is_0_so_there_is_no_repayment_and_net_income_is_94000() -> None:
    # Line 20: the amount from line 7, 0. Line 21: line 19 (0) + line 20 (0) = 0, so no social
    # benefits repayment is entered on line 23500. The EI repayment test (line 23400 less lines
    # 11700 and 12500 plus line 21300) is 94,000 - 100,000 = -6,000, so no repayment arises. Net
    # income (line 23600) is 94,000 - 0 = 94,000.
    worksheet = return_fw()

    assert worksheet.get(SOCIAL_BENEFITS_LINE_21).value == D("0")
    assert worksheet.get(SOCIAL_BENEFITS_REPAYMENT).value == D("0")
    assert worksheet.get(NET_INCOME).value == D("94000.00")


def test_pre_1986_line_2_is_1525_and_line_3_is_7475() -> None:
    # Form T1436: line 2 is A + B + C + D + E = 500 + 300.00 (400 x 3/4, printed 0.75) + 400.00 (600
    # x 2/3, printed 0.6667) + 225.00 (300 x 1/(0.666666 x 2)) + 100 = 1,525.00. Line 3 is line 1
    # less line 2: 9,000 - 1,525 = 7,475.00.
    worksheet = return_fw()

    assert worksheet.get(PRE_1986_DEDUCTIONS_TOTAL).value == D("1525.00")
    assert worksheet.get(PRE_1986_CAPITAL_LOSS_BALANCE).value == D("7475.00")


def test_the_adjusted_capital_gains_deductions_b_c_and_d_are_300_400_and_225() -> None:
    # The amounts after adjustment: B 400 x 3/4 (printed 0.75) = 300.00; C 600 x 2/3 (printed
    # 0.6667) = 400.00; D 300 x 1/(0.666666 x 2) = 225.000225, rounded to 225.00.
    worksheet = return_fw()

    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1988_AND_1989).value == D("300.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_1990_TO_1999).value == D("400.00")
    assert worksheet.get(PRE_1986_DEDUCTIONS_ADJUSTED_2000).value == D("225.00")


def test_pre_1986_line_4_is_8475_and_line_6_is_8475() -> None:
    # Line 4: the total of column C, 7,475.00 + 1,000.00 = 8,475.00. Line 6: the lesser of line 4
    # (8,475.00) and line 5 (the taxable capital gains, 10,000.00): 8,475.00.
    worksheet = return_fw()

    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES).value == D("8475.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_AVAILABLE_TO_CLAIM).value == D("8475.00")


def test_pre_1986_lines_7_8_and_9_are_5000_3475_and_2000() -> None:
    # Line 7: the losses claimed, 5,000 (at most line 6). Line 8: line 4 less line 7 = 8,475 - 5,000
    # = 3,475. Line 9: the least of line 3 (7,475), line 8 (3,475) and $2,000: 2,000.
    worksheet = return_fw()

    assert worksheet.get(ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("5000")
    assert worksheet.get(UNAPPLIED_ADJUSTED_NET_CAPITAL_LOSSES).value == D("3475.00")
    assert worksheet.get(NET_CAPITAL_LOSSES_ADDITIONAL_DEDUCTION).value == D("2000.00")


def test_pre_1986_lines_10_and_13_are_7000() -> None:
    # Line 10: line 7 (5,000) + line 9 (2,000) = 7,000, the net capital loss of other years deducted
    # on T1 line 25300. Line 13 is the same 7,000, applied to the oldest row first.
    worksheet = return_fw()

    assert worksheet.get(NET_CAPITAL_LOSSES_OF_OTHER_YEARS).value == D("7000.00")
    assert worksheet.get(TOTAL_ADJUSTED_NET_CAPITAL_LOSSES_APPLIED).value == D("7000.00")


def test_chart_a_column_c_is_7475_and_1000_for_the_two_rows_with_a_balance() -> None:
    # Column C is column A times column B: "Before May 23, 1985" 7,475.00 x 1 (line 3), "After May
    # 22, 1985, and before 1988" 1,000.00 x 1; every other row is 0.
    worksheet = return_fw()

    assert values(worksheet, COLUMN_C) == [
        D("7475.00"),
        D("1000.00"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
    ]


def test_chart_a_column_d_applies_7000_to_the_oldest_row() -> None:
    # Line 13 (7,000) is applied oldest row first: 7,000.00 to "Before May 23, 1985" (7,475.00 is
    # more), nothing left for the 1985 to 1987 row, so every other row is 0.
    worksheet = return_fw()

    assert values(worksheet, COLUMN_D) == [
        D("7000.00"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
    ]


def test_chart_a_column_e_is_475_and_1000() -> None:
    # Column E is column C less column D: 7,475.00 - 7,000.00 = 475.00; 1,000.00 - 0 = 1,000.00; the
    # other rows 0.
    worksheet = return_fw()

    assert values(worksheet, COLUMN_E) == [
        D("475.00"),
        D("1000.00"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
    ]


def test_chart_a_column_g_is_475_and_1000_carried_forward() -> None:
    # Column G is column E times column F (1, 1, 4/3 (printed 1.33), 3/2 (printed 1.5), 2 x IR, 1):
    # 475.00 x 1 and 1,000.00 x 1; the other rows 0.
    worksheet = return_fw()

    assert values(worksheet, COLUMN_G) == [
        D("475.00"),
        D("1000.00"),
        D("0"),
        D("0"),
        D("0"),
        D("0"),
    ]


def test_net_income_is_94000_and_taxable_income_is_87000() -> None:
    # Net income (line 23600) is 94,000. The deduction from net income is the net capital loss of
    # other years (line 25300), 7,000, and no other payments deduction applies (no net federal
    # supplements), so taxable income (line 26000) is 94,000 - 7,000 = 87,000.
    worksheet = return_fw()

    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("7000.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("87000.00")
