"""CA-ON 2025 end to end: return jn, Form T1206 "Dispositions of certain capital property - shares
subject to TOSI" as its own form.

The worked return `returns/2025_return_jn.yaml` (two dispositions with a reserve, lines A, B and F,
and a filer under 18) is checked by `test_worked_returns.py`. This module computes each example of
the section on its own: the dispositions form `ca/t1206_share_dispositions` (run once: lines
A to G, the under-18 and the 18-or-older amounts) and the reserve form `ca/t1206_share_reserve`
(run once for each row: the maximum, the lesser of the calculations (i) and (ii), and the reserve
claimed, up to that maximum), with the refusals the printed form does not give (no bound is
printed, so the bounds are refused, not capped).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, NoAmountForCountError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    T1206_LINE_C,
    T1206_LINE_D,
    T1206_LINE_E,
    T1206_LINE_G,
    T1206_PART_1_LINE_3_AMOUNT,
    T1206_PART_1_LINE_3_PERCENT,
    T1206_RESERVE_APPLICABLE_PERCENTAGE,
    T1206_RESERVE_BY_PAYMENT,
    T1206_RESERVE_BY_PERCENTAGE,
    T1206_RESERVE_MAXIMUM,
    T1206_ROW_RESERVE,
    T1206_UNDER_18_DIVIDEND_AMOUNT,
    T1206_UNDER_18_PERCENT,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

DISPOSITIONS = "ca/t1206_share_dispositions"
RESERVE = "ca/t1206_share_reserve"

# The two dispositions of return JN, chosen figures: the year of sale, and two years after it. The
# first claims its maximum, the second less than its maximum.
ROWS = (
    {
        "capital_gain": "10000",
        "payable": "6000",
        "proceeds": "12000",
        "years": 0,
        "claimed": "5000",
    },
    {"capital_gain": "4000", "payable": "1000", "proceeds": "8000", "years": 2, "claimed": "300"},
)
# The starting figures of return JN: line A, line B and line F.
LINE_A = "20000"
LINE_B = "5000"
LINE_F = "1000"


def run(
    *,
    rows: tuple[Mapping[str, Any], ...] = ROWS,
    line_a: str = LINE_A,
    line_b: str = LINE_B,
    line_f: str = LINE_F,
    aged_18_or_older: int = 0,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of the section, with the starting figures and the rows given.

    The return's other inputs are `starting(...)` with the age answer given; the section's inputs
    are the `t1206_*` arguments of `starting(...)`.
    """
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        aged_18_or_older_at_end_of_2025=aged_18_or_older,
        t1206_capital_gain_on_dispositions=line_a,
        t1206_reserve_2024=line_b,
        t1206_t3_box_21_capital_gains=line_f,
        t1206_rows=rows,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def dispositions(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[DISPOSITIONS]
    return worksheet


def reserves(**overrides: Any) -> tuple[Worksheet, ...]:
    return run(**overrides)[RESERVE]


# --- the reserve, one copy for each row ----------------------------------------------------------


def test_each_row_maximum_is_the_lesser_of_the_payment_and_the_percentage_calculations() -> None:
    first, second = reserves()

    assert first.get(T1206_RESERVE_MAXIMUM).value == D("5000.00")
    assert second.get(T1206_RESERVE_MAXIMUM).value == D("500.00")


def test_each_row_reserve_is_the_claim_taken_up_to_its_maximum() -> None:
    first, second = reserves()

    assert first.get(T1206_ROW_RESERVE).value == D("5000.00")
    assert second.get(T1206_ROW_RESERVE).value == D("300.00")


def test_the_two_calculations_of_the_first_row_are_5000_and_8000() -> None:
    first, _ = reserves()

    assert first.get(T1206_RESERVE_BY_PAYMENT).value == D("5000.00")
    assert first.get(T1206_RESERVE_BY_PERCENTAGE).value == D("8000.00")
    assert first.get(T1206_RESERVE_APPLICABLE_PERCENTAGE).value == D("80.00")


def test_the_two_calculations_of_the_second_row_are_500_and_1600_at_40_percent() -> None:
    _, second = reserves()

    assert second.get(T1206_RESERVE_BY_PAYMENT).value == D("500.00")
    assert second.get(T1206_RESERVE_BY_PERCENTAGE).value == D("1600.00")
    assert second.get(T1206_RESERVE_APPLICABLE_PERCENTAGE).value == D("40.00")


def test_a_claim_of_zero_takes_no_reserve_and_line_c_is_zero() -> None:
    rows = tuple({**row, "claimed": "0"} for row in ROWS)

    first, second = reserves(rows=rows)
    found = dispositions(rows=rows)

    assert first.get(T1206_ROW_RESERVE).value == D("0.00")
    assert second.get(T1206_ROW_RESERVE).value == D("0.00")
    assert found.get(T1206_LINE_C).value == D("0.00")
    assert found.get(T1206_LINE_D).value == D("5000.00")
    assert found.get(T1206_LINE_G).value == D("26000.00")


def test_a_claim_above_the_maximum_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(rows=({**ROWS[1], "claimed": "500.01"},))


@pytest.mark.parametrize(
    ("years", "percentage"), [(0, "80"), (1, "60"), (2, "40"), (3, "20"), (4, "0")]
)
def test_the_applicable_percentage_is_read_for_each_year_after_the_sale(
    years: int, percentage: str
) -> None:
    (worksheet,) = reserves(
        rows=(
            {
                "capital_gain": "1000",
                "payable": "1000",
                "proceeds": "1000",
                "years": years,
                "claimed": "0",
            },
        )
    )

    assert worksheet.get(T1206_RESERVE_APPLICABLE_PERCENTAGE).value == D(percentage)


@pytest.mark.parametrize(("years", "reserve"), [(3, "200.00"), (4, "0.00")])
def test_a_later_year_takes_its_percentage_and_the_fourth_year_takes_nothing(
    years: int, reserve: str
) -> None:
    (worksheet,) = reserves(
        rows=(
            {
                "capital_gain": "1000",
                "payable": "1000",
                "proceeds": "1000",
                "years": years,
                "claimed": "0",
            },
        )
    )

    assert worksheet.get(T1206_RESERVE_MAXIMUM).value == D(reserve)


def test_a_row_with_proceeds_of_zero_has_a_payment_calculation_of_zero() -> None:
    (worksheet,) = reserves(
        rows=(
            {"capital_gain": "1000", "payable": "0", "proceeds": "0", "years": 0, "claimed": "0"},
        )
    )

    assert worksheet.get(T1206_RESERVE_BY_PAYMENT).value == D("0.00")
    assert worksheet.get(T1206_RESERVE_BY_PERCENTAGE).value == D("800.00")
    assert worksheet.get(T1206_RESERVE_MAXIMUM).value == D("0.00")
    assert worksheet.get(T1206_ROW_RESERVE).value == D("0.00")


def test_the_payment_calculation_is_rounded_half_up_to_the_cent() -> None:
    # 10,000.00 x 1,000.00 / 3,000.00 = 3,333.333..., which rounds to 3,333.33.
    (worksheet,) = reserves(
        rows=(
            {
                "capital_gain": "10000",
                "payable": "1000",
                "proceeds": "3000",
                "years": 0,
                "claimed": "3333.33",
            },
        )
    )

    assert worksheet.get(T1206_RESERVE_BY_PAYMENT).value == D("3333.33")
    assert worksheet.get(T1206_RESERVE_MAXIMUM).value == D("3333.33")
    assert worksheet.get(T1206_ROW_RESERVE).value == D("3333.33")


# --- the dispositions form -----------------------------------------------------------------------


def test_line_c_is_the_total_of_the_two_row_reserves_of_5300() -> None:
    assert dispositions().get(T1206_LINE_C).value == D("5300.00")


def test_line_d_is_line_b_less_line_c_and_is_minus_300_in_brackets() -> None:
    assert dispositions().get(T1206_LINE_D).value == D("-300.00")


def test_line_e_is_line_a_plus_line_d_and_line_g_is_line_e_plus_line_f() -> None:
    found = dispositions()

    assert found.get(T1206_LINE_E).value == D("19700.00")
    assert found.get(T1206_LINE_G).value == D("20700.00")


def test_an_under_18_filer_has_line_g_times_1_15_as_the_deemed_dividend() -> None:
    found = dispositions()

    assert found.get(T1206_UNDER_18_PERCENT).value == D("115")
    assert found.get(T1206_UNDER_18_DIVIDEND_AMOUNT).value == D("23805.00")


def test_an_under_18_filer_has_no_part_1_line_3_amount() -> None:
    found = dispositions()

    assert found.get(T1206_PART_1_LINE_3_PERCENT).value == D("0")
    assert found.get(T1206_PART_1_LINE_3_AMOUNT).value == D("0.00")


def test_an_18_or_older_filer_has_half_of_line_g_on_part_1_line_3_and_no_deemed_dividend() -> None:
    found = dispositions(aged_18_or_older=1)

    assert found.get(T1206_PART_1_LINE_3_PERCENT).value == D("50")
    assert found.get(T1206_PART_1_LINE_3_AMOUNT).value == D("10350.00")
    assert found.get(T1206_UNDER_18_PERCENT).value == D("0")
    assert found.get(T1206_UNDER_18_DIVIDEND_AMOUNT).value == D("0.00")


def test_no_rows_give_line_c_of_zero_and_line_d_of_line_b() -> None:
    found = dispositions(rows=())

    assert reserves(rows=()) == ()
    assert found.get(T1206_LINE_C).value == D("0.00")
    assert found.get(T1206_LINE_D).value == D("5000.00")
    assert found.get(T1206_LINE_E).value == D("25000.00")
    assert found.get(T1206_LINE_G).value == D("26000.00")


# --- refusals ------------------------------------------------------------------------------------


def test_an_amount_payable_above_the_proceeds_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(
            rows=(
                {
                    "capital_gain": "10000",
                    "payable": "12001",
                    "proceeds": "12000",
                    "years": 0,
                    "claimed": "0",
                },
            )
        )


def test_line_c_above_lines_a_and_b_is_refused_not_capped() -> None:
    # The row claims its maximum, the lesser of 10,000.00 and 8,000.00, so line C is 8,000.00
    # against lines A and B of 1,000.00 and 0.00: the net capital gain could not be negative.
    with pytest.raises(InputAboveBoundError):
        run(
            rows=(
                {
                    "capital_gain": "10000",
                    "payable": "10000",
                    "proceeds": "10000",
                    "years": 0,
                    "claimed": "8000",
                },
            ),
            line_a="1000",
            line_b="0",
            line_f="0",
        )


def test_a_year_after_the_sale_with_no_row_is_refused() -> None:
    with pytest.raises(NoAmountForCountError):
        run(
            rows=(
                {
                    "capital_gain": "1000",
                    "payable": "1000",
                    "proceeds": "1000",
                    "years": 5,
                    "claimed": "0",
                },
            )
        )


def test_an_age_answer_above_one_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(aged_18_or_older=2)
