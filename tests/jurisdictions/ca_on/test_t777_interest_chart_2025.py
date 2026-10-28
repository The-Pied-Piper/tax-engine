"""The datasets of Guide T4044 (2025) "Available interest expense for passenger vehicles or
zero-emission passenger vehicles chart", read from the parameter source."""

from __future__ import annotations

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.amount import AMOUNT, Amount
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_on.end_to_end.support import D

SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
T4044_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4044/t4044-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_daily_interest_limit_is_10_00() -> None:
    # Line B "$10 multiplied by the number of days for which interest was paid".
    data = SOURCE.get("ca/t777_interest_daily_limit", 2025, AMOUNT)

    assert data.values == Amount(D("10.00"))
    assert data.rounding == CENT
    assert T4044_TXT in data.sources
