"""The 2025 `ca-on/medical_expense_attendant_care_maximum` dataset, from CRA 5006-PC "Ontario tax
information for 2025", section "Line 58689" (5006-pc-25e.txt): "If the amount you claimed for
medical expenses on your return includes an amount for attendant care expenses that was limited to
$10,000 ($20,000 in the year of death), the maximum Ontario claim for attendant care expenses is
$17,627 ($35,253 in the year of death)"

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


def test_2025_medical_expense_attendant_care_maximum_is_17627() -> None:
    data = SOURCE.get("ca-on/medical_expense_attendant_care_maximum", 2025, AMOUNT)

    assert data.values == Amount(D("17627"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
