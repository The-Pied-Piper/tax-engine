"""The 2025 Form T2043 datasets, checked against the printed form.

Form T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit, 2025 edition, read from the PDF
(https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf; no .txt is
published). Two datasets, one for each figure the form prints:
- `ca/fuel_charge_payment_rate`: Part 2 "ON payment rate 0.229%", the rate each province's farming
  expenses are multiplied by (lines 2A to 2H, "each at 0.229%"). The rate is a dataset figure as
  printed; each product is a dollars-and-cents box, so it rounds half-up to the cent, as the form
  states no rounding rule.
- `ca/fuel_charge_expense_threshold`: Part 1 Note 1 "If your total gross farming expenses for all
  businesses are $25,000 or more, you are eligible to claim the credit." The amount is a
  dollars-and-cents figure, so it is an amount with the cent rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
T2043_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2043/t2043-25e.pdf"
PAYMENT_RATE = "ca/fuel_charge_payment_rate"
EXPENSE_THRESHOLD = "ca/fuel_charge_expense_threshold"


def test_2025_payment_rate_is_point_two_two_nine_percent_rounded_to_the_cent() -> None:
    data = SOURCE.get(PAYMENT_RATE, 2025, RATE)

    assert data.values == Rate(D("0.00229"))
    assert data.rounding == CENT
    assert T2043_PDF in data.sources


def test_2025_expense_threshold_is_25000_as_printed() -> None:
    data = SOURCE.get(EXPENSE_THRESHOLD, 2025, AMOUNT)

    assert data.values == Amount(D("25000"))
    assert data.rounding == CENT
    assert T2043_PDF in data.sources
