"""The 2026 `ca-sk/age_maximum` dataset: provisional, the 2025 figure
5,785.00 x 1.02 (Worksheet SK428, line 1, 5008-d-25e.txt)
indexed by the 2026 factor (T4127 January 2026), rounded to the nearest dollar,
a half going up: 5,901.00. Replace it when the 2026 SK428 is published.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    saskatchewan_packages().roots(),
    saskatchewan_parameter_parsers(),
)
FAMILY = "ca-sk/age_maximum"
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-d/5008-d-25e.txt"
YEAR = 2026


def test_2026_age_maximum_is_5901_00() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("5901.00"))


def test_2026_age_maximum_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT, T4127)
