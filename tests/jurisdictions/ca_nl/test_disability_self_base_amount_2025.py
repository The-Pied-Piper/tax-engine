"""The 2025 amount of `ca-nl/disability_self_base_amount`, checked against Worksheet NL428
(5001-D, 2025), "Line 58440 - Disability amount for self".

Worksheet NL428, line 1: "Line 1: Base amount 7,467.00". The figure is printed, so the dataset holds
it as printed, the `credit` kind, because it is taken whole.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built
# over its own packages.
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/disability_self_base_amount"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-d/5001-d-25e.txt"


def test_2025_disability_self_base_amount_is_7467() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("7467.00"))


def test_2025_disability_self_base_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2025_disability_self_base_amount_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.sources == (CRA_FORM_TEXT,)
