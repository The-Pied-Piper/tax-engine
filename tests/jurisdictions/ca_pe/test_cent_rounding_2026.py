"""The 2026 `ca-pe/cent_rounding` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/cent_rounding"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5002-c/5002-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed "
    "against the 2026 form text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: carried forward unchanged from the 2025 file; T4127 (Jan and Jul 2026)"
    " does not print this figure and the 2026 form is not yet published, so it is "
    "unconfirmed."
)


def test_2026_cent_rounding_value() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.values == RoundingOnly()


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)
    original = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_2026_cent_rounding_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_cent_rounding_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.sources == SOURCES


def test_2026_cent_rounding_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    path = root / "parameters" / "cent_rounding" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
