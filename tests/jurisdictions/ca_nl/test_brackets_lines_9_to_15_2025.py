"""The 2025 table of `ca-nl/brackets_lines_9_to_15`, checked against Form NL428 (2025), Part A.

Form NL428 (5001-C, 2025), lines 9 to 15, prints four columns: "Line 1 is more than $220,910 but not
more than $282,214" (line 10: 220,910.00), "Line 1 is more than $282,214 but not more than
$564,429" (line 10: 282,214.00), "Line 1 is more than $564,429 but not more than $1,128,858" (line
10: 564,429.00) and "Line 1 is more than $1,128,858" (line 10: 1,128,858.00). The rates (19.8%,
20.8%, 21.3%, 21.8%) and the line 14 constants (32,454.04, 44,592.23, 103,292.95, 223,516.33) are
carried as printed: no rounding rule, no computed or rounded start. The table's range is line 1
above 220,910.00: a base at 220,910.00 falls in the table below (lines 2 to 8), so this table gives
a blank there, and 220,910.01 is in the first column.

The low table's `up_to` (`ca-nl/brackets_lines_2_to_8`) must equal this table's first `from`, so
that every amount falls in exactly one of the two tables.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import AmountOutsideBracketRangeError
from tax_engine.domain.parameters.brackets import BRACKETS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_nl.support import newfoundland_packages, newfoundland_parameter_parsers

D = Decimal
# Newfoundland and Labrador is not in `registrations.JURISDICTIONS` yet, so the source is built
# over its own packages.
SOURCE = YamlParameterSource(newfoundland_packages().roots(), newfoundland_parameter_parsers())
FAMILY = "ca-nl/brackets_lines_9_to_15"


def test_2025_brackets_are_the_four_printed_columns() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    # Line 10 lower bound, line 12 rate, as printed.
    assert [(b.lower, b.rate) for b in data.values.brackets] == [
        (D("220910.00"), D("0.198")),
        (D("282214.00"), D("0.208")),
        (D("564429.00"), D("0.213")),
        (D("1128858.00"), D("0.218")),
    ]


def test_the_first_lower_bound_is_220910_which_the_low_table_ends_at() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert schedule.brackets[0].lower == D("220910.00")


def test_the_tax_at_each_start_is_the_line_14_printed_constant() -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert [b.tax_at_start for b in schedule.brackets] == [
        D("32454.04"),
        D("44592.23"),
        D("103292.95"),
        D("223516.33"),
    ]


def test_the_figures_are_used_as_printed_with_no_rounding() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_the_table_has_no_upper_end() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.up_to is None


@pytest.mark.parametrize("amount", ["0", "44192.00", "157792.00", "220909.99", "220910.00"])
def test_a_base_at_or_below_220910_is_outside_the_range(amount: str) -> None:
    schedule = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert not schedule.covers(D(amount))
    with pytest.raises(AmountOutsideBracketRangeError):
        schedule.column_for(D(amount))


@pytest.mark.parametrize("amount", ["220910.01", "282214.00", "1128858.00", "5000000"])
def test_a_base_above_220910_is_in_the_range(amount: str) -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).values.covers(D(amount))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        # 220,910.01 is the first column, whose lower bound is 220,910.00.
        ("220910.01", "220910.00"),
        # A base at a column's upper bound is in that column ("not more than").
        ("282214.00", "220910.00"),
        ("282214.01", "282214.00"),
        ("564429.00", "282214.00"),
        ("564429.01", "564429.00"),
        ("1128858.00", "564429.00"),
        ("1128858.01", "1128858.00"),
    ],
)
def test_the_schedule_gives_the_column_a_base_falls_in(amount: str, lower: str) -> None:
    column = SOURCE.get(FAMILY, 2025, BRACKETS).values.column_for(D(amount))

    assert column.lower == D(lower)


def test_the_low_tables_up_to_is_this_tables_first_from() -> None:
    low = SOURCE.get("ca-nl/brackets_lines_2_to_8", 2025, BRACKETS).values
    high = SOURCE.get(FAMILY, 2025, BRACKETS).values

    assert low.up_to == high.brackets[0].lower == D("220910.00")
