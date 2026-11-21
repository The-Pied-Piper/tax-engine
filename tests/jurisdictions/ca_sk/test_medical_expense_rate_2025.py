"""The 2025 `ca-sk/medical_expense_rate` dataset, Form SK428 (5008-c-25e.txt) line 45:
"Applicable rate 3%"

Rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)


def test_2025_medical_expense_rate_is_0_03() -> None:
    data = SOURCE.get("ca-sk/medical_expense_rate", 2025, RATE)

    assert data.values == Rate(D("0.03"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
