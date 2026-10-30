"""CA-ON 2025 end to end: Return JO (returns/2025_return_jo.yaml), limited partnership losses.

Return JO is an Ontario resident with employment income of 30,000. Guide 5000-G line 25100
(docs/cra-forms-2025/5000-g-25e.txt): "you can only deduct them if you have a positive at-risk
amount (ARA) for the partnership" and "You can only deduct this loss if there is an amount in box
105". The amount claimed is the filer's figure; a claim above the T5013 box 105 amount is refused,
not capped. The guide prints no cap by the amount of box 105 itself: the bound is ours.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT,
    DEDUCTIONS_FROM_NET_INCOME,
    LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED,
    TAXABLE_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_jo(claim: str = "4000", at_risk: str = "6000") -> dict[str, tuple[Worksheet, ...]]:
    """Return JO: employment income of 30,000, limited partnership losses of other years `claim`
    claimed on line 25100 and a T5013 box 105 at-risk amount of `at_risk`."""
    return run(
        "30000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        limited_partnership_losses_of_other_years=claim,
        limited_partnership_at_risk_amount=at_risk,
    )


def test_a_claim_below_the_at_risk_amount_is_deducted_on_line_25100() -> None:
    # 4,000 claimed against a box 105 amount of 6,000: net income 29,735.00 less 4,000 is
    # 25,735.00.
    worksheet = run_jo()["ca-on/return"][0]

    assert worksheet.get(LIMITED_PARTNERSHIP_LOSSES_OF_OTHER_YEARS_CHECKED).value == D("4000")
    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("4000")
    assert worksheet.get(TAXABLE_INCOME).value == D("25735.00")


def test_a_claim_of_the_whole_at_risk_amount_is_accepted() -> None:
    worksheet = run_jo("6000")["ca-on/return"][0]

    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("6000")
    assert worksheet.get(TAXABLE_INCOME).value == D("23735.00")


def test_a_claim_above_the_at_risk_amount_is_refused_not_capped() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/limited_partnership_losses_of_other_years 6001 is above "
        r"ca/limited_partnership_at_risk_amount 6000\S*",
    ):
        run_jo("6001")


def test_a_claim_with_no_at_risk_amount_is_refused() -> None:
    # "You can only deduct this loss if there is an amount in box 105": $99,999 against a box 105
    # of 0 on a $60,000 job (Return Y's income) is refused instead of taking taxable income to 0.
    with pytest.raises(
        InputAboveBoundError,
        match=r"ca/limited_partnership_losses_of_other_years 99999 is above "
        r"ca/limited_partnership_at_risk_amount 0\S*",
    ):
        run_jo("99999", "0")


def test_no_claim_and_no_at_risk_amount_is_accepted() -> None:
    worksheet = run_jo("0", "0")["ca-on/return"][0]

    assert worksheet.get(DEDUCTIONS_FROM_NET_INCOME).value == D("0")
    assert worksheet.get(AMT_LIMITED_PARTNERSHIP_LOSSES_ADJUSTMENT).value == D("0")
