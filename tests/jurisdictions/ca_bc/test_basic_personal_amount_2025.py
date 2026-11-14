"""The 2025 `ca-bc/basic_personal_amount` dataset: the British Columbia basic personal amount.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 16 and line 58040: Basic personal amount Claim
$12,932". The amount is not income-tested, so it is a `credit` dataset. Line 58040 is a
dollars-and-cents box, so it rounds half-up to the cent (the project's choice, as the form states no
rounding rule). Only the BC428 text is cited here.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/basic_personal_amount"


def test_2025_amount_is_12932() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("12932"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_bc428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt"
        in data.sources
    )
