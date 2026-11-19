"""The 2025 `ca-nl/political_contribution_tax_credit_maximum` dataset, checked against Form NL428
(5001-C, 2025).

Form NL428 (CRA 5001-c-25e.txt): "Line 76: Newfoundland and Labrador political contribution tax
credit (use Worksheet NL428) (maximum $500)". The maximum is printed, so the dataset holds it as
printed, claimed whole: the `credit` kind. The figure rounds half-up to the cent, the project's
choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
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
FAMILY = "ca-nl/political_contribution_tax_credit_maximum"


def test_2025_political_contribution_tax_credit_maximum_is_500() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("500"))


def test_2025_political_contribution_tax_credit_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
