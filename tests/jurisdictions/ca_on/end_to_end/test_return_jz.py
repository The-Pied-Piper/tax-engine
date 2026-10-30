"""CA-ON 2025 end to end: return jz, Form T2017 (2025), "Summary of Reserves on Dispositions of
Capital Property", Part 1, lines 14 and 26.

Form T2017 (2025), page 2, line 26 (66960): "Amount of 2024 reserve for dispositions of property
after 2020, other than dispositions listed on lines 66843, 66883, 66910, and 66930 (lines 66990 and
67058 of Form T2017 for 2024 minus amounts reported at line 66937 of Form T2017 for 2025)". The 2024
figure is the starting input; line 26 is that figure less line 23 (66937), signed, since the form
prints no floor on it. Form T2017 (2025), page 1, line 14 (66905): "Enter the amount of the most
recent reserves claimed on line 66850." It is entered, and no line of the form reads it.

The worked return `returns/2025_return_jz.yaml` (a 2024 figure of 5,000.00, line 23 of 1,200.00 and
line 14 of 7,500.00) is checked by `test_worked_returns.py`. This module reads the lines the worked
return does not export (line 26 and the lines it feeds), and the refusals and the negative line 26
the worked return does not express.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    T2017_LINE_6,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_25,
    T2017_LINE_26,
    T2017_LINE_28,
    T2017_LINE_29,
    T2017_LINE_31,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

SUMMARY = "ca/t2017"

# The figures of return JZ, by line number: line 14 (the most recent reserve claimed), line 23 (the
# 2025 amount that line 26 is less), and line 26 (the 2024 figure of line 26).
AMOUNTS: Mapping[int, str] = {14: "7500", 23: "1200", 26: "5000"}

# The lines of Part 1 that the figures of return JZ reach: line 26 and the lines it feeds.
LINES_FED_BY_26 = (
    T2017_LINE_6,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_25,
    T2017_LINE_26,
    T2017_LINE_28,
    T2017_LINE_29,
    T2017_LINE_31,
)


def run(*, amounts: Mapping[int, str] = AMOUNTS) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of Part 1, with the figures given and no dispositions."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t2017_amounts=amounts,
        t2017_rows={},
    )
    return service().compute(CA_ON, 2025, *artifacts)


def summary(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[SUMMARY]
    return worksheet


# --- line 26: the 2024 figure less line 23 ------------------------------------------------------


def test_line_26_is_the_2024_figure_of_5000_less_line_23_of_1200() -> None:
    assert summary().get(T2017_LINE_26).value == D("3800")


def test_line_25_is_line_23_of_1200_as_line_24_is_not_entered() -> None:
    assert summary().get(T2017_LINE_25).value == D("1200")


def test_line_28_is_line_26_less_line_27_which_is_not_entered() -> None:
    assert summary().get(T2017_LINE_28).value == D("3800")


def test_line_29_adds_lines_19_22_25_and_28_to_5000() -> None:
    assert summary().get(T2017_LINE_29).value == D("5000")


def test_line_31_is_line_29_with_line_30_not_entered_and_is_5000() -> None:
    assert summary().get(T2017_LINE_31).value == D("5000")


def test_lines_6_12_and_13_are_zero_when_no_line_1_or_7_is_entered() -> None:
    found = summary()

    assert found.get(T2017_LINE_6).value == D("0")
    assert found.get(T2017_LINE_12).value == D("0")
    assert found.get(T2017_LINE_13).value == D("0")


def test_a_2024_figure_equal_to_line_23_gives_line_26_of_zero() -> None:
    assert summary(amounts={26: "1200", 23: "1200"}).get(T2017_LINE_26).value == D("0")


# --- line 26 below zero is signed, not floored ----------------------------------------------------


def test_a_2024_figure_below_line_23_gives_a_negative_line_26_and_is_not_floored() -> None:
    found = summary(amounts={26: "1000", 23: "1200"})

    assert found.get(T2017_LINE_26).value == D("-200")
    assert found.get(T2017_LINE_28).value == D("-200")
    assert found.get(T2017_LINE_29).value == D("1000")
    assert found.get(T2017_LINE_31).value == D("1000")


# --- line 14: entered, read by nothing ----------------------------------------------------------


def test_line_14_changes_none_of_the_lines_of_part_1_it_could_reach() -> None:
    with_14 = summary(amounts=AMOUNTS)
    without_14 = summary(amounts={**AMOUNTS, 14: "0"})

    for kind in LINES_FED_BY_26:
        assert with_14.get(kind).value == without_14.get(kind).value, kind.identifier


def test_line_14_is_accepted_as_entered_without_a_line_26_figure() -> None:
    found = summary(amounts={14: "7500"})

    assert found.get(T2017_LINE_26).value == D("0")
    assert found.get(T2017_LINE_31).value == D("0")


# --- the refusals of a negative amount ----------------------------------------------------------


def test_a_negative_line_14_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        run(amounts={**AMOUNTS, 14: "-1"})


def test_a_negative_2024_figure_of_line_26_is_refused() -> None:
    with pytest.raises(NegativeArtifactError):
        run(amounts={**AMOUNTS, 26: "-1"})
