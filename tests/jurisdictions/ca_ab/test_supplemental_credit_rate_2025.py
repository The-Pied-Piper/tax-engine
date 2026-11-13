"""The 2025 rate of `ca-ab/supplemental_credit_rate`, checked against Worksheet AB428, line 8.

Worksheet AB428 (5009-d-25e.txt), line 8: "Line 8: Applicable rate 25%". The printed percentage is a
rate of 0.25, read by line 9 (line 7 multiplied by it); line 9 is a dollars-and-cents line, so the
product rounds half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-ab/supplemental_credit_rate"
CRA_WORKSHEET_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"


def test_2025_supplemental_credit_rate_is_25_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.25"))


def test_2025_supplemental_credit_rate_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_supplemental_credit_rate_cites_the_worksheet_ab428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_WORKSHEET_TEXT,)
