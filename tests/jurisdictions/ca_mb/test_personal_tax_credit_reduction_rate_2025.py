"""The 2025 rate of `ca-mb/personal_tax_credit_reduction_rate`, checked against form MB479 (5007-TC,
2025).

Form MB479, line 18: "Line 18: Amount from line 6 above multiplied by 1% =". The printed
percentage is a rate of 0.01, read by line 18's multiplication; the line is a dollars-and-cents
line, so the product rounds half-up to the cent, the project's choice, as the form states no
rounding rule.
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
FAMILY = "ca-mb/personal_tax_credit_reduction_rate"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-tc/5007-tc-25e.txt"


def test_2025_personal_tax_credit_reduction_rate_is_1_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.01"))


def test_2025_personal_tax_credit_reduction_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_personal_tax_credit_reduction_rate_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
