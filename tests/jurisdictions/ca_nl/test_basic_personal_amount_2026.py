"""The 2026 `ca-nl/basic_personal_amount` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/basic_personal_amount"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jul/t4127-jul-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jul 2026); to be confirmed against the 2026 form "
    "text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: figure as printed in T4127 (Jul 2026) Newfoundland and Labrador change"
    " notice (the Government of Newfoundland and Labrador announced on April 29, 2026 an "
    "increase of the basic personal amount from 11,188 to 13,094 effective January 1, "
    "2026; the 15,000 printed there is the prorated payroll amount for July to December, "
    "not the annual amount); no rounding applied here."
)


def test_2026_basic_personal_amount_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("13094"))


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
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "basic_personal_amount" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_basic_personal_amount_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("11067"))
    assert data.sources != SOURCES
