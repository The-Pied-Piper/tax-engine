"""CA-ON 2025 end to end: return jw, Form T2017 (2025), "Summary of Reserves on Dispositions of
Capital Property", Part 1, as its own forms.

The worked return `returns/2025_return_jw.yaml` (four dispositions with a reserve, on reserve lines
2, 8, 17 and 27, and the 2024 figures of lines 1, 7, 16, 26 and 30) is checked by
`test_worked_returns.py`. This module computes each example of Part 1 on its own: the row forms
`ca/t2017_line_N_reserve` (run once for each disposition of their list: the maximum, the lesser of
calculations (i) and (ii), and the reserve claimed, up to that maximum) and the summary form
`ca/t2017` (run once: the lines of Part 1), with the refusals the printed form does not give (no
bound is
printed, so the bounds are refused, not capped; a year past the table is refused).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, NoAmountForCountError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ANNUAL_GAINS_LINE_2,
    ANNUAL_GAINS_LINE_3,
    CAPITAL_GAIN,
    INCLUDED_CAPITAL_GAIN,
    SCHEDULE_3_LINE_19200,
    T2017_LINE_5,
    T2017_LINE_6,
    T2017_LINE_11,
    T2017_LINE_12,
    T2017_LINE_13,
    T2017_LINE_29,
    T2017_LINE_31,
    T2017_RESERVE_APPLICABLE_PERCENTAGE,
    T2017_RESERVE_BY_PAYMENT,
    T2017_RESERVE_BY_PERCENTAGE,
    T2017_RESERVE_MAXIMUM,
    T2017_ROW_RESERVE,
    TAXABLE_CAPITAL_GAINS,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

SUMMARY = "ca/t2017"
RETURN = "ca-on/return"

# The dispositions of return JW, chosen figures, by reserve line. Line 2 is of the nine-year kind,
# line 8 of the four-year kind (nine_year 0), line 17 is nine-year, line 27 four-year.
ROW_2 = {
    "capital_gain": "100000",
    "payable": "60000",
    "proceeds": "200000",
    "years": 0,
    "claimed": "30000",
    "previous": "0",
    "nine_year": 1,
}
ROW_8 = {
    "capital_gain": "50000",
    "payable": "20000",
    "proceeds": "100000",
    "years": 2,
    "claimed": "5000",
    "previous": "10000",
    "nine_year": 0,
}
ROW_17 = {
    "capital_gain": "20000",
    "payable": "10000",
    "proceeds": "40000",
    "years": 3,
    "claimed": "4000",
    "previous": "5000",
}
ROW_27 = {
    "capital_gain": "10000",
    "payable": "10000",
    "proceeds": "10000",
    "years": 1,
    "claimed": "6000",
    "previous": "6000",
}
ROWS: Mapping[int, tuple[Mapping[str, Any], ...]] = {
    2: (ROW_2,),
    8: (ROW_8,),
    17: (ROW_17,),
    27: (ROW_27,),
}
# The 2024 figures of return JW, by line number.
AMOUNTS: Mapping[int, str] = {1: "10000", 7: "20000", 16: "4000", 26: "1000", 30: "2000"}


def form_name(line: int) -> str:
    return f"ca/t2017_line_{line}_reserve"


def run(
    *,
    amounts: Mapping[int, str] = AMOUNTS,
    rows: Mapping[int, tuple[Mapping[str, Any], ...]] = ROWS,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of Part 1, with the 2024 figures and the rows given.

    The return's other inputs are `starting(...)`; Part 1's inputs are the `t2017_*` arguments.
    """
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


# --- the row forms: the calculation of reserve ---------------------------------------------------


def test_line_2_maximum_is_the_lesser_of_the_payment_and_the_percentage_calculations() -> None:
    (worksheet,) = row(2)

    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("30000.00")
    assert worksheet.get(T2017_RESERVE_APPLICABLE_PERCENTAGE).value == D("90")
    assert worksheet.get(T2017_RESERVE_BY_PERCENTAGE).value == D("90000.00")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("30000.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("30000.00")


def test_line_8_takes_the_four_year_table_when_the_nine_year_answer_is_0() -> None:
    (worksheet,) = row(8)

    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("10000.00")
    assert worksheet.get(T2017_RESERVE_APPLICABLE_PERCENTAGE).value == D("40")
    assert worksheet.get(T2017_RESERVE_BY_PERCENTAGE).value == D("20000.00")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("10000.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("5000.00")


def test_line_8_takes_the_nine_year_table_when_the_nine_year_answer_is_1() -> None:
    worksheet = one_row(8, {**ROW_8, "nine_year": 1})

    assert worksheet.get(T2017_RESERVE_APPLICABLE_PERCENTAGE).value == D("70")
    assert worksheet.get(T2017_RESERVE_BY_PERCENTAGE).value == D("35000.00")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("10000.00")


def test_line_17_takes_the_nine_year_table_for_its_3rd_year() -> None:
    (worksheet,) = row(17)

    assert worksheet.get(T2017_RESERVE_APPLICABLE_PERCENTAGE).value == D("60")
    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("5000.00")
    assert worksheet.get(T2017_RESERVE_BY_PERCENTAGE).value == D("12000.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("4000.00")


def test_line_27_takes_the_four_year_table_for_its_1st_year_and_the_claim_is_the_maximum() -> None:
    (worksheet,) = row(27)

    assert worksheet.get(T2017_RESERVE_APPLICABLE_PERCENTAGE).value == D("60")
    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("10000.00")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("6000.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("6000.00")


def test_a_claim_above_the_maximum_by_one_cent_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(27, {**ROW_27, "claimed": "6000.01"})


def test_a_claim_above_the_maximum_of_a_line_2_row_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(2, {**ROW_2, "claimed": "30000.01"})


@pytest.mark.parametrize(
    ("line", "record"),
    [(2, ROW_2), (17, ROW_17)],
)
def test_a_year_past_the_nine_year_table_is_refused(line: int, record: Mapping[str, Any]) -> None:
    with pytest.raises(NoAmountForCountError):
        one_row(line, {**record, "years": 10})


def test_a_year_past_the_four_year_table_of_a_line_27_row_is_refused() -> None:
    with pytest.raises(NoAmountForCountError):
        one_row(27, {**ROW_27, "years": 10})


def test_a_nine_year_answer_above_one_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(2, {**ROW_2, "nine_year": 2})


def test_an_amount_payable_above_the_proceeds_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        one_row(27, {**ROW_27, "payable": "10000.01"})


def test_a_row_with_zero_proceeds_has_a_payment_calculation_of_zero_and_no_reserve() -> None:
    worksheet = one_row(27, {**ROW_27, "payable": "0", "proceeds": "0", "claimed": "0"})

    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("0.00")
    assert worksheet.get(T2017_RESERVE_BY_PERCENTAGE).value == D("6000.00")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("0.00")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("0.00")


def test_the_payment_calculation_is_rounded_half_up_to_the_cent() -> None:
    # 10,000.00 x 1,000.00 / 3,000.00 = 3,333.333..., which rounds to 3,333.33.
    worksheet = one_row(
        27, {**ROW_27, "payable": "1000", "proceeds": "3000", "years": 0, "claimed": "3333.33"}
    )

    assert worksheet.get(T2017_RESERVE_BY_PAYMENT).value == D("3333.33")
    assert worksheet.get(T2017_RESERVE_MAXIMUM).value == D("3333.33")
    assert worksheet.get(T2017_ROW_RESERVE).value == D("3333.33")


# --- the summary form ----------------------------------------------------------------------------


def test_line_5_is_the_total_of_the_line_2_reserves_of_30000() -> None:
    assert summary().get(T2017_LINE_5).value == D("30000.00")


def test_line_6_is_line_1_less_line_5_and_is_minus_20000_in_brackets() -> None:
    assert summary().get(T2017_LINE_6).value == D("-20000.00")


def test_line_11_is_the_total_of_the_line_8_reserves_of_5000() -> None:
    assert summary().get(T2017_LINE_11).value == D("5000.00")


def test_line_12_is_line_7_less_line_11() -> None:
    assert summary().get(T2017_LINE_12).value == D("15000.00")


def test_line_13_is_line_6_plus_line_12_and_is_minus_5000_in_brackets() -> None:
    assert summary().get(T2017_LINE_13).value == D("-5000.00")


def test_line_29_adds_lines_19_22_25_and_28_to_minus_10000() -> None:
    assert summary().get(T2017_LINE_29).value == D("-10000.00")


def test_line_31_is_line_29_plus_line_30_and_is_minus_8000_in_brackets() -> None:
    found = summary()

    assert found.get(T2017_LINE_31).value == D("-8000.00")


# --- the rows as printed: no dispositions --------------------------------------------------------


def test_no_rows_give_no_worksheets_for_the_row_forms() -> None:
    found = run(rows={})

    for line in (2, 8, 17, 27):
        assert found[form_name(line)] == (), line


def test_with_no_rows_each_total_is_zero_and_the_2024_lines_carry_through() -> None:
    found = summary(rows={})

    assert found.get(T2017_LINE_5).value == D("0.00")
    assert found.get(T2017_LINE_11).value == D("0.00")
    assert found.get(T2017_LINE_6).value == D("10000.00")
    assert found.get(T2017_LINE_12).value == D("20000.00")
    assert found.get(T2017_LINE_13).value == D("30000.00")
    assert found.get(T2017_LINE_29).value == D("35000.00")
    assert found.get(T2017_LINE_31).value == D("37000.00")


# --- the return: the summary's lines 13 and 31 as read by the T1 and T657 lines ------------------


def test_line_19200_is_t2017_line_31_of_minus_8000_and_the_capital_gain_is_minus_8000() -> None:
    (worksheet,) = run()[RETURN]

    assert worksheet.get(SCHEDULE_3_LINE_19200).value == D("-8000.00")
    assert worksheet.get(CAPITAL_GAIN).value == D("-8000.00")
    assert worksheet.get(INCLUDED_CAPITAL_GAIN).value == D("-4000.00")
    assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("0.00")


def test_t657_step_1_line_2_is_t2017_line_13_of_minus_5000_and_flows_to_line_3() -> None:
    (worksheet,) = run()[RETURN]

    assert worksheet.get(ANNUAL_GAINS_LINE_2).value == D("-5000.00")
    assert worksheet.get(ANNUAL_GAINS_LINE_3).value == D("-5000.00")
