"""CA-ON 2025 end to end: return ar."""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    NET_INCOME,
    PARTNERSHIP_GAINS_AT_FULL_INCLUSION,
    REFUND_OR_BALANCE_OWING,
    SHARE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, compute


def return_ar(**overrides: Any) -> Worksheet:
    """Return AR's inputs, as in `returns/2025_return_ar.yaml`: employment income of 60000 and a
    share sale with a gain of 40000, each a chosen figure, and 10000 of partnership gains at full
    inclusion on Schedule 3 line 25; `overrides` replace any keyword of `compute`, for the
    variants below.
    """
    given: dict[str, Any] = {
        "partnership_gains_at_full_inclusion": "10000.00",
        "income_tax_deducted": "22000",
    }
    return compute(
        "60000", (("40000.00", "0.00", "0.00"),), "0", "0", "0", "0", "0", **{**given, **overrides}
    )


def test_return_ar_adds_the_partnership_gain_to_line_24_on_line_12700() -> None:
    # Line 4 and line 13200: the share gain of 40000.00, which is line 21 and line 22. Line 24 is
    # 50% of 40000.00 = 20000.00. Line 26 = line 24 plus line 25 = 20000.00 + 10000.00 = 30000.00,
    # positive, so line 12700 is 30000.00. Line 25 is not multiplied by the inclusion rate (its
    # 100% inclusion is the point of the line). Total income (line 15000) = 60000.00 + 30000.00 =
    # 90000.00. The enhanced CPP contributions (565.00) are deducted: net income and taxable income
    # are 89435.00. The total payable is 17721.79 (federal 11791.47 and Ontario 5930.32), and with
    # the chosen tax deducted of 22000.00 the refund (line 48400) is 4278.21.
    worksheet = return_ar()

    assert worksheet.get(PARTNERSHIP_GAINS_AT_FULL_INCLUSION).value == D("10000.00")
    assert worksheet.get(SHARE_GAIN_OR_LOSS).value == D("40000.00")
    assert worksheet.get(CAPITAL_GAIN).value == D("40000.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("20000.00")
    assert isinstance(worksheet.producer_of(TAXABLE_CAPITAL_GAINS), SumNotBelowZero)
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("30000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("90000.00")
    assert worksheet.get(NET_INCOME).value == D("89435.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("89435.00")
    assert worksheet.get(TOTAL_PAYABLE).value == D("17721.79")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-4278.21")


def test_the_partnership_gain_of_10000_adds_2965_to_the_total_payable() -> None:
    # Without line 25 the taxable capital gains are 20000.00 and the taxable income 79435.00: the
    # total payable is 14756.79. The 10000.00 is taxed at the 20.5% federal rate (2050.00, the
    # second bracket of 57375.00 to 114750.00) and the 9.15% Ontario rate (915.00): 2965.00.
    with_line_25 = return_ar()
    without_line_25 = return_ar(partnership_gains_at_full_inclusion="0")

    assert without_line_25.get(TAXABLE_CAPITAL_GAINS).value == D("20000.00")
    assert without_line_25.get(TOTAL_PAYABLE).value == D("14756.79")
    assert with_line_25.get(TOTAL_PAYABLE).value - without_line_25.get(TOTAL_PAYABLE).value == D(
        "2965.00"
    )


def test_a_negative_line_24_plus_line_25_is_taken_as_the_positive_part_on_line_12700() -> None:
    # A share loss of 20000.00 (proceeds 0.00, adjusted cost base 20000.00) is line 21 of
    # -20000.00 and line 24 of -10000.00 (50%, signed). Line 25 of 15000.00 gives line 26 =
    # -10000.00 + 15000.00 = 5000.00, positive, so line 12700 is 5000.00, not the negative line 24
    # and not 15000.00. Total income (line 15000) = 60000.00 + 5000.00 = 65000.00.
    worksheet = compute(
        "60000",
        (("0.00", "20000.00", "0.00"),),
        "0",
        "0",
        "0",
        "0",
        "0",
        partnership_gains_at_full_inclusion="15000.00",
        income_tax_deducted="22000",
    )

    assert worksheet.get(CAPITAL_GAIN).value == D("-20000.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("-10000.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("5000.00")
    assert worksheet.get(TOTAL_INCOME).value == D("65000.00")
