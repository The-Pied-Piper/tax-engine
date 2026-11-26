"""The 2025 `ca-pe/spouse_or_common_law_partner_amount_maximum` dataset: the printed maximum of
PE428 line 13.

Form text (Form PE428, CRA 5002-c-25e.txt): "Line 11 minus line 12 (if negative, enter "0") (maximum
$12,443)". The maximum is claimed whole, so it is a `credit` dataset. The form states no rounding
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
FAMILY = "ca-pe/spouse_or_common_law_partner_amount_maximum"


def test_2025_maximum_is_12443() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("12443"))


def test_2025_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_maximum_cites_the_pe428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt",
    )
