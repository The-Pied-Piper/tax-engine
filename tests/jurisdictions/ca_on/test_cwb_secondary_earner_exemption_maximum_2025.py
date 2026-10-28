"""The 2025 amount of `ca/cwb_secondary_earner_exemption_maximum`, checked against CRA's forms.

Federal: 2025 Schedule 6 (form 5000-S6), Part B, "Secondary earner exemption": line 14 "If your
working income (line 5) is less than your eligible spouse's working income, enter whichever is
less from column 1: amount from line 5 or line 12. If your working income (line 5) is equal to or
more than your eligible spouse's working income, enter whichever is less from column 2: amount
from line 5 or line 12. (maximum $16,386)".

The dataset holds one amount, rounded half-up to the cent; it is a plain amount (the `amount`
kind), the maximum that line 14 is capped at, not a claimed credit.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
SECONDARY_EARNER_EXEMPTION_MAXIMUM = "ca/cwb_secondary_earner_exemption_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s6/5000-s6-25e.txt"


def test_2025_secondary_earner_exemption_maximum_is_16386() -> None:
    data = SOURCE.get(SECONDARY_EARNER_EXEMPTION_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("16386"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (CRA_FORM_TEXT,)
