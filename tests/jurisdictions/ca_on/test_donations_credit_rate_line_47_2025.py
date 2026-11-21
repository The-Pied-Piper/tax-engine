"""The 2025 `ca-on/donations_credit_rate_line_47` dataset, Form ON428 line 47:
"... multiplied by 5.05% ="

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice,
as the form states no rounding rule.
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


def test_2025_donations_credit_rate_line_47_is_0_0505() -> None:
    data = SOURCE.get("ca-on/donations_credit_rate_line_47", 2025, RATE)

    assert data.values == Rate(D("0.0505"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
