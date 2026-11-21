"""The 2025 `ca-on/medical_expense_rate` dataset: 3%, Form ON428 line 38 "Applicable rate 3%"."""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)


def test_2025_medical_expense_rate_is_3_percent() -> None:
    data = SOURCE.get("ca-on/medical_expense_rate", 2025, RATE)

    assert data.values == Rate(D("0.03"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
