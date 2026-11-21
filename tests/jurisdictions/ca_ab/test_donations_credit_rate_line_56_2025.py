"""The 2025 `ca-ab/donations_credit_rate_line_56` dataset, checked against
Form AB428 (5009-c, 2025).

Form AB428 (CRA 5009-c-25e.txt), line 56: "Line 56: Amount from line 14 of your federal Schedule 9
multiplied by 21% =". The rate is a printed percentage, the `rate`
kind. The product it feeds is a dollars-and-cents box, so it rounds half-up to the cent, the
project's choice, as the form states no rounding rule.
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
FAMILY = "ca-ab/donations_credit_rate_line_56"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-c/5009-c-25e.txt"


def test_2025_donations_credit_rate_line_56_is_21_percent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.21"))


def test_2025_donations_credit_rate_line_56_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_donations_credit_rate_line_56_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
