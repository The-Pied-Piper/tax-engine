"""The 2025 amount of `ca/volunteer_amount_maximum`, checked against CRA's forms.

Federal: the T1 guide (form 5000-G, 2025): "You can claim $6,000 for the volunteer
firefighters' amount (VFA) or search and rescue volunteers' amount (SRVA), but not both,
if you meet all of the following conditions:". The VFA and the SRVA together are at
most this $6,000 (the "but not both" bound on the sum of lines 31220 and 31240).

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.credit import CREDIT, Credit
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
VOLUNTEER_MAXIMUM = "ca/volunteer_amount_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"


def test_2025_volunteer_amount_maximum_is_6000() -> None:
    data = SOURCE.get(VOLUNTEER_MAXIMUM, 2025, CREDIT)

    assert data.values == Credit(amount=D("6000"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
