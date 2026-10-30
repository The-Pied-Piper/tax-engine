"""The 2025 amount of `ca/volunteer_firefighters_amount`, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 90 (line 31220) "Volunteer firefighters' amount
(VFA)", and the T1 guide (form 5000-G, 2025): "You can claim $6,000 for the volunteer
firefighters' amount (VFA) or search and rescue volunteers' amount (SRVA), but not both,
if you meet all of the following conditions:". The $6,000 is a per-unit amount, times
the conditions met (a count, 1 or 0) on line 31220 of the return.

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
VFA_AMOUNT = "ca/volunteer_firefighters_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"


def test_2025_volunteer_firefighters_amount_is_6000() -> None:
    data = SOURCE.get(VFA_AMOUNT, 2025, AMOUNT)

    assert data.values == Amount(D("6000"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
