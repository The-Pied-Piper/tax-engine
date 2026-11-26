"""The 2025 `ca-pe/donations_credit_rate_line_51` dataset. The printed rate that line 51 multiplies
the Schedule 9 amount by.

Form text (Form PE428, CRA 5002-c-25e.txt): Line 51: Amount from line 13 of your federal Schedule
9 multiplied by 9.5% = The form states no rounding rule, so the figure rounds half-up to the cent
(the project's choice).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/donations_credit_rate_line_51"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def test_2025_donations_credit_rate_line_51_value() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.values == Rate(D("0.095"))


def test_2025_donations_credit_rate_line_51_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_donations_credit_rate_line_51_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, RATE)

    assert data.sources == (CRA_FORM_TEXT,)
