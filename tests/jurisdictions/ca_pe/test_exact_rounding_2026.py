"""The 2026 `ca-pe/exact_rounding` dataset: the rule of a Prince Edward Island product or sum
that is not a dollars-and-cents box, so nothing is rounded (`rounding: none`). The Prince Edward
Island marginal rate on the return summary (a gated bracket rate, and the sum of the federal and
Prince Edward Island parts) uses it: a rate is an exact fraction, so the cent rule of
`ca-pe/cent_rounding` must not touch it.
The 2026 file is carried forward unchanged from 2025 (provisional)."""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_pe.support import (
    prince_edward_island_packages,
    prince_edward_island_parameter_parsers,
)

SOURCE = YamlParameterSource(
    prince_edward_island_packages().roots(), prince_edward_island_parameter_parsers()
)
FAMILY = "ca-pe/exact_rounding"
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
    root = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    lines = (root / "parameters" / "exact_rounding" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_provisional_line_is_the_one_of_the_ontario_2026_files() -> None:
    prince_edward_island = prince_edward_island_packages().roots()[Namespace("ca-pe")]
    ontario = Path(tax_engine.jurisdictions.ca_on.__file__).parent
    prince_edward_island_first = (
        (prince_edward_island / "parameters" / "exact_rounding" / "2026.yaml")
        .read_text()
        .splitlines()[0]
    )
    ontario_first = (
        (ontario / "parameters" / "marginal_rate_gate" / "2026.yaml").read_text().splitlines()[0]
    )

    assert prince_edward_island_first == ontario_first
