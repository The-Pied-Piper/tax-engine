"""The 2025 Ontario farmers' food donation credit rate, checked against CRA's ON428, line 87.

2025 Form ON428 (form 5006-C), line 87 "Line 87 and line 62150: Enter the amount of qualifying
donations that have also been claimed as a charitable donation. multiplied by 25% =". The 25% is a
rate (the `rate` kind), and line 87 a dollars-and-cents box, so the product is rounded half-up to
the cent.
"""

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
FOOD_RATE = "ca-on/farmers_food_donation_rate"


def test_2025_farmers_food_donation_rate_is_25_percent() -> None:
    data = SOURCE.get(FOOD_RATE, 2025, RATE)

    assert data.values == Rate(D("0.25"))
    # ON428 line 87, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
