"""The 2025 `ca-bc/home_renovation_expenses_maximum` dataset: the printed maximum of BC479 line 14.

Form text (Form BC479, CRA 5010-TC, 2025): "Line 14: Enter your home renovation expenses from line 5
of your Schedule BC(S12). (maximum $10,000)". The maximum is a figure of the form, not an input, so
it is a `credit` dataset claimed whole, like the Alberta pension income amount maximum. It rounds
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

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/home_renovation_expenses_maximum"


def test_2025_amount_is_10000() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("10000"))


def test_2025_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_amount_cites_the_bc479_text() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-tc/5010-tc-25e.txt"
        in data.sources
    )


def test_2025_amount_is_for_tax_year_2025() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.tax_year == 2025
