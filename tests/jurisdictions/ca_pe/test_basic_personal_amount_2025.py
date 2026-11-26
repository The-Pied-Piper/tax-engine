"""The 2025 `ca-pe/basic_personal_amount` dataset: the Prince Edward Island basic personal amount.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 9 and line 58040: Basic personal amount Claim
$14,650". The amount is not income-tested, so it is a `credit` dataset. The form states no rounding
rule, so it rounds half-up to the cent (the project's choice).
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
FAMILY = "ca-pe/basic_personal_amount"


def test_2025_amount_is_14650() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("14650"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt"
        in data.sources
    )
