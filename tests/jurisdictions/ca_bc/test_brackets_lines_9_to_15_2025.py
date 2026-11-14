"""The 2025 table of `ca-bc/brackets_lines_9_to_15`, checked against Form BC428 (2025), Part A.

Form BC428 (5010-C, 2025), lines 9 to 15, prints three columns: "Column 1: Line 1 is more than
$137,407 but not more than $186,306  Line 10: 137,407.00", "Column 2: Line 1 is more than $186,306
but not more than $259,829  Line 10: 186,306.00" and "Column 3: Line 1 is more than $259,829
Line 10: 259,829.00". The rates (14.7%, 16.8%, 20.5%) and the line 14 constants (10,801.15,
17,989.30, 30,341.16) are the ticket's figures, carried as printed: no rounding rule, no computed or
rounded start. The table's range is line 1 above 137,407.00: a base at 137,407.00 is outside it, so
this table gives a blank there, and 137,407.01 is in the first column.

Not tested here: the low table's `up_to` (`ca-bc/brackets_lines_2_to_8`) equal to this table's first
`from`. That table is built by a parallel change; add the check when it lands.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import AmountOutsideBracketRangeError
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
# British Columbia is not in `registrations.JURISDICTIONS` yet; the source uses its own packages.
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/brackets_lines_9_to_15"


def test_2025_brackets_are_the_three_printed_columns() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    # Line 10 lower bound, line 12 rate, as printed.
    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D("137407.00"), D("0.147")),
        (D("186306.00"), D("0.168")),
        (D("259829.00"), D("0.205")),
    ]


def test_the_first_lower_bound_is_137407() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("137407.00")


def test_the_tax_at_each_start_is_the_line_14_printed_constant() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert [b.tax_at_start for b in schedule.brackets] == [
        D("10801.15"),
        D("17989.30"),
        D("30341.16"),
    ]


def test_the_figures_are_used_as_printed_with_no_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_the_table_has_no_upper_end() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.up_to is None


@pytest.mark.parametrize("amount", ["0", "16865.00", "137406.99", "137407.00"])
def test_a_base_at_or_below_137407_is_outside_the_range(amount: str) -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert not schedule.covers(D(amount))
    with pytest.raises(AmountOutsideBracketRangeError):
        schedule.column_for(D(amount))


@pytest.mark.parametrize("amount", ["137407.01", "198926.00", "259829.00", "500000"])
def test_a_base_above_137407_is_in_the_range(amount: str) -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        # 137,407.01 is the first column, whose lower bound is 137,407.00.
        ("137407.01", "137407.00"),
        ("160000.00", "137407.00"),
        # A base at a column's upper bound is in that column ("not more than").
        ("186306.00", "137407.00"),
        ("186306.01", "186306.00"),
        ("259829.00", "186306.00"),
        ("259829.01", "259829.00"),
    ],
)
def test_the_schedule_gives_the_column_a_base_falls_in(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2025, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)
