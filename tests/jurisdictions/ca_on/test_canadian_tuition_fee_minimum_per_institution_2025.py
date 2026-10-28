"""The 2025 amount of `ca/canadian_tuition_fee_minimum_per_institution`, checked against CRA.

Federal: 2025 Schedule 11 (form 5000-S11) line 1 and line 32000 "Eligible tuition fees paid to
Canadian educational institutions for 2025 (fees for each institution must be more than $100)".
The $100 is a per-unit amount, times the number of institutions the fees were paid to (a count).
The form prints the condition as "more than", so the total must be strictly above the minimum.

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
MINIMUM_PER_INSTITUTION = "ca/canadian_tuition_fee_minimum_per_institution"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s11/5000-s11-25e.txt"


def test_2025_minimum_per_institution_is_100() -> None:
    data = SOURCE.get(MINIMUM_PER_INSTITUTION, 2025, AMOUNT)

    assert data.values == Amount(D("100.00"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
