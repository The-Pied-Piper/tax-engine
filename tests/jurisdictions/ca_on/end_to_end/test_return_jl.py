"""CA-ON 2025 end to end: Return JL (returns/2025_return_jl.yaml), restricted farm losses.

Return JL is an Ontario resident with employment income of 30,000 and one Form T2042 statement
with wheat sales of 5,000, so net farming income (T1 line 14100) is 5,000. Guide T4002
(docs/cra-forms-2025/t4002-25e.pdf, "Applying your restricted farm losses from years before 2025";
confirmed from the PDF, no .txt published): "you can only apply them up to the amount of your net
farming income in 2025 ... Claim this amount on line 25200." The amount claimed is the filer's
figure, added on line 25200 to the non-capital losses of other years; a claim above the net farming
income is refused, not capped. Form T691 Part 1 lines 41 and 50 read the whole of line 25200.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_NON_CAPITAL_LOSSES_ADJUSTMENT,
    AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED,
    DEDUCTIONS_FROM_NET_INCOME,
    NET_FARMING_INCOME_NOT_BELOW_ZERO,
    NET_INCOME,
    NON_CAPITAL_LOSSES_ON_LINE_25200,
    RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_jl(
    claim: str = "5000",
    *,
    wheat: str = "5000",
    expenses: str = "0",
    non_capital: str = "0",
    amt_difference: str = "0",
) -> dict[str, tuple[Worksheet, ...]]:
    """Return JL: employment income of 30,000 and one T2042 statement with wheat sales `wheat` and
    fertilizers and lime `expenses`, restricted farm losses of other years `claim` and non-capital
    losses of other years `non_capital`, and the T691 line 41 difference `amt_difference`."""
    return run(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=({"farm": {"wheat": wheat, "fertilizers_and_lime": expenses}},),
        restricted_farm_losses_of_other_years=claim,
        non_capital_losses_of_other_years=non_capital,
        amt_non_capital_losses_difference=amt_difference,
    )


def test_a_claim_of_the_net_farming_income_is_deducted_on_line_25200() -> None:
    # 8,000 of losses from 2023, 5,000 of net farming income: 5,000 is claimed, the 3,000 left
    # carries on. Net income 35,000 - 265 = 34,735.00, less 5,000 on line 25200: 29,735.00.
    worksheet = run_jl()["ca-on/return"][0]

    assert worksheet.get(NET_FARMING_INCOME_NOT_BELOW_ZERO).value == D("5000.00")
    assert worksheet.get(RESTRICTED_FARM_LOSSES_OF_OTHER_YEARS_CHECKED).value == D("5000")
    assert worksheet.get(NON_CAPITAL_LOSSES_ON_LINE_25200).value == D("5000")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("5000")
    assert worksheet.get(NET_INCOME).value == D("34735.00")
    assert worksheet.get(TAXABLE_INCOME).value == D("29735.00")


def test_a_claim_below_the_net_farming_income_is_deducted_as_claimed() -> None:
    # 2,000 of the 5,000 of net farming income: line 25200 is 2,000 and taxable income 32,735.00.
    worksheet = run_jl("2000")["ca-on/return"][0]

    assert worksheet.get(NON_CAPITAL_LOSSES_ON_LINE_25200).value == D("2000")
    assert worksheet.get(TAXABLE_INCOME).value == D("32735.00")


def test_a_claim_above_the_net_farming_income_is_refused_not_capped() -> None:
    # 5,001 of losses against 5,000 of net farming income: "you can only apply them up to the
    # amount of your net farming income".
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/restricted_farm_losses_of_other_years 5001 is above "
        r"ca/net_farming_income_not_below_zero 5000\S*",
    ):
        run_jl("5001")


def test_a_net_farm_loss_leaves_nothing_to_apply_the_losses_against() -> None:
    # Fertilizers and lime of 3,000 and no sales: net farming income is a loss, counted as 0, so
    # any claim is refused and a claim of 0 is accepted.
    worksheet = run_jl("0", wheat="0", expenses="3000")["ca-on/return"][0]

    assert worksheet.get(NET_FARMING_INCOME_NOT_BELOW_ZERO).value == D("0")
    assert worksheet.get(NON_CAPITAL_LOSSES_ON_LINE_25200).value == D("0")
    with pytest.raises(InputAboveBoundError):
        run_jl("1", wheat="0", expenses="3000")


def test_the_restricted_farm_losses_add_to_the_non_capital_losses_on_line_25200() -> None:
    # 1,500 of non-capital losses of other years and 5,000 of restricted farm losses: line 25200
    # is 6,500 (the cap is on the restricted farm losses alone, not on the line).
    worksheet = run_jl(non_capital="1500")["ca-on/return"][0]

    assert worksheet.get(NON_CAPITAL_LOSSES_ON_LINE_25200).value == D("6500")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("6500")
    assert worksheet.get(TAXABLE_INCOME).value == D("28235.00")


def test_form_t691_line_41_may_be_up_to_the_whole_of_line_25200() -> None:
    # Form T691 Part 1 line 41 covers "non-capital losses, including restricted farm losses ...
    # on line 25200": a difference of 5,000 against the 5,000 claimed is accepted, line 50 is 0.
    worksheet = run_jl(amt_difference="5000")["ca-on/return"][0]

    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_DIFFERENCE_CHECKED).value == D("5000")
    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_ADJUSTMENT).value == D("0")


def test_form_t691_line_41_above_the_whole_of_line_25200_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/amt_non_capital_losses_difference 5001 is above "
        r"ca/non_capital_losses_on_line_25200 5000\S*",
    ):
        run_jl(amt_difference="5001")


def test_form_t691_line_50_is_the_whole_of_line_25200_less_line_41() -> None:
    # Line 25200 of 6,500 less a line 41 difference of 2,000 is 4,500.
    worksheet = run_jl(non_capital="1500", amt_difference="2000")["ca-on/return"][0]

    assert worksheet.get(AMT_NON_CAPITAL_LOSSES_ADJUSTMENT).value == D("4500")
