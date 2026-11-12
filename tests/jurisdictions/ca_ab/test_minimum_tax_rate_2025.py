"""The 2025 rate of `ca-ab/minimum_tax_rate`, checked against Form AB428 (2025), lines 64 and 67.

Form AB428 (5009-C, 2025), line 64: "Amount from line 40427 of your return multiplied by 35% = ".
The printed percentage is a rate of 0.35, read by line 64 and by line 67; both are
dollars-and-cents lines, so the product rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/minimum_tax_rate"


def test_2025_minimum_tax_rate_is_35_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.35"))


def test_2025_minimum_tax_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
