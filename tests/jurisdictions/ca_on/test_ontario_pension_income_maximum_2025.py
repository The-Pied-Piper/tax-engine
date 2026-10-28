"""The 2025 Ontario pension income maximum, checked against CRA's forms.

Form ON428 (form 5006-C), "Line 27 and line 58360: Pension income amount (maximum $1,762)": line 28
"Line 26 plus line 27". The maximum is printed on the line, so it caps the amount on the federal
line 31400 that the Ontario amount is the lesser of.

The dataset holds one amount, the maximum, rounded half-up to the cent (a dollars-and-cents
figure on the claim); it is a plain amount (the `amount` kind), not a claimed credit. The federal
maximum of the same name is `ca/pension_income_maximum`, checked in
`test_pension_income_maximum_2025.py`.
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
PENSION_INCOME_MAXIMUM = "ca-on/pension_income_maximum"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"


def test_2025_ontario_pension_income_maximum_is_1762() -> None:
    data = SOURCE.get(PENSION_INCOME_MAXIMUM, 2025, AMOUNT)

    assert data.values == Amount(D("1762"))
    # A dollars-and-cents amount: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_ontario_pension_income_maximum_cites_form_5006_c() -> None:
    assert SOURCE.get(PENSION_INCOME_MAXIMUM, 2025, AMOUNT).sources == (ON428_TEXT,)
