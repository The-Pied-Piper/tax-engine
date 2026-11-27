"""The 2026 `ca-sk/senior_supplementary_amount` dataset: provisional, the 2025 figure
2,028 x 1.02 + 500 (SK428 line 19, 5008-c-25e.txt)
indexed by the 2026 factor (T4127 January 2026), rounded to the nearest dollar,
a half going up: 2,569. Replace it when the 2026 SK428 is published.
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
FAMILY = "ca-sk/senior_supplementary_amount"
T4127 = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt"
YEAR = 2026


def test_2026_senior_supplementary_amount_is_2569() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.values == Credit(amount=D("2569"))


def test_2026_senior_supplementary_amount_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_senior_supplementary_amount_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, YEAR, CREDIT)

    assert data.sources == (CRA_FORM_TEXT, T4127)
