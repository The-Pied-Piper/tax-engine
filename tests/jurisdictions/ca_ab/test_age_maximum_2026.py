"""The 2026 `ca-ab/age_maximum` dataset, Worksheet AB428 (5009-d-25e.txt), Line 1 "Maximum amount
6,221.00" (2025 text) indexed by Alberta's 2026 factor 1.02 (6,345.42, nearest dollar, halves up:
6,345.00), provisional, claimed whole (the `credit` kind). Rounds half-up to the cent, the
project's choice, as the form states no rounding rule.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/age_maximum"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5009-d/5009-d-25e.txt"
YEAR = 2026


def test_2026_age_maximum_is_6345_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("6345.00"))


def test_2026_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
