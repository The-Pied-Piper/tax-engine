"""The 2026 `ca-pe/basic_personal_amount` dataset, provisional.

Pins the 2026 figure, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/basic_personal_amount"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 "
    "form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jan 2026) Prince Edward Island "
    "change notice (the Government of Prince Edward Island announced on April 10, "
    "2025 an increase of the basic personal amount from 14,650 to 15,000 effective "
    "January 1, 2026) and in T4127 (Jul 2026) as the total claim amount when Form "
    "TD1PE is not filed (15,000); no rounding applied here."
)


def test_2026_basic_personal_amount_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("15000"))


def test_2026_basic_personal_amount_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_basic_personal_amount_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_basic_personal_amount_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    path = root / "parameters" / "basic_personal_amount" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_basic_personal_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("14650"))
    assert data.sources != SOURCES
