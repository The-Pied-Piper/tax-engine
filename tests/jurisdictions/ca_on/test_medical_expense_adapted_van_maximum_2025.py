"""The 2025 `ca-on/medical_expense_adapted_van_maximum` dataset, from CRA 5006-PC "Ontario tax
information for 2025", section "Line 58689" (5006-pc-25e.txt): "The maximum Ontario claim for the
cost of a van adapted for transporting a patient who requires the use of a wheelchair is $8,813"

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice, as
the text states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)


def test_2025_medical_expense_adapted_van_maximum_is_8813() -> None:
    data = SOURCE.get("ca-on/medical_expense_adapted_van_maximum", 2025, AMOUNT)

    assert data.values == Amount(D("8813"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
