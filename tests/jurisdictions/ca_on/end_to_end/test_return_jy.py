"""CA-ON 2025 end to end: return jy, Form T2017 (2025), "Summary of Reserves on Dispositions of
Capital Property", Part 1, as its own forms, with the later-year bound.

Form T2017 (2025), page 3: "You do not have to claim the maximum reserve in a tax year (Year A).
However, the amount you claim in a later year (Year B) cannot be more than the amount you claimed
for that property in the previous year (Year A)." A row in a year after its disposition (1 or more
years after it) is therefore bounded by the lesser of its maximum and the reserve claimed for the
property in the previous year; a claim above that limit is refused, not capped. A row in its year of
disposition is bounded by its maximum alone, and its previous-year claim is not read.

The worked return `returns/2025_return_jy.yaml` (dispositions on lines 2, 8, 17 and 27, in the
4th, 2nd and 1st years after the disposition (two rows on line 27: the 1st year and the year of
disposition), on the four-year and the nine-year tables) is checked by `test_worked_returns.py`.
This module computes each row on its own, and the refusals the worked return cannot express."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    T2017_LINE_5,
    T2017_LINE_6,
    T2017_LINE_11,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_29,
    T2017_LINE_31,
    T2017_RESERVE_CLAIM_LIMIT,
    T2017_RESERVE_LATER_YEAR,
    T2017_RESERVE_LATER_YEAR_MAXIMUM,
    T2017_RESERVE_MAXIMUM,
    T2017_ROW_RESERVE,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

SUMMARY = "ca/t2017"

# The dispositions of return JY, chosen figures, by reserve line. Line 2 is of the nine-year kind,
# line 8 of the four-year kind (nine_year 0), line 17 is nine-year, line 27 four-year.
ROW_2 = {
    "capital_gain": "100000",
    "payable": "100000",
    "proceeds": "200000",
    "years": 4,
    "claimed": "50000",
    "previous": "60000",
    "nine_year": 1,
}
ROW_8 = {
    "capital_gain": "50000",
    "payable": "20000",
    "proceeds": "100000",
    "years": 2,
    "claimed": "4000",
    "previous": "4000",
    "nine_year": 0,
}
ROW_17 = {
    "capital_gain": "20000",
    "payable": "10000",
    "proceeds": "40000",
    "years": 1,
    "claimed": "3000",
    "previous": "3000",
}
# The first of two dispositions on line 27: one year after it, its previous claim above the maximum.
ROW_27_LATER = {
    "capital_gain": "10000",
    "payable": "10000",
    "proceeds": "10000",
    "years": 1,
    "claimed": "6000",
    "previous": "9000",
}
# The second: in its year of disposition, so its previous claim is 0 and is not read.
ROW_27_DISPOSED = {
    "capital_gain": "10000",
    "payable": "5000",
    "proceeds": "10000",
    "years": 0,
    "claimed": "5000",
    "previous": "0",
}
ROWS: Mapping[int, tuple[Mapping[str, Any], ...]] = {
    2: (ROW_2,),
    8: (ROW_8,),
    17: (ROW_17,),
    27: (ROW_27_LATER, ROW_27_DISPOSED),
}
# The 2024 figures of return JY, by line number.
AMOUNTS: Mapping[int, str] = {1: "10000", 7: "20000", 16: "4000", 26: "1000", 30: "2000"}


def form_name(line: int) -> str:
    return f"ca/t2017_line_{line}_reserve"


def run(
    *,
    amounts: Mapping[int, str] = AMOUNTS,
    rows: Mapping[int, tuple[Mapping[str, Any], ...]] = ROWS,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of Part 1, with the 2024 figures and the rows given."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t2017_amounts=amounts,
        t2017_rows=rows,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def summary(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[SUMMARY]
    return worksheet


def row(line: int, **overrides: Any) -> tuple[Worksheet, ...]:
    return run(**overrides)[form_name(line)]


def one_row(line: int, record: Mapping[str, Any]) -> Worksheet:
    (worksheet,) = row(line, rows={line: (record,)})
    return worksheet


# --- the later-year bound: accepted claims -------------------------------------------------------


def test_a_claim_equal_to_the_previous_year_claim_is_accepted() -> None:
    worksheet = one_row(8, ROW_8)

    assert worksheet.get(T2017_RESERVE_LATER_YEAR).value == 1
    assert worksheet.get(T2017_RESERVE_LATER_YEAR_MAXIMUM).value == D("4000")
    assert worksheet.get(T2017_RESERVE_CLAIM_LIMIT).value == D("4000")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("4000.00")


def test_a_claim_on_a_row_with_a_previous_claim_above_the_maximum_is_limited_by_the_maximum() -> (
    None
):
    worksheet = one_row(2, ROW_2)

    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("50000.00")
    assert worksheet.get(T2017_RESERVE_LATER_YEAR_MAXIMUM).value == D("50000")
    assert worksheet.get(T2017_RESERVE_CLAIM_LIMIT).value == D("50000")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("50000.00")


def test_the_later_year_maximum_is_the_lesser_of_the_maximum_and_the_previous_year_claim() -> None:
    worksheet = one_row(17, ROW_17)

    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("5000.00")
    assert worksheet.get(T2017_RESERVE_LATER_YEAR_MAXIMUM).value == D("3000")
    assert worksheet.get(T2017_RESERVE_CLAIM_LIMIT).value == D("3000")


def test_a_disposition_in_its_year_of_disposition_does_not_read_its_previous_claim() -> None:
    worksheet = one_row(27, {**ROW_27_DISPOSED, "previous": "1.00", "claimed": "5000"})

    assert worksheet.get(T2017_RESERVE_LATER_YEAR).value == 0
    assert worksheet.get(T2017_RESERVE_CLAIM_LIMIT).value == D("5000.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("5000.00")


def test_each_line_27_disposition_has_its_own_row_in_the_order_of_its_list() -> None:
    later, disposed = row(27)

    assert later.get(T2017_ROW_RESERVE).value == D("6000.00")
    assert disposed.get(T2017_ROW_RESERVE).value == D("5000.00")


# --- the later-year bound: refused claims --------------------------------------------------------


def test_a_claim_one_cent_above_the_previous_year_claim_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(17, {**ROW_17, "claimed": "3000.01"})


def test_a_claim_above_the_previous_year_claim_but_below_the_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(27, {**ROW_27_LATER, "previous": "1500", "claimed": "2000"})


def test_a_claim_above_the_previous_year_claim_of_zero_is_refused_in_a_later_year() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(8, {**ROW_8, "previous": "0"})


# --- the summary form ----------------------------------------------------------------------------


def test_line_5_is_the_total_of_the_line_2_reserve_of_50000() -> None:
    assert summary().get(T2017_LINE_5).value == D("50000.00")


def test_line_6_is_line_1_less_line_5_and_is_minus_40000_in_brackets() -> None:
    assert summary().get(T2017_LINE_6).value == D("-40000.00")


def test_line_12_is_line_7_less_the_line_11_reserve_of_4000() -> None:
    found = summary()

    assert found.get(T2017_LINE_11).value == D("4000.00")
    assert found.get(T2017_LINE_12).value == D("16000.00")


def test_line_13_is_line_6_plus_line_12_and_is_minus_24000_in_brackets() -> None:
    assert summary().get(T2017_LINE_13).value == D("-24000.00")


def test_line_29_adds_lines_19_22_25_and_28_to_minus_33000() -> None:
    assert summary().get(T2017_LINE_29).value == D("-33000.00")


def test_line_31_is_line_29_plus_line_30_and_is_minus_31000_in_brackets() -> None:
    assert summary().get(T2017_LINE_31).value == D("-31000.00")
