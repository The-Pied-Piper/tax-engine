"""CA-ON 2025 end to end: return kc (Form T2048 Chart A line 13, net partnership income).

Form T2048 (2025), Chart A line 13: "Net income from limited or non-active partnership (line 12200)
other than taxable capital gains". The taxable capital gains that the line 12200 amount includes are
entered once (the shared fact with Form T936 Part 2 line 10) and taken off line 12200; the form
prints no limit or floor.

The worked return `returns/2025_return_kc.yaml` (Return BE with a line 12200 amount of 3,000 that
includes 1,000 of taxable capital gains) is checked by `test_worked_returns.py`. This module reads
the cases the worked return does not express: no carve-out, a carve-out of the whole line 12200
amount, and a carve-out above it, which leaves line 13 negative.
"""

from __future__ import annotations

from tax_calculator.jurisdictions.ca.catalog import (
    QBT_CHART_A_NET_INVESTMENT_LOSS,
    QBT_INVESTMENT_INCOME,
    QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    QBT_PARTNERSHIP_TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, form_be


def test_line_13_is_line_12200_less_the_taxable_capital_gains_it_includes() -> None:
    # Line 12200 is 3000 and includes 1000 of taxable capital gains: line 13 is 2000.00. Line 19 is
    # 25500.00 (Return BE) + 2000.00 = 27500.00 and line 20 is 31000.00 - 27500.00 = 3500.00.
    worksheet = form_be(
        net_partnership_income="3000",
        partnership_taxable_capital_gains="1000",
        qbt_deduction_claimed="60500",
    )

    assert worksheet.get(QBT_PARTNERSHIP_TAXABLE_CAPITAL_GAINS).value == D("1000")
    assert worksheet.get(QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("2000")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("27500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("3500.00")


def test_without_taxable_capital_gains_in_line_12200_line_13_is_all_of_it() -> None:
    # Line 13 is 3000; line 19 is 25500.00 + 3000 = 28500.00 and line 20 is 31000.00 - 28500.00 =
    # 2500.00.
    worksheet = form_be(net_partnership_income="3000", qbt_deduction_claimed="60500")

    assert worksheet.get(QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("3000")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("28500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("2500.00")


def test_taxable_capital_gains_equal_to_line_12200_leave_line_13_at_0() -> None:
    worksheet = form_be(
        net_partnership_income="3000",
        partnership_taxable_capital_gains="3000",
        qbt_deduction_claimed="60500",
    )

    assert worksheet.get(QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("0")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("25500.00")


def test_taxable_capital_gains_above_line_12200_leave_line_13_negative() -> None:
    # The form prints no limit or floor on line 13: 3000.00 less 3000.01 is (0.01), so line 19 is
    # 25500.00 (Return BE) - 0.01 = 25499.99 and line 20 is 31000.00 - 25499.99 = 5500.01.
    worksheet = form_be(
        net_partnership_income="3000",
        partnership_taxable_capital_gains="3000.01",
        qbt_deduction_claimed="60000",
    )

    assert worksheet.get(QBT_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("-0.01")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("25499.99")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("5500.01")
