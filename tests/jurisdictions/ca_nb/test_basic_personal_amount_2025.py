"""The 2025 `ca-nb/basic_personal_amount` dataset, checked against Form NB428 (5004-C, 2025).

Form NB428 (CRA 5004-c-25e.txt): "Line 9 and line 58040: Basic personal amount Claim $13,396". The
amount is not income-tested, so it is a `credit` dataset. The figure is a dollars-and-cents figure,
so it rounds half-up to the cent, the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_packages,
    new_brunswick_parameter_parsers,
)

D = Decimal
# The source is built over the New Brunswick package list of `support.py`.
SOURCE = YamlParameterSource(
    new_brunswick_packages().roots(),
    new_brunswick_parameter_parsers(),
)
FAMILY = "ca-nb/basic_personal_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-c/5004-c-25e.txt"


def test_2025_basic_personal_amount_is_13396() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("13396"))


def test_2025_basic_personal_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_basic_personal_amount_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
