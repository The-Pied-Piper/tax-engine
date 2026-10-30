"""CA-ON 2025 end to end: return mg, Form T2205 "Amounts from a Spousal or Common-law Partner RRSP,
RRIF, or SPP to Include in Income" as its own form, and the T1 lines 12900, 11500 and 13000 it
feeds.

The worked return `returns/2025_return_mg.yaml` (T2205 line 1 of 5,000.00, line 6 of 2,000.00, an
SPP part of line 11 of 1,000.00, line 12 and line 20 of 4,000.00; a filer under 65) is checked by
`test_worked_returns.py`. This module computes each example on its own: the form `ca/t2205` (run
once: Part 1 lines 3 to 11, Part 2 lines 15 to 22), the choice between the typed lines 17 and 18 and
the Part 1 figures, the refusal of every part above its whole (never a cap), and the routing of the
SPP part and of line 22 to T1 line 11500 (65 or older at the end of the year) or line 13000.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_engine.domain.errors import DomainError, InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    T2205_LINE_3,
    T2205_LINE_5,
    T2205_LINE_8,
    T2205_LINE_10,
    T2205_LINE_11,
    T2205_LINE_11_RRSP_PART,
    T2205_LINE_11_SPP_PART_CHECKED,
    T2205_LINE_15,
    T2205_LINE_16,
    T2205_LINE_17_USED,
    T2205_LINE_18_CHECKED,
    T2205_LINE_19,
    T2205_LINE_21,
    T2205_LINE_22,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_12900,
    T2205_ON_LINE_13000,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

T2205 = "ca/t2205"
RETURN = "ca-on/return"

# The figures of return MG: Part 1 (line 1 of 5,000.00, line 6 of 2,000.00, 1,000.00 of line 11
# relating to SPP withdrawals) and Part 2 (line 12 and line 20 of 4,000.00).
MG_T2205 = {
    "line_1": "5000",
    "line_6": "2000",
    "line_11_spp_part": "1000",
    "line_12": "4000",
    "line_20": "4000",
}


def run(
    *,
    t2205: Mapping[str, str] = MG_T2205,
    employment_income: str = "0",
    **overrides: Any,
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return MG with the T2205 amounts and the keyword overrides of
    `starting(...)` given: no income other than the employment income given (0)."""
    artifacts = starting(
        employment_income, (), "0", "0", "0", "0", "0", t2205_amounts=t2205, **overrides
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_mg(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


def t2205_form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[T2205]
    return worksheet


# --- Part 1 of return MG -------------------------------------------------------------------------


def test_part_1_lines_3_to_11_of_return_mg() -> None:
    # Line 3 = 5,000 + 0; line 5 = 5,000 - 0; line 8 = 2,000 - 0; line 10 is the lesser of 5,000 and
    # 2,000; line 11 = 5,000 - 2,000 = 3,000.
    found = t2205_form()

    assert found.get(T2205_LINE_3).value == D("5000")
    assert found.get(T2205_LINE_5).value == D("5000")
    assert found.get(T2205_LINE_8).value == D("2000")
    assert found.get(T2205_LINE_10).value == D("2000")
    assert found.get(T2205_LINE_11).value == D("3000")


def test_line_11_is_split_into_the_spp_part_and_the_rrsp_part() -> None:
    found = t2205_form()

    assert found.get(T2205_LINE_11_SPP_PART_CHECKED).value == D("1000")
    assert found.get(T2205_LINE_11_RRSP_PART).value == D("2000")


def test_line_2_alone_fills_in_part_1() -> None:
    # An FHSA transfer of 3,000.00 makes line 3 3,000.00, more than 0, so Part 1 is filled in.
    found = t2205_form(t2205={"line_2": "3000", "line_6": "1000", "line_17": "9999"})

    assert found.get(T2205_LINE_3).value == D("3000")
    assert found.get(T2205_LINE_10).value == D("1000")
    assert found.get(T2205_LINE_11).value == D("2000")
    assert found.get(T2205_LINE_17_USED).value == D("1000")


def test_line_6_of_0_leaves_all_of_line_3_on_line_11() -> None:
    found = t2205_form(t2205={"line_1": "5000", "line_6": "0"})

    assert found.get(T2205_LINE_10).value == D("0")
    assert found.get(T2205_LINE_11).value == D("5000")
    assert found.get(T2205_LINE_11_RRSP_PART).value == D("5000")


def test_lines_4_and_7_reduce_lines_5_and_8() -> None:
    # Line 4 of 1,500 is transferred on: line 5 = 3,500; line 7 of 500: line 8 = 1,500.
    found = t2205_form(
        t2205={"line_1": "5000", "line_4": "1500", "line_6": "2000", "line_7": "500"}
    )

    assert found.get(T2205_LINE_5).value == D("3500")
    assert found.get(T2205_LINE_8).value == D("1500")
    assert found.get(T2205_LINE_10).value == D("1500")
    assert found.get(T2205_LINE_11).value == D("3500")


# --- Part 2 of return MG -------------------------------------------------------------------------


def test_part_2_lines_15_to_22_of_return_mg() -> None:
    # Part 1 is filled in: line 17 is line 6 (2,000.00) and line 18 is line 7 plus line 10
    # (0 + 2,000.00), so line 19 = 0 and line 21 is the lesser of 4,000.00 and 0; line 22 is
    # 4,000.00.
    found = t2205_form()

    assert found.get(T2205_LINE_15).value == D("0")
    assert found.get(T2205_LINE_16).value == D("4000")
    assert found.get(T2205_LINE_17_USED).value == D("2000")
    assert found.get(T2205_LINE_18_CHECKED).value == D("2000")
    assert found.get(T2205_LINE_19).value == D("0")
    assert found.get(T2205_LINE_21).value == D("0")
    assert found.get(T2205_LINE_22).value == D("4000")


def test_part_1_not_filled_in_uses_the_typed_lines_17_and_18() -> None:
    # Line 1 and line 2 are 0, so line 3 is 0: line 17 is 3,000.00 and line 18 is 1,000.00 as typed
    # (line 6 of 7,777.00 is not read), line 19 = 2,000.00, line 16 = 2,500.00; line 21 is the
    # lesser of 2,500.00 and 2,000.00; line 22 = 2,500.00 - 2,000.00 = 500.00.
    found = t2205_form(
        t2205={
            "line_6": "7777",
            "line_17": "3000",
            "line_18": "1000",
            "line_12": "2500",
            "line_20": "2500",
        }
    )

    assert found.get(T2205_LINE_3).value == D("0")
    assert found.get(T2205_LINE_17_USED).value == D("3000")
    assert found.get(T2205_LINE_18_CHECKED).value == D("1000")
    assert found.get(T2205_LINE_19).value == D("2000")
    assert found.get(T2205_LINE_16).value == D("2500")
    assert found.get(T2205_LINE_21).value == D("2000")
    assert found.get(T2205_LINE_22).value == D("500")


def test_part_1_filled_in_ignores_the_typed_lines_17_and_18() -> None:
    found = t2205_form(t2205={**MG_T2205, "line_17": "9000", "line_18": "8000"})

    assert found.get(T2205_LINE_17_USED).value == D("2000")
    assert found.get(T2205_LINE_18_CHECKED).value == D("2000")
    assert found.get(T2205_LINE_22).value == D("4000")


def test_line_13_less_line_14_is_added_to_line_12_at_line_16() -> None:
    found = t2205_form(t2205={"line_12": "1000", "line_13": "600", "line_14": "100"})

    assert found.get(T2205_LINE_15).value == D("500")
    assert found.get(T2205_LINE_16).value == D("1500")


def test_line_22_is_negative_when_line_21_is_above_line_20() -> None:
    # Line 21 is the lesser of line 16 (4,000.00) and line 19 (5,000.00) = 4,000.00; line 20 is
    # 1,000.00. The form prints no floor, so line 22 is (3,000.00), reported on line 13000; with
    # employment income of 5,000.00 the total income is 2,000.00.
    amounts = {"line_17": "5000", "line_12": "4000", "line_20": "1000"}

    assert t2205_form(t2205=amounts, employment_income="5000").get(T2205_LINE_21).value == D("4000")
    assert t2205_form(t2205=amounts, employment_income="5000").get(T2205_LINE_22).value == D(
        "-3000"
    )
    worksheet = return_mg(t2205=amounts, employment_income="5000")
    assert worksheet.get(T2205_ON_LINE_13000).value == D("-3000")
    assert worksheet.get(TOTAL_INCOME).value == D("2000")


def test_a_negative_line_22_that_takes_the_income_below_zero_is_refused() -> None:
    with pytest.raises(DomainError):
        run(t2205={"line_17": "5000", "line_12": "4000", "line_20": "1000"})


def test_lines_10_and_21_are_the_spouse_s_amounts_and_change_nothing_on_this_return() -> None:
    worksheet = return_mg()

    assert t2205_form().get(T2205_LINE_10).value == D("2000")
    assert t2205_form().get(T2205_LINE_21).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("7000")


# --- the T1 lines of a filer under 65 ------------------------------------------------------------


def test_the_rrsp_part_goes_to_line_12900_and_the_rest_to_line_13000_under_65() -> None:
    worksheet = return_mg()

    assert worksheet.get(T2205_ON_LINE_12900).value == D("2000")
    assert worksheet.get(T2205_ON_LINE_11500).value == D("0")
    assert worksheet.get(T2205_ON_LINE_13000).value == D("5000")


def test_total_income_adds_the_three_amounts() -> None:
    # 2,000.00 (line 12900) + 0 (line 11500) + 5,000.00 (line 13000: SPP part 1,000.00 and line 22
    # of 4,000.00).
    assert return_mg().get(TOTAL_INCOME).value == D("7000")


# --- the T1 lines of a filer 65 or older ---------------------------------------------------------


def test_the_spp_part_and_line_22_go_to_line_11500_at_65_or_older() -> None:
    worksheet = return_mg(born_in_1960_or_earlier=1)

    assert worksheet.get(T2205_ON_LINE_12900).value == D("2000")
    assert worksheet.get(T2205_ON_LINE_11500).value == D("5000")
    assert worksheet.get(T2205_ON_LINE_13000).value == D("0")
    assert worksheet.get(TOTAL_INCOME).value == D("7000")


# --- no T2205 ------------------------------------------------------------------------------------


def test_with_no_t2205_amounts_every_line_and_the_total_income_are_0() -> None:
    worksheet = return_mg(t2205={})

    for kind in (T2205_ON_LINE_12900, T2205_ON_LINE_11500, T2205_ON_LINE_13000, TOTAL_INCOME):
        assert worksheet.get(kind).value == D("0"), kind.identifier
    assert t2205_form(t2205={}).get(T2205_LINE_22).value == D("0")


def test_the_typed_t1_lines_stay_beside_the_t2205_amounts() -> None:
    # Other T4RSP income of 800.00 (line 12900), other pensions of 600.00 (line 11500) and other
    # income of 400.00 (line 13000) are added to the T2205 amounts, not replaced by them.
    worksheet = return_mg(
        rrsp_income="800", other_pensions_and_superannuation="600", other_income="400"
    )

    assert worksheet.get(TOTAL_INCOME).value == D("8800")


# --- every part above its whole is refused, never capped -----------------------------------------


def test_line_4_above_line_1_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(t2205={"line_1": "100", "line_4": "100.01"})


def test_line_4_equal_to_line_1_is_accepted() -> None:
    found = t2205_form(t2205={"line_1": "100", "line_4": "100"})

    assert found.get(T2205_LINE_5).value == D("0")


def test_line_7_above_line_6_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(t2205={"line_6": "100", "line_7": "100.01"})


def test_line_14_above_line_13_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(t2205={"line_13": "100", "line_14": "100.01"})


def test_the_spp_part_above_line_11_is_refused() -> None:
    # Line 11 is 3,000.00.
    with pytest.raises(InputAboveBoundError):
        run(t2205={**MG_T2205, "line_11_spp_part": "3000.01"})


def test_the_spp_part_equal_to_line_11_is_accepted() -> None:
    found = t2205_form(t2205={**MG_T2205, "line_11_spp_part": "3000"})

    assert found.get(T2205_LINE_11_RRSP_PART).value == D("0")


def test_typed_line_18_above_typed_line_17_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(t2205={"line_17": "100", "line_18": "100.01", "line_12": "1", "line_20": "1"})


def test_typed_lines_17_and_18_are_not_read_when_part_1_is_filled_in() -> None:
    # Line 18 above line 17 as typed is not refused: Part 1 gives the figures.
    found = t2205_form(t2205={**MG_T2205, "line_17": "100", "line_18": "5000"})

    assert found.get(T2205_LINE_19).value == D("0")
