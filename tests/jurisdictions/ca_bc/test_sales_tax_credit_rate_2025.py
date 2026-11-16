"""The 2025 rate of `ca-bc/sales_tax_credit_rate`, checked against Form BC479 (2025), line 12.

Form BC479 (5010-TC, 2025), line 12: "Amount from line 8 ^ multiplied by 2% = ^". The printed
percentage is a rate of 0.02, read by line 12, which multiplies line 8 by it. Line 12 is a
dollars-and-cents box, so the product rounds half-up to the cent.
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
# British Columbia is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/sales_tax_credit_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-tc/5010-tc-25e.txt"


def test_2025_sales_tax_credit_rate_is_2_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.02"))


def test_2025_sales_tax_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_sales_tax_credit_rate_cites_form_bc479() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
