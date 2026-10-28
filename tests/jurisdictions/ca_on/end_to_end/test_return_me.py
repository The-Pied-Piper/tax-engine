"""CA-ON 2025 end to end: return me (Guide T4037 "Restricted farm loss", farmland on line 2).

Guide T4037 (2025): farmland sold in 2025 for $200,000 with an ACB of $160,000 and an unapplied
restricted farm loss of $20,000, of which $5,000 is property taxes and $5,000 is interest. "Reduce
your capital gain by adding these amounts to the adjusted cost base (ACB) of your farmland": the
ACB entered is 160,000 with 10,000 applied, 170,000 used, and the capital gain (line F) is 30,000.
Return KN enters the sale as real estate; this module enters it as qualified farm or fishing
property (Schedule 3 line 2), the same Guide text.

The worked return `returns/2025_return_me.yaml` (checked by `test_worked_returns.py`) pins the 30000
CRA prints. This module reads the same gain through the Schedule 3 lines and the taxable half, and
the refusals above the property taxes and interest part and above the gain.
"""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_GAIN_OR_LOSS,
    REAL_ESTATE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, QffpFarmlandDisposition, run

# One qualified farm or fishing property row: proceeds 200000, ACB 160000 (the Guide's line B),
# outlays 0, 10000 of property taxes and interest in the restricted farm loss, 5000 of property
# taxes and 5000 of interest added (the Guide's lines C and D).
FARMLAND = ("200000", "160000", "0", "10000", "5000", "5000")


def farmland_return(row: QffpFarmlandDisposition) -> dict[str, tuple[Worksheet, ...]]:
    return run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        qffp_dispositions=(row,),
        unapplied_restricted_farm_loss_taxes_and_interest="10000",
    )


def test_the_capital_gain_on_the_farmland_is_30000_and_half_of_it_is_taxable() -> None:
    worksheet = farmland_return(FARMLAND)["ca-on/return"][0]

    assert worksheet.get(QFFP_GAIN_OR_LOSS).value == D("30000")
    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("0")
    assert worksheet.get(CAPITAL_GAIN).value == D("30000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("15000")


def test_the_same_sale_as_a_repossession_on_line_3_gives_the_same_gain() -> None:
    # Guide T4037: a repossessed property is considered sold, so the loss applies on line 3 too.
    result = run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        qffp_foreclosure_dispositions=(FARMLAND,),
        unapplied_restricted_farm_loss_taxes_and_interest="10000",
    )
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(QFFP_FORECLOSURE_GAIN_OR_LOSS).value == D("30000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("15000")


def test_a_farm_loss_above_the_taxes_and_interest_part_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="item 1: .*is above the property taxes"):
        farmland_return(("200000", "160000", "0", "9999", "5000", "5000"))


def test_a_farm_loss_above_the_gain_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match="is above the gain 9999"):
        farmland_return(("169999", "160000", "0", "10000", "5000", "5000"))
