"""The 2025 `ca-sk/basic_personal_amount` dataset: the Saskatchewan basic personal amount.

Form text (Form SK428, CRA 5008-c-25e.txt): "Line 9 and line 58040: Basic personal amount Claim
$19,491". The amount is not income-tested, so it is a `credit` dataset. Line 58040 is a
dollars-and-cents box, so it rounds half-up to the cent (the project's choice, as the form states no
rounding rule).
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_sk.support import saskatchewan_packages, saskatchewan_parameter_parsers

SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/basic_personal_amount"


def test_2025_amount_is_19491() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("19491"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_sk428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt"
        in data.sources
    )
