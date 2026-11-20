"""The 2026 `ca/exact_rounding` dataset: the rule of a federal form line the engine only carries
through, for an unprinted working step (not a line the form prints), so nothing is rounded
 (`rounding: none`).
The 2026 file is carried forward unchanged from 2025 (provisional)."""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/exact_rounding"
YEAR = 2026
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)


def test_the_exact_rounding_rounds_nothing() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == NO_ROUNDING
    assert data.tax_year == YEAR


def test_the_exact_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)
    original = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = Path(tax_engine.jurisdictions.ca.__file__).parent
    lines = (root / "parameters" / "exact_rounding" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")
