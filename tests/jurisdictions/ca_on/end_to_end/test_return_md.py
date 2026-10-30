"""CA-ON 2025 end to end: return md (Form T2048 Chart A line 15, the recovery part of line 13000).

Form T2048 (2025), Chart A line 15: "50% of income from the recovery of exploration and development
expenses (line 13000)". Line 13000 "Other income" also holds retiring allowances, death benefits
and the like, so the filer enters the recovery part and the form takes 50% of that part, which may
not exceed line 13000.

The worked return `returns/2025_return_md.yaml` (Return BE with a line 13000 amount of 5,000 of
which 2,000 is the recovery) is checked by `test_worked_returns.py`. This module reads the cases
the worked return does not express: no recovery, the whole of line 13000 as the recovery, and a
recovery above line 13000, which is refused.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.jurisdictions.ca.catalog import (
    QBT_CHART_A_NET_INVESTMENT_LOSS,
    QBT_EXPLORATION_RECOVERY_INCOME_CHECKED,
    QBT_INVESTMENT_INCOME,
    QBT_RECOVERY_OF_EXPLORATION_EXPENSES,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, form_be


def test_line_15_is_50_percent_of_the_recovery_part_not_of_all_of_line_13000() -> None:
    # Line 13000 is 5000 and 2000 of it is the recovery: line 15 is 1000.00, not 2500.00. Line 19
    # is 25500.00 (Return BE) and line 20 is 31000.00 - 25500.00 = 5500.00.
    worksheet = form_be(
        other_income="5000", qbt_exploration_recovery_income="2000", qbt_deduction_claimed="60500"
    )

    assert worksheet.get(QBT_EXPLORATION_RECOVERY_INCOME_CHECKED).value == D("2000")
    assert worksheet.get(QBT_RECOVERY_OF_EXPLORATION_EXPENSES).value == D("1000.00")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("25500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("5500.00")


def test_without_a_recovery_line_15_is_0_whatever_line_13000_holds() -> None:
    # Line 15 is 0; line 19 is 25500.00 - 1000.00 = 24500.00 and line 20 is 31000.00 - 24500.00 =
    # 6500.00, so line 26 is 80000.00 - 20500.00 = 59500.00, the most that can be claimed.
    worksheet = form_be(
        other_income="5000", qbt_exploration_recovery_income="0", qbt_deduction_claimed="59500"
    )

    assert worksheet.get(QBT_RECOVERY_OF_EXPLORATION_EXPENSES).value == D("0")
    assert worksheet.get(QBT_INVESTMENT_INCOME).value == D("24500.00")
    assert worksheet.get(QBT_CHART_A_NET_INVESTMENT_LOSS).value == D("6500.00")


def test_a_recovery_equal_to_line_13000_is_all_of_it() -> None:
    worksheet = form_be(
        other_income="5000", qbt_exploration_recovery_income="5000", qbt_deduction_claimed="60500"
    )

    assert worksheet.get(QBT_RECOVERY_OF_EXPLORATION_EXPENSES).value == D("2500.00")


def test_a_recovery_above_line_13000_is_refused_naming_both_kinds() -> None:
    # 2000.01 of recovery cannot be in a line 13000 amount of 2000: an input error, not capped.
    with pytest.raises(InputAboveBoundError) as raised:
        form_be(other_income="2000", qbt_exploration_recovery_income="2000.01")

    assert str(raised.value).startswith(
        "ca/t2048, instance 1: ca/qbt_exploration_recovery_income 2000.01 is above "
        "ca/other_income 2000"
    )
