"""The 2026 `ca-sk/age_maximum` dataset: provisional, the 2025 figure
5,785.00 x 1.02 (Worksheet SK428, line 1, 5008-d-25e.txt)
indexed by the 2026 factor (T4127 January 2026), rounded to the nearest dollar,
a half going up: 5,901.00. Replace it when the 2026 SK428 is published.

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
FAMILY = "ca-sk/age_maximum"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5008-d/5008-d-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 5785.00 x 1.02 (Saskatchewan's 2026 index factor, "
    "2.0%, T4127 (Jan 2026)) = 5900.70, rounded to the nearest dollar, a half going "
    "up, to 5901.00; unconfirmed, as the 2026 SK428 is not yet published."
)


def test_2026_age_maximum_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("5901.00"))


def test_2026_age_maximum_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_age_maximum_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_age_maximum_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = saskatchewan_packages().roots()[Namespace("ca-sk")]
    path = root / "parameters" / "age_maximum" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_age_maximum_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("5785.00"))
    assert data.sources != SOURCES
