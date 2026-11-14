"""The 2025 rate of `ca-bc/farmers_food_donation_rate`, checked against Form BC428 (2025), line 59.

Form BC428 (5010-c-25e.txt), line 59: "Line 59 and line 58980: Amount of qualifying gifts also
claimed on line 57 multiplied by 25% = ^". The printed percentage is a rate of 0.25, read by line
59; line 59 is a dollars-and-cents line, so the product rounds half-up to the cent. The form prints
no rounding rule, so half-up follows the British Columbia credit rate dataset.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/farmers_food_donation_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt"


def test_2025_farmers_food_donation_rate_is_25_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))


def test_2025_farmers_food_donation_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_farmers_food_donation_rate_cites_the_form_bc428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
