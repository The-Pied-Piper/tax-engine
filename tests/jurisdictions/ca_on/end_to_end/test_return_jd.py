"""CA-ON 2025 end to end: return jd."""

from __future__ import annotations

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_ADJUSTED_TAXABLE_INCOME,
    AMT_PART_1_SUBTOTAL,
    AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL,
    AMT_SECURITY_OPTIONS_D1_TOTAL,
    AMT_SECURITY_OPTIONS_D_TOTAL,
    AMT_SECURITY_OPTIONS_NET,
    NET_INCOME,
    SECURITY_OPTIONS_DEDUCTIONS,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    TAXABLE_INCOME,
    TAXABLE_INCOME_SIGNED,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_jd() -> Worksheet:
    """Employment income 42000 (a chosen figure, which includes the security option benefits of
    the T4 boxes 39 and 91 of 30000 and the boxes 41 and 92 of 10000), gifts of publicly listed
    securities of 2000 (Form T691 line 31) and no T1212 amount, as in `returns/2025_return_jd.yaml`.
    """
    return compute(
        "42000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t4_security_options_boxes_39_and_91="30000",
        t4_security_options_boxes_41_and_92="10000",
        amt_security_option_publicly_listed_gifts="2000",
        t4_cpp_pensionable_earnings_outside_quebec="42000",
        t2204_insurable_earnings="42000",
        t2204_premiums_deducted="688.80",
        cpp_t4_base_and_first_additional_contributions="2290.75",
        cpp_t4_second_additional_contributions="0",
    )


def test_jd_the_t4_boxes_are_read_once_by_t691_and_line_24900() -> None:
    # Form T691 Part 1 line 28 is the total of boxes 39 and 91 (30000) and line 35 the total of
    # boxes 41 and 92 (10000); the same two figures are the boxes of line 24900 of the return, which
    # the return computes rather than takes as an input.
    worksheet = return_jd()

    assert worksheet.get(T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL).value == D("30000")
    assert worksheet.get(T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL).value == D("10000")
    assert worksheet.get(AMT_SECURITY_OPTIONS_D_TOTAL).value == D("30000")
    assert worksheet.get(AMT_SECURITY_OPTIONS_D1_TOTAL).value == D("10000")


def test_jd_line_24900_is_the_boxes_plus_the_gifts_as_entered() -> None:
    # Guide 5000-G line 24900 "Claim on line 24900 of your return the total of the amounts shown in
    # boxes 39, 41, 91, and 92 of your T4 slips", and Form T691 line 31 (the gifts of 2000 "included
    # on line 24900"): 30000 + 0 + 2000 + 10000 + 0 + 0 = 42000, which is the total income of 42000,
    # taken as entered.
    worksheet = return_jd()

    assert worksheet.get(SECURITY_OPTIONS_DEDUCTIONS).value == D("42000")


def test_jd_net_income_and_the_signed_taxable_income_after_line_24900() -> None:
    # Net income is the employment income of 42000 less the enhanced CPP contributions deducted on
    # line 22215, 1% of 42000 less the 3500 basic exemption, 385: 41615. Line 26000 is 41615 less
    # line 24900 of 42000, -385, which is 0 on the return but the signed -385 is Form T691 Part 1
    # line 1, so the minimum tax starts from -385 (part 1 line 12). Line 33 is that plus the 29200
    # of line 32 (the 30000 of line 30 less 40% of the 2000 of line 31, 800), 28815, and line 44
    # adds the 10000 of line 38 and the 0 of line 43: 38815. Line 82 adds line 80 to it, 50% of the
    # 385 of line 78 (the enhanced CPP contributions of line 58, added back), 192.50: 39007.50,
    # which is the adjusted taxable income of line 93 (no dividends or capital gains deduction).
    worksheet = return_jd()

    assert worksheet.get(NET_INCOME).value == D("41615.00")
    assert worksheet.get(TAXABLE_INCOME_SIGNED).value == D("-385.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("0")
    assert worksheet.get(AMT_PART_1_SUBTOTAL).value == D("-385.00")
    assert worksheet.get(AMT_SECURITY_OPTIONS_NET).value == D("29200.00")
    assert worksheet.get(AMT_SECURITY_OPTIONS_AND_LOSSES_TOTAL).value == D("38815.00")
    assert worksheet.get(AMT_ADJUSTED_TAXABLE_INCOME).value == D("39007.50")
