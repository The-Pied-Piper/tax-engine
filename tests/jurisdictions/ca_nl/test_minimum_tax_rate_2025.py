"""The 2025 rate of `ca-nl/minimum_tax_rate`, checked against Form NL428 (5001-C, 2025).

Form NL428, line 68 and line 61540: the amount from line 40427 of the return "multiplied by 60%
=". Line 71: the amount from line 14 of Part 7 of Form T691 "multiplied by 60% =". The printed
percentage is a rate of 0.6, read by both multiplications; each line is a dollars-and-cents line,
so the product rounds half-up to the cent, the project's choice, as the form states no rounding
rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built
# over its own packages.
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/minimum_tax_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


def test_2025_minimum_tax_rate_is_60_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.6"))


def test_2025_minimum_tax_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_minimum_tax_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
