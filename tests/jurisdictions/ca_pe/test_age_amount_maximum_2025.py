"""The 2025 `ca-pe/age_amount_maximum` dataset: the printed maximum of PE428 line 10.

Form text (Form PE428, CRA 5002-c-25e.txt): "Age amount (if you were born in 1960 or earlier) (use
Worksheet PE428) (maximum $6,510)". The maximum is claimed whole, so it is a `credit` dataset. The
form states no rounding rule, so it rounds half-up to the cent (the project's choice).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/age_amount_maximum"


def test_2025_maximum_is_6510() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("6510"))


def test_2025_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt",
    )
