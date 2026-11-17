"""The 2025 `ca-bc/political_contribution_tax_credit_maximum` dataset: BC428 line 84's maximum.

Form text (Form BC428, CRA 5010-c-25e.txt line 285-286): "Line 84: British Columbia political
contribution tax credit (use Worksheet BC428) (maximum $500)". The maximum is a figure of the form,
not an input, so it is a `credit` dataset claimed whole, like the basic personal amount. It rounds
half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-bc/political_contribution_tax_credit_maximum"


def test_2025_amount_is_500() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=Decimal("500"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(Decimal("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_bc428_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt",
    )


def test_2025_amount_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.tax_year == 2025
