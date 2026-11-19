"""The 2026 `ca-nl/disability_self_care_threshold` dataset, provisional.

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
FAMILY = "ca-nl/disability_self_care_threshold"
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-d/5001-d-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",
)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: 2025 amount 2987.00 x 1.011 (Newfoundland and Labrador's index rate in"
    " T4127 (Jan 2026) Table 8.2; applied to the 2025 basic amount 11,067 it gives the "
    "printed 11,188) = 3019.857, rounded down to 3019.00 (the project ruling for "
    "provisional indexed amounts); unconfirmed, as the 2026 NL428 is not yet published."
)


def test_2026_disability_self_care_threshold_value() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("3019.00"))


def test_2026_disability_self_care_threshold_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_disability_self_care_threshold_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == SOURCES


def test_2026_disability_self_care_threshold_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "disability_self_care_threshold" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_disability_self_care_threshold_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, CREDIT)

    assert data.values == Credit(amount=D("2987.00"))
    assert data.sources != SOURCES
