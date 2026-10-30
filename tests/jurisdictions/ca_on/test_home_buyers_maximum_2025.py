"""The 2025 amount of `ca/home_buyers_maximum`, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 93 (line 31270) "Home buyers' amount (maximum
$10,000)", and the T1 guide (form 5000-G, 2025): "Enter $10,000 on line 31270 of your
return if you are not splitting the amount with your spouse or common-law partner." and
"You and your spouse or common-law partner can split the claim but the combined total
cannot be more than $10,000." The maximum is the bound on the caller's claim.

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
HOME_BUYERS_MAXIMUM = "ca/home_buyers_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"


def test_2025_home_buyers_maximum_is_10000() -> None:
    data = SOURCE.get(HOME_BUYERS_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("10000"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
