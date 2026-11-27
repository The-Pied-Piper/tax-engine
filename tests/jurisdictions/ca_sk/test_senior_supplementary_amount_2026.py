"""The 2026 `ca-sk/senior_supplementary_amount` dataset: provisional, the 2025 figure
2,028 x 1.02 + 500 (SK428 line 19, 5008-c-25e.txt)
indexed by the 2026 factor (T4127 January 2026), rounded to the nearest dollar,
a half going up: 2,569. Replace it when the 2026 SK428 is published.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(saskatchewan_packages().roots(), saskatchewan_parameter_parsers())
FAMILY = "ca-sk/senior_supplementary_amount"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-c/5008-c-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 2028 x 1.02 (Saskatchewan's 2026 index factor, 2.0%, "
    "T4127 (Jan 2026)) + 500 (the Saskatchewan Affordability Act's yearly $500 "
    "addition: 2025's figure was the indexed 2024 amount plus 500; the +500 for 2026 "
    "is not yet checked against the Act's text) = 2568.56, rounded to the nearest "
    "dollar, a half going up, to 2569; unconfirmed, as the 2026 SK428 is not yet "
    "published."
)


def test_2026_senior_supplementary_amount_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("2569"))


def test_2026_senior_supplementary_amount_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_senior_supplementary_amount_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_senior_supplementary_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = saskatchewan_packages().roots()[Namespace("ca-sk")]
    path = root / "parameters" / "senior_supplementary_amount" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_senior_supplementary_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("2028"))
    assert data.sources != SOURCES
