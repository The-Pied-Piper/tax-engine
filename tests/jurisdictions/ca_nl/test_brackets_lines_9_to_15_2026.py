"""The 2026 `ca-nl/brackets_lines_9_to_15` dataset, provisional.

Pins the 2026 figures, rounding, sources, tax year and the two header comment lines of the file.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_nl.support import (
    newfoundland_packages,
    newfoundland_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/brackets_lines_9_to_15"
SOURCES = ("https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf",)
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form "
    "text when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds and rates as printed in T4127 (Jan 2026) Table 8.1, "
    "Newfoundland and Labrador row; tax_at_start calculated as the cumulative tax on the "
    "earlier brackets, rounded half-up to the cent (reproduces the 2025 printed "
    "constants), because the 2026 line 7 and line 14 constants are not yet published."
)


def test_2026_brackets_lines_9_to_15_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("223340.00"), D("0.198"), D("32811.03")),
        (D("285319.00"), D("0.208"), D("45082.88")),
        (D("570638.00"), D("0.213"), D("104429.23")),
        (D("1141275.00"), D("0.218"), D("225974.91")),
    ]
    assert data.values.up_to is None


def test_2026_brackets_lines_9_to_15_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING


def test_2026_brackets_lines_9_to_15_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.sources == SOURCES


def test_2026_brackets_lines_9_to_15_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "brackets_lines_9_to_15" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
