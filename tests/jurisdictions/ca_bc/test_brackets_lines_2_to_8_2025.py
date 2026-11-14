"""2025 `ca-bc/brackets_lines_2_to_8`, checked against Form BC428 (5010-C, 2025), Part A.

Form text (read 2026-11-14): "Column 1: Line 1 is $49,279 or less", "Line 3: 0.00"; "Column 2:
Line 1 is more than $49,279 but not more than $98,560", "Line 3: 49,279.00"; "Column 3: Line 1 is
more than $98,560 but not more than $113,158", "Line 3: 98,560.00"; "Column 4: Line 1 is more than
$113,158 but not more than $137,407", "Line 3: 113,158.00". The rates (5.06%, 7.7%, 10.5%, 12.29%)
and the line 7 constants (0.00, 2,493.52, 6,288.15, 7,820.94) are the ticket's printed figures; the
form text for them is to be confirmed (the ticket quotes only the lower bounds).

Each bracket holds the form's column: its lower bound (line 3), its rate and the printed tax at its
start (line 7), carried as printed. The dataset has no rounding rule. The table covers line 1 of
137,407.00 or less: its `up_to` is the form's printed boundary, 137,407.00.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/brackets_lines_2_to_8"
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5010-c/5010-c-25e.txt"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_four_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0.00"), D("0.0506"), D("0.00")),
        (D("49279.00"), D("0.077"), D("2493.52")),
        (D("98560.00"), D("0.105"), D("6288.15")),
        (D("113158.00"), D("0.1229"), D("7820.94")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_form_bc428() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.sources == (CRA_FORM_TEXT,)


def test_2025_brackets_stop_at_137407() -> None:
    assert _schedule().up_to == D("137407.00")


def test_the_table_covers_137407_and_not_a_cent_more() -> None:
    schedule = _schedule()

    assert schedule.covers(D("137407.00"))
    assert not schedule.covers(D("137407.01"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0.00"),
        ("49279.00", "0.00"),
        ("49279.01", "49279.00"),
        ("98560.00", "49279.00"),
        ("98560.01", "98560.00"),
        ("113158.00", "98560.00"),
        ("113158.01", "113158.00"),
        ("137407.00", "113158.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    column = _schedule().column_for(D(amount))

    assert column.lower == D(lower)
