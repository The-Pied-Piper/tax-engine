"""The 2026 `ca-sk/age_income_threshold` dataset: provisional, the 2025 figure
43,066.00 x 1.02 (Worksheet SK428, line 3, 5008-d-25e.txt)
indexed by the 2026 factor (T4127 January 2026), rounded to the nearest dollar,
a half going up: 43,927.00. Replace it when the 2026 SK428 is published.

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
FAMILY = "ca-sk/age_income_threshold"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-d/5008-d-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 threshold 43066.00 x 1.02 (Saskatchewan's 2026 index factor, "
    "2.0%, T4127 (Jan 2026)) = 43927.32, rounded to the nearest dollar, a half going "
    "up, to 43927.00; unconfirmed, as the 2026 SK428 is not yet published."
)


def test_2026_age_income_threshold_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("43927.00"))


def test_2026_age_income_threshold_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_income_threshold_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_age_income_threshold_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = saskatchewan_packages().roots()[Namespace("ca-sk")]
    path = root / "parameters" / "age_income_threshold" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_income_threshold_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("43066.00"))
    assert data.sources != SOURCES
