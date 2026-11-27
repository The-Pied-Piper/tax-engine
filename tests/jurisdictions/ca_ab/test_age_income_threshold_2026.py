"""The 2026 `ca-ab/age_income_threshold` dataset, Worksheet AB428 (5009-d-25e.txt), Line 3 "Income
threshold 46,308.00" (2025 text) indexed by Alberta's 2026 factor 1.02 (47,234.16, nearest dollar,
halves up: 47,234.00), provisional, claimed whole (the `credit` kind). Rounds half-up to the cent,
the project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/age_income_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"
YEAR = 2026


def test_2026_age_income_threshold_is_47234_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("47234.00"))


def test_2026_age_income_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_income_threshold_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
