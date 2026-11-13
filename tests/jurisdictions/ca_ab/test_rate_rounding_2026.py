"""The 2026 `ca-ab/rate_rounding` dataset: the rule of the Alberta return summary's average income
tax rate (`core/divide`, total payable over salary). It carries nothing but its rule, half-up to
0.0001: a rate as a fraction, so 0.1598 prints as 15.98%. The forms print no precision for this
figure, so the precision is the project's choice, recorded in the dataset header.
The 2026 file is carried forward unchanged from 2025 (provisional)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/rate_rounding"
YEAR = 2026
PROVISIONAL_HEADER = (
    "# Provisional: taken from the 2025 form text named in sources; to be confirmed against the "
    "2026 form text when CRA publishes it."
)


def test_the_rate_rounding_is_half_up_to_ten_thousandths() -> None:
    data = SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == RoundTo(Decimal("0.0001"), RoundingMode.HALF_UP)
    assert data.tax_year == YEAR


def test_the_rate_rounding_names_its_sources() -> None:
    assert SOURCE.get(FAMILY, YEAR, ROUNDING_ONLY).sources


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    carried = SOURCE.get(FAMILY, 2026, ROUNDING_ONLY)
    original = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert carried.values == original.values
    assert carried.rounding == original.rounding
    assert carried.sources == original.sources


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = alberta_packages().roots()[Namespace("ca-ab")]
    lines = (root / "parameters" / "rate_rounding" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_provisional_line_is_the_one_of_the_ontario_2026_files() -> None:
    alberta = alberta_packages().roots()[Namespace("ca-ab")]
    ontario = Path(tax_engine.jurisdictions.ca_on.__file__).parent
    alberta_first = (
        (alberta / "parameters" / "rate_rounding" / "2026.yaml").read_text().splitlines()[0]
    )
    ontario_first = (
        (ontario / "parameters" / "marginal_rate_gate" / "2026.yaml").read_text().splitlines()[0]
    )

    assert alberta_first == ontario_first
