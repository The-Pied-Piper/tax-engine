"""The 2025 `ca-nl/basic_personal_amount` dataset, checked against Form NL428 (5001-C, 2025).

Form NL428 (CRA 5001-c-25e.txt): "Line 16 and line 58040: Basic personal amount Claim $11,067". The
amount is not income-tested, so it is a `credit` dataset. The figure is a dollars-and-cents figure,
so it rounds half-up to the cent, the project's choice, as the form states no rounding rule.
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
FAMILY = "ca-nl/basic_personal_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt"


def test_2025_basic_personal_amount_is_11067() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("11067"))


def test_2025_basic_personal_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_basic_personal_amount_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
