"""The 2026 `ca-nl/brackets_lines_2_to_8` dataset, provisional.

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
FAMILY = "ca-nl/brackets_lines_2_to_8"
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


def test_2026_brackets_lines_2_to_8_are_the_t4127_thresholds_and_rates() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.087"), D("0")),
        (D("44678.00"), D("0.145"), D("3886.99")),
        (D("89354.00"), D("0.158"), D("10365.01")),
        (D("159528.00"), D("0.178"), D("21452.50")),
    ]
    assert data.values.up_to == D("223340.00")


def test_the_low_table_ends_where_the_high_table_starts() -> None:
    low = SOURCE.get(FAMILY, 2026, BRACKETS).values
    high = SOURCE.get("ca-nl/brackets_lines_9_to_15", 2026, BRACKETS).values

    assert low.up_to == high.brackets[0].lower


def test_2026_brackets_lines_2_to_8_rounding() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING


def test_2026_brackets_lines_2_to_8_sources() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.sources == SOURCES


def test_2026_brackets_lines_2_to_8_is_for_tax_year_2026() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = newfoundland_packages().roots()[Namespace("ca-nl")]
    path = root / "parameters" / "brackets_lines_2_to_8" / "2026.yaml"
    lines = path.read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER


def test_2025_brackets_lines_2_to_8_is_unchanged() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.087"), D("0.00")),
        (D("44192.00"), D("0.145"), D("3844.70")),
        (D("88382.00"), D("0.158"), D("10252.25")),
        (D("157792.00"), D("0.178"), D("21219.03")),
    ]
    assert data.sources != SOURCES
