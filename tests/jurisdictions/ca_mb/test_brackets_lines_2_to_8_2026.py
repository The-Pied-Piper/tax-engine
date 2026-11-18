"""2026 `ca-mb/brackets_lines_2_to_8`, from T4127 (Jan 2026) Table 8.1 (Manitoba), provisional.

The 2026 Form MB428 (CRA 5007-c) text is not yet published, so the dataset cites T4127 and its
header says so. The thresholds (47,000 and 100,000) and rates (10.80%, 12.75%, 17.40%) are
unchanged from 2025 and `tax_at_start` is carried from the 2025 form's printed line 7 constants.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/brackets_lines_2_to_8"
T4127_URL = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/t4127-jan/t4127-01-26e.pdf"
PROVISIONAL_HEADER = (
    "# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text "
    "when CRA publishes it."
)
DERIVATION_HEADER = (
    "# Derivation: thresholds 47,000 and 100,000 and rates 10.80%, 12.75%, 17.40% as printed in "
    "T4127 (Jan 2026) Table 8.1 (Manitoba thresholds are not indexed); tax_at_start carried from "
    "the 2025 form's printed line 7 constants, which these thresholds and rates still reproduce."
)
COLUMNS = [
    (D("0.00"), D("0.108"), D("0.00")),
    (D("47000.00"), D("0.1275"), D("5076.00")),
    (D("100000.00"), D("0.174"), D("11833.50")),
]


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2026, BRACKETS).values


def test_2026_brackets_are_the_three_columns_from_t4127() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == COLUMNS


def test_2026_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2026, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2026_brackets_cite_t4127_only() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).sources == (T4127_URL,)


def test_2026_brackets_are_for_tax_year_2026() -> None:
    assert SOURCE.get(FAMILY, 2026, BRACKETS).tax_year == 2026


def test_2026_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


def test_2026_brackets_equal_the_2025_brackets() -> None:
    carried = SOURCE.get(FAMILY, 2026, BRACKETS)
    original = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert carried.values == original.values


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("47000.00", "0.00"),
        ("47000.01", "47000.00"),
        ("100000.00", "47000.00"),
        ("100000.01", "100000.00"),
        ("1000000.00", "100000.00"),
    ],
)
def test_the_column_is_the_one_t4127_gives_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = manitoba_packages().roots()[Namespace("ca-mb")]
    lines = (root / "parameters" / "brackets_lines_2_to_8" / "2026.yaml").read_text().splitlines()

    assert lines[0] == PROVISIONAL_HEADER
    assert lines[1] == DERIVATION_HEADER
