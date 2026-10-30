"""CA-ON 2025 end to end: return kn (Guide T4037 "Restricted farm loss", the farmland example).

Guide T4037 (2025): farmland sold in 2025 for $200,000 with an ACB of $160,000 and an unapplied
restricted farm loss of $20,000, of which $5,000 is property taxes and $5,000 is interest. "Reduce
your capital gain by adding these amounts to the adjusted cost base (ACB) of your farmland": the
ACB entered is 160,000 with 10,000 applied, 170,000 used, and the capital gain (line F) is 30,000.

The worked return `returns/2025_return_kn.yaml` (checked by `test_worked_returns.py`) pins the 30000
CRA prints. This module reads the same gain through the Schedule 3 lines and the taxable half.
"""

from __future__ import annotations

from tax_engine.jurisdictions.ca.catalog import (
    CAPITAL_GAIN,
    REAL_ESTATE_GAIN_OR_LOSS,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

# One real estate row: proceeds 200000, ACB 160000 (the Guide's line B), outlays 0, not depreciable
# property, 10000 of property taxes and interest in the restricted farm loss, 5000 of property
# taxes and 5000 of interest added (the Guide's lines C and D). The Guide names no property type:
# real estate is a chosen entry.
FARMLAND = ("200000", "160000", "0", 0, "10000", "5000", "5000")


def test_the_capital_gain_on_the_farmland_is_30000_and_half_of_it_is_taxable() -> None:
    result = run(
        employment_income="0",
        share_dispositions=(),
        unused_rrsp_contributions="0",
        rrsp_contributions="0",
        rrsp_deduction_limit="0",
        rrsp_amount_deducted="0",
        union_dues="0",
        real_estate_dispositions=(FARMLAND,),
        unapplied_restricted_farm_loss_taxes_and_interest="10000",
    )
    worksheet = result["ca-on/return"][0]

    assert worksheet.get(REAL_ESTATE_GAIN_OR_LOSS).value == D("30000")
    assert worksheet.get(CAPITAL_GAIN).value == D("30000")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("15000")
