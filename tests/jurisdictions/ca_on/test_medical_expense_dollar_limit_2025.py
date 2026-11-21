"""The 2025 `ca-on/medical_expense_dollar_limit` dataset, from Form ON428 (5006-c-25e.txt) line 40:
"Enter whichever is less: $2,885 or the amount on line 39."

The figure is a dollars-and-cents figure, so it rounds half-up to the cent, the project's choice, as
the form states no rounding rule.
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


def test_2025_medical_expense_dollar_limit_is_2885() -> None:
    data = SOURCE.get("ca-on/medical_expense_dollar_limit", 2025, AMOUNT)

    assert data.values == Amount(D("2885"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
