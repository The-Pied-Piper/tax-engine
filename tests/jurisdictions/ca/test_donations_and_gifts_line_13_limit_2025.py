"""The 2025 `ca/donations_and_gifts_line_13_limit` dataset, checked against Schedule 9 line 13.

Schedule 9 (5000-S9, 2025) line 13: "Enter whichever is less: amount from line 12 or $200." The $200
is the printed figure, claimed whole through core/credit_amount. A dollars-and-cents figure, so it
rounds half-up to the cent, which changes nothing.
"""

from __future__ import annotations

from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/donations_and_gifts_line_13_limit"
SCHEDULE_9_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s9/5000-s9-25e.txt"


def test_2025_the_limit_is_200_claimed_whole() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("200.00"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_the_limit_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert SCHEDULE_9_TEXT in data.sources
    assert data.tax_year == 2025
