"""The 2025 amount of `ca/pension_income_maximum`, checked against CRA's forms.

Federal: 2025 Federal Worksheet (form 5000-D1), "Line 31400 - Pension income amount":
"Enter on line 31400 of your return whichever amount is less: line 8 or $2,000." T1 line
97 (line 31400) "Pension income amount (use Federal Worksheet) (maximum $2,000)".

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
PENSION_INCOME_MAXIMUM = "ca/pension_income_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"


def test_2025_pension_income_maximum_is_2000() -> None:
    data = SOURCE.get(PENSION_INCOME_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("2000"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
