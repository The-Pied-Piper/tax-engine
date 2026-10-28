"""CA-ON 2025 end to end: return lf (Guide T4037 "Restricted farm loss", the bounds on the amount).

Guide T4037 (2025): the farmland example (sold for $200,000, ACB $160,000, an unapplied restricted
farm loss of $20,000 of which $10,000 is property taxes and interest). The Guide says "The amount of
RFLs that you can apply cannot be more than the property taxes and interest on money you borrowed
to buy the farmland that were included in the calculation of the RFLs for each year." and "You
cannot use it to create or increase a capital loss."

The worked return `returns/2025_return_lf.yaml` (checked by `test_worked_returns.py`) applies 4,000
and pins the capital gain of 36,000. This module reads the same gain through the Schedule 3 lines
and checks that an amount above either bound is refused, never capped.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    REAL_ESTATE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, FarmlandDisposition, run


def farmland_return(row: FarmlandDisposition) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        real_estate_dispositions=(row,),
        unapplied_restricted_farm_loss_taxes_and_interest="10000",
    )


def test_applying_4000_of_the_10000_allowed_gives_a_gain_of_36000() -> None:
    result = farmland_return(("200000", "160000", "0", 0, "10000", "2500", "1500"))
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("36000")
    assert worksheet.get(CAPITAL_GAIN).value == D("36000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("18000")


def test_an_amount_above_the_taxes_and_interest_part_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="restricted farm loss 10000$"):
        farmland_return(("200000", "160000", "0", 0, "10000", "6000", "4001"))


def test_an_amount_above_the_gain_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="cannot create or increase a capital loss"):
        farmland_return(("165000", "160000", "0", 0, "10000", "3000", "2001"))
