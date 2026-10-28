"""CA-ON 2025 end to end: return kf (Form T2048 Part 3 line 24, one answer for the year).

Form T2048 (2025), Part 3 line 24: "Net investment loss for the year: If you have investment
expenses in 2025, complete Chart A on page 4 and enter the amount from line 20 of Chart A.
Otherwise, enter "0"." The answer to "If you have investment expenses in 2025" is one answer for
the year, entered once and read by the form of every disposition.

The worked return `returns/2025_return_kf.yaml` (Return BZ, two QBTs, with other investment
expenses of 60,000 and the answer 1) is checked by `test_worked_returns.py`. This module reads the
cases the worked return does not express: the answer 0, which gives line 24 as 0 on both forms, and
an answer above 1, which is refused.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    QBT_CAPITAL_GAINS_DEDUCTION,
    QBT_HAS_INVESTMENT_EXPENSES,
    QBT_NET_INVESTMENT_LOSS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run_bz

# Return BZ's two QBTs, the first claiming 290,000 (its line 26 with a line 24 of 10,000.00) and
# the second claiming 0 (its line 24 is 50,000.00 and its line 26 is 0).
EXPENSES = {"other_investment_expenses": "60000"}


def rows(first: str, second: str) -> tuple[dict[str, str | int], ...]:
    return (
        {
            "qbt_election_eligible_amount": "1000000",
            "qbt_percentage_allocated": "100",
            "qbt_capital_gains": "600000",
            "qbt_election_is_qbt": 1,
            "qbt_deduction_claimed": first,
        },
        {
            "qbt_election_eligible_amount": "400000",
            "qbt_percentage_allocated": "100",
            "qbt_capital_gains": "200000",
            "qbt_election_is_qbt": 1,
            "qbt_deduction_claimed": second,
        },
    )


def test_the_one_yes_answer_gives_line_24_on_both_forms() -> None:
    # Chart A line 20 is 60000.00 - 50000.00 = 10000.00 on the first form; on the second it is
    # 60000.00 - 0.00 = 60000.00 less the earlier line 42 (10000.00): 50000.00. The answer is 1 for
    # both, so line 24 is those amounts and the second form's line 26 is 50000.00 - 50000.00 = 0.
    one, two = run_bz(
        **EXPENSES, has_investment_expenses=1, t2048_dispositions_rows=rows("290000", "0")
    )["ca/t2048"]

    assert one.get(QBT_HAS_INVESTMENT_EXPENSES).value == 1
    assert two.get(QBT_HAS_INVESTMENT_EXPENSES).value == 1
    assert one.get(QBT_NET_INVESTMENT_LOSS).value == D("10000.00")
    assert two.get(QBT_NET_INVESTMENT_LOSS).value == D("50000.00")


def test_the_one_no_answer_gives_line_24_of_0_on_both_forms() -> None:
    # "Otherwise, enter 0": line 24 is 0 on both forms whatever Chart A would give, so the first
    # form can claim all of its line 17, 300000, and the second all of its 50000.
    runs = run_bz(
        **EXPENSES, has_investment_expenses=0, t2048_dispositions_rows=rows("300000", "50000")
    )
    one, two = runs["ca/t2048"]

    assert one.get(QBT_HAS_INVESTMENT_EXPENSES).value == 0
    assert two.get(QBT_HAS_INVESTMENT_EXPENSES).value == 0
    assert one.get(QBT_NET_INVESTMENT_LOSS).value == D("0")
    assert two.get(QBT_NET_INVESTMENT_LOSS).value == D("0")
    assert one.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("300000")
    assert two.get(QBT_CAPITAL_GAINS_DEDUCTION).value == D("50000")


def test_an_answer_above_1_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run_bz(**EXPENSES, has_investment_expenses=2)
