"""The 2025 rate of `ca-mb/geothermal_heat_pump_credit_rate`, checked against Form MB479 (5007-TC).

Form MB479, line 68: "Green energy equipment tax credit (manufacturer): Line 68 and line 61390:
7.5% of the adjusted cost of geothermal heat pumps". The printed percentage is a rate of 0.075,
read by line 68's multiplication; the line is a dollars-and-cents line, so the product rounds
half-up to the cent, the project's choice, as the form states no rounding rule. The form prints no
maximum for line 68.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
# Manitoba is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/geothermal_heat_pump_credit_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-tc/5007-tc-25e.txt"


def test_2025_geothermal_heat_pump_credit_rate_is_7_5_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.075"))


def test_2025_geothermal_heat_pump_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_geothermal_heat_pump_credit_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
