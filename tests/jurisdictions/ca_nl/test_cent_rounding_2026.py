"""The 2026 `ca-nl/cent_rounding` dataset, provisional.

Pins the 2026 figures, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
SOURCE = YamlParameterSource(
    newfoundland_packages().roots(),
    newfoundland_parameter_parsers(),
    newfoundland_units(),
)
FAMILY = "ca-nl/cent_rounding"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5001-c/5001-c-25e.txt",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be c"
    "onfirmed against the 2026 form text when CRA publishes it."
)


def _file(year: int) -> Path:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    return root / "parameters" / FAMILY.split("/")[1] / f"{year}.yaml"


def test_2026_cent_rounding_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)
    original = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert carried.tax_year == 2026
    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_2026_cent_rounding_sources() -> None:
    assert SOURCE.get(FAMILY, 2026, ROUNDING_ONLY).sources == SOURCES


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file(2026).read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_file_sits_beside_the_2025_file() -> None:
    assert _file(2025).is_file()
    assert _file(2026).is_file()
