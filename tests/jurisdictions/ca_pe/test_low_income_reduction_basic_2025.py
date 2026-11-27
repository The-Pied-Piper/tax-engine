"""The 2025 `ca-pe/low_income_reduction_basic` dataset. The printed basic reduction of line 75.

Form text (Form PE428, CRA 5002-c-25e.txt): Line 75 and line 63370: Basic reduction Claim $350
The form states no rounding rule, so the figure rounds half-up to the cent (the project's
choice)."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/low_income_reduction_basic"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"


def test_2025_low_income_reduction_basic_value() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("350"))


def test_2025_low_income_reduction_basic_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_low_income_reduction_basic_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
    assert data.tax_year == 2025
