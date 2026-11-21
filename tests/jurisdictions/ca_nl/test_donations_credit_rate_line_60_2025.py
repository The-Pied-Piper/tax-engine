"""The 2025 `ca-nl/donations_credit_rate_line_60` dataset, Form NL428 (5001-C).

Form NL428 (CRA 5001-c-25e.txt): "Line 60: Amount from line 14 of your federal Schedule 9
multiplied by 21.8% =". The printed percentage is a rate of 0.218. The figure is a
dollars-and-cents box, so it rounds half-up to the cent.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built over
# its own packages.
SOURCE = YamlParameterSource(
    newfoundland_packages().roots(),
    newfoundland_parameter_parsers(),
)
FAMILY = "ca-nl/donations_credit_rate_line_60"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


def test_2025_donations_credit_rate_line_60_is_0_218() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.218"))


def test_2025_donations_credit_rate_line_60_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_donations_credit_rate_line_60_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
