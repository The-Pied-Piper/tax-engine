"""The 2025 amount of `ca-nl/age_income_threshold`, checked against Worksheet NL428 (5001-D,
2025), "Line 58080 - Age amount".

Worksheet NL428, line 3: "Line 3: Income threshold 38,712.00". The threshold is printed, so the
dataset holds it as printed, the `credit` kind as `ca/age_income_threshold` does, because it is a
printed amount taken whole.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/age_income_threshold"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-d/5001-d-25e.txt"


def test_2025_age_income_threshold_is_38712() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("38712.00"))


def test_2025_age_income_threshold_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_age_income_threshold_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
