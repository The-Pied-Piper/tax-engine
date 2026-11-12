"""The 2025 table of `ca-ab/brackets_lines_9_to_15`, checked against Form AB428 (2025), Part A.

Form AB428 (5009-C, 2025), lines 9 to 15, prints three columns: "Line 1 is more than $181,481 but
not more than $241,974" (line 10: 181,481.00), "Line 1 is more than $241,974 but not more than
$362,961" (line 10: 241,974.00) and "Line 1 is more than $362,961" (line 10: 362,961.00). The rates
(13%, 14%, 15%) and the line 14 constants (17,553.04, 25,417.13, 42,355.31) are carried as printed:
no rounding rule, no computed or rounded start. The table's range is line 1 above 181,481.00: a base
at 181,481.00 falls in the table below (lines 2 to 8), so this table gives a blank there, and
181,481.01 is in the first column.

The low table's `up_to` (`ca-ab/brackets_lines_2_to_8`) must equal this table's first `from`, so
that every amount falls in exactly one of the two tables.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import AmountOutsideBracketRangeError
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_ab.support import alberta_packages, alberta_parameter_parsers

D = Decimal
# Alberta is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(alberta_packages().roots(), alberta_parameter_parsers())
FAMILY = "ca-ab/brackets_lines_9_to_15"


def test_2025_brackets_are_the_three_printed_columns() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    # Line 10 lower bound, line 12 rate, as printed.
    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D("181481.00"), D("0.13")),
        (D("241974.00"), D("0.14")),
        (D("362961.00"), D("0.15")),
    ]


def test_the_first_lower_bound_is_181481_which_the_low_table_ends_at() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("181481.00")


def test_the_tax_at_each_start_is_the_line_14_printed_constant() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert [b.tax_at_start for b in schedule.brackets] == [
        D("17553.04"),
        D("25417.13"),
        D("42355.31"),
    ]


def test_the_figures_are_used_as_printed_with_no_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_the_table_has_no_upper_end() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.up_to is None


@pytest.mark.parametrize("amount", ["0", "19835.00", "181480.99", "181481.00"])
def test_a_base_at_or_below_181481_is_outside_the_range(amount: str) -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert not schedule.covers(D(amount))
    with pytest.raises(AmountOutsideBracketRangeError):
        schedule.column_for(D(amount))


@pytest.mark.parametrize("amount", ["181481.01", "198926.00", "241974.00", "500000"])
def test_a_base_above_181481_is_in_the_range(amount: str) -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        # 181,481.01 is the first column, whose lower bound is 181,481.00.
        ("181481.01", "181481.00"),
        ("198926.00", "181481.00"),
        # A base at a column's upper bound is in that column ("not more than").
        ("241974.00", "181481.00"),
        ("241974.01", "241974.00"),
        ("362961.00", "241974.00"),
        ("362961.01", "362961.00"),
    ],
)
def test_the_schedule_gives_the_column_a_base_falls_in(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2025, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)


def test_the_low_tables_up_to_is_this_tables_first_from() -> None:
    low = SOURCE.get("ca-ab/brackets_lines_2_to_8", 2025, BRACKETS).values
    high = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert low.up_to == high.brackets[0].lower == D("181481.00")
