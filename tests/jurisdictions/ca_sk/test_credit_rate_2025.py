"""The 2025 rate of `ca-sk/credit_rate`, checked against Form SK428 (5008-C, 2025), line 52.

Form SK428 (CRA 5008-c), line 52: "Line 52: Saskatchewan non-refundable tax credit rate 10.5%". The
printed percentage is a rate of 0.105, read by line 53's multiplication; the line is a
dollars-and-cents line, so the product rounds half-up to the cent, the project's choice, as the
form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_sk.support import saskatchewan_packages, saskatchewan_parameter_parsers

D = Decimal
# Saskatchewan is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/credit_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt"


def test_2025_credit_rate_is_10_point_5_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.105"))


def test_2025_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_credit_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
