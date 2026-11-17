"""2025 `ca-mb/brackets_lines_2_to_8`, checked against Form MB428 (CRA 5007-C, 2025), Part A.

Form text (read 2026-11-14, https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt):
"Column 1: Line 1 is $47,000 or less", "Line 3: 0.00", "Line 5: Rate 10.8%", "Line 7: 0.00";
"Column 2: Line 1 is more than $47,000 but not more than $100,000", "Line 3: 47,000.00",
"Line 5: Rate 12.75%", "Line 7: 5,076.00"; "Column 3: Line 1 is more than $100,000",
"Line 3: 100,000.00", "Line 5: Rate 17.4%", "Line 7: 11,833.50".

Each bracket holds the form's column: its lower bound (line 3), its rate (line 5) and the printed
tax at its start (line 7), carried as printed. The dataset has no rounding rule. Column 3 has no
upper boundary, so the schedule has no `up_to` and covers every amount.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_mb.support import manitoba_packages, manitoba_parameter_parsers

D = Decimal
# Manitoba is not in `registrations.JURISDICTIONS` yet, so the source is built over its own
# packages.
SOURCE = YamlParameterSource(manitoba_packages().roots(), manitoba_parameter_parsers())
FAMILY = "ca-mb/brackets_lines_2_to_8"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_three_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.108"), D("0.00")),
        (D("47000.00"), D("0.1275"), D("5076.00")),
        (D("100000.00"), D("0.174"), D("11833.50")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_mb428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_have_no_upper_boundary() -> None:
    schedule = _schedule()

    assert schedule.up_to is None
    assert not schedule.has_range


@pytest.mark.parametrize("amount", ["0.00", "100000.00", "100000.01", "500000.00", "99999999.99"])
def test_the_table_covers_every_amount(amount: str) -> None:
    assert _schedule().covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("47000.00", "0.00"),
        ("47000.01", "47000.00"),
        ("100000.00", "47000.00"),
        ("100000.01", "100000.00"),
        ("500000.00", "100000.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)
