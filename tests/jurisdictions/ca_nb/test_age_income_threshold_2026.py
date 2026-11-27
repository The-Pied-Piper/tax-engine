"""The 2026 `ca-nb/age_income_threshold` dataset, Worksheet NB428
(5004-d-25e.txt), Line 3 "Income threshold 30,828.00": the printed figure,
claimed whole (the `credit` kind). Rounds half-up to the cent, the project's choice, as the form
states no rounding rule.
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
SOURCE = YamlParameterSource(
    new_brunswick_packages().roots(),
    new_brunswick_parameter_parsers(),
)
FAMILY = "ca-nb/age_income_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5004-d/5004-d-25e.txt"
YEAR = 2026


def test_2026_age_income_threshold_is_44945_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("44945.00"))


def test_2026_age_income_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_income_threshold_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
