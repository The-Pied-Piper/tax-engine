"""The 2025 Ontario ON428 medical expenses and donations datasets (Form ON428, 5006-c-25e.txt).

Line 40 "Enter whichever is less: $2,885 or the amount on line 39."
(`ca-on/medical_expense_dollar_limit`),
line 47 "... multiplied by 5.05% =" and line 48 "... multiplied by 11.16% =" (the two donations
rates). Each dollars-and-cents figure rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(),
    tax_engine.registrations.parameter_parsers(),
    tax_engine.registrations.units(),
)
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_medical_expense_dollar_limit_is_2885() -> None:
    data = SOURCE.get("ca-on/medical_expense_dollar_limit", 2025, AMOUNT)

    assert data.values == Amount(D("2885"))
    assert data.rounding == CENT


def test_2025_donations_credit_rates_are_5_05_and_11_16_percent() -> None:
    first = SOURCE.get("ca-on/donations_credit_rate_line_47", 2025, RATE)
    second = SOURCE.get("ca-on/donations_credit_rate_line_48", 2025, RATE)

    assert first.values == Rate(D("0.0505"))
    assert second.values == Rate(D("0.1116"))
    assert first.rounding == CENT and second.rounding == CENT
