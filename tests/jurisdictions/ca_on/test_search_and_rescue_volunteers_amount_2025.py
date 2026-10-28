"""The 2025 amount of `ca/search_and_rescue_volunteers_amount`, checked against CRA's forms.

Federal: 2025 T1 (form 5000-R) line 91 (line 31240) "Search and rescue volunteers'
amount (SRVA)", and the T1 guide (form 5000-G, 2025): "You can claim $6,000 for the
volunteer firefighters' amount (VFA) or search and rescue volunteers' amount (SRVA), but
not both, if you meet all of the following conditions:". The $6,000 is a per-unit
amount, times the conditions met (a count, 1 or 0) on line 31240 of the return.

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
SRVA_AMOUNT = "ca/search_and_rescue_volunteers_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5000-g/5000-g-25e.txt"


def test_2025_search_and_rescue_volunteers_amount_is_6000() -> None:
    data = SOURCE.get(SRVA_AMOUNT, 2025, AMOUNT)

    assert data.values == Amount(D("6000"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
