"""The 2025 rate of `ca-on/minimum_tax_rate`, checked against Form ON428 (2025), line 59.

Form ON428 (5006-C, 2025), line 59: "Amount from line 40427 of your return multiplied by 24.63% =".
The printed percentage is a rate of 0.2463; line 59 is a dollars-and-cents line, so the product
rounds half-up to the cent.
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
FAMILY = "ca-on/minimum_tax_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"


def test_2025_minimum_tax_rate_is_24_63_percent_rounded_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.2463"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_minimum_tax_rate_cites_form_on428() -> None:
    assert SOURCE.get(FAMILY, 2025, RATE).sources == (CRA_FORM_TEXT,)
