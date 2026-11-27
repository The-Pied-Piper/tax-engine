"""The 2025 `ca-bc/age_maximum` dataset, Worksheet BC428
(5010-d-25e.txt), Line 1 "Maximum amount 5,799.00": the printed figure,
claimed whole (the `credit` kind). Rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
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

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-d/5010-d-25e.txt"
YEAR = 2025


def test_2025_age_maximum_is_5799_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("5799.00"))


def test_2025_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
