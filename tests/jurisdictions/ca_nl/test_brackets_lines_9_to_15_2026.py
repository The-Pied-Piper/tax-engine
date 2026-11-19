"""The 2026 `ca-nl/brackets_lines_9_to_15` dataset, provisional.

Pins the 2026 figures, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
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
FAMILY = "ca-nl/brackets_lines_9_to_15"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against th"
    "e 2026 form text when CRA publishes it."
)


def _file(year: int) -> Path:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    return root / "parameters" / FAMILY.split("/")[1] / f"{year}.yaml"


def test_2026_brackets_lines_9_to_15_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.tax_year == 2026
    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("223340.00"), D("0.198"), D("32811.03")),
        (D("285319.00"), D("0.208"), D("45082.88")),
        (D("570638.00"), D("0.213"), D("104429.23")),
        (D("1141275.00"), D("0.218"), D("225974.91")),
    ]
    assert data.values.up_to is None
    assert data.rounding == NO_ROUNDING


def test_the_tax_at_each_start_is_the_cumulative_tax_of_the_earlier_brackets() -> None:
    rows = SOURCE.get("ca-nl/brackets_lines_2_to_8", 2026, BRACKETS).values.brackets + (
        SOURCE.get("ca-nl/brackets_lines_9_to_15", 2026, BRACKETS).values.brackets
    )
    tax = D("0")
    for earlier, later in zip(rows, rows[1:], strict=False):
        tax += (later.lower - earlier.lower) * earlier.rate
        assert later.tax_at_start == tax.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def test_2026_brackets_lines_9_to_15_sources() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == SOURCES


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    lines = _file(2026).read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1].startswith("# Derivation: ")


def test_the_2026_file_sits_beside_the_2025_file() -> None:
    assert _file(2025).is_file()
    assert _file(2026).is_file()
