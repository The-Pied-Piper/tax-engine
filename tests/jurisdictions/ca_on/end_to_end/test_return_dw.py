"""CA-ON 2025 end to end: return dw, Form T2043 Parts 3 and 4 with Chart B and Chart C.

Return DW (returns/2025_return_dw.yaml) is one farm in Ontario and Quebec on a Form T2042
statement (Chart B, rows 1 to 11, and Chart C), and a second Ontario farm in Part 2 (Chart A), for
a fiscal period of 365 days, 184 of them in 2024. The figures are the worked example of Form T2043
Chart B (row 8 is 55%, row 11 is 10,120.00 and Chart C is 23.17), totalled in Parts 3 to 5.

Each statement's Chart B (per designated province: rows 1 and 4 are the statement's starting
amounts, rows 2 and 5 its lines 9659 and 9814) is computed for the statement: rows 3 and 6 are
percentages, row 7 their sum, row 8 is row 7 at 50% (or unhalved under note 9), row 9 is amount 6
at row 8, and rows 10 and 11 prorate row 9 by the days in 2024. Chart C is row 11 at the province's
payment rate. Part 3 totals the statements' rows 1 and 4 (and rows 2 and 5), Part 4 the Chart C
amounts (4A to 4H, and 4I), and line 5B is amount 4I.

Two sums are the usual expectations: each Part 4 amount is rounded to the cent per statement, and
the percentages are twelve decimals of a percent (half up); row 8 is exact.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from tax_calculator.domain.errors import InvalidRecordError, NegativeArtifactError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_CHART_A_GROSS_EXPENSES,
    FARM_CHART_B_NOTE_9_APPLIES,
    FARM_CHART_B_ROW_3_MB,
    FARM_CHART_B_ROW_3_ON,
    FARM_CHART_B_ROW_6_MB,
    FARM_CHART_B_ROW_6_ON,
    FARM_CHART_B_ROW_7_ON,
    FARM_CHART_B_ROW_8_MB,
    FARM_CHART_B_ROW_8_ON,
    FARM_CHART_B_ROW_9_MB,
    FARM_CHART_B_ROW_9_ON,
    FARM_CHART_B_ROW_11_MB,
    FARM_CHART_B_ROW_11_ON,
    FARM_CHART_C_AMOUNT_MB,
    FARM_CHART_C_AMOUNT_ON,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_MB,
    FUEL_CHARGE_CHART_B_GROSS_INCOME_ON,
    FUEL_CHARGE_CHART_B_SALARIES_ON,
    FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME,
    FUEL_CHARGE_CHART_B_TOTAL_SALARIES,
    FUEL_CHARGE_CHART_C_TOTAL_ON,
    FUEL_CHARGE_CREDIT_FARMERS,
    FUEL_CHARGE_CREDIT_ON,
    FUEL_CHARGE_GROSS_FARMING_EXPENSES,
    FUEL_CHARGE_PART_2_TOTAL,
    FUEL_CHARGE_PART_4_TOTAL,
    FUEL_CHARGE_PART_5A_CREDIT,
    FUEL_CHARGE_PART_5B_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

ONTARIO = 1
MANITOBA = 2


def statement(
    *,
    wheat: str,
    seeds_and_plants: str = "0",
    salaries_wages_and_benefits: str = "0",
    province: int = 0,
    chart_b: tuple[tuple[int, str, str], ...] = (),
    days_in_2024: int = 184,
    period_days: int = 365,
) -> dict[str, Any]:
    """One Form T2042 statement, as the keywords of `t2042_statement`: the gross income is
    `wheat`, the expenses are `seeds_and_plants` and `salaries_wages_and_benefits` (line 9898 is
    their sum), `chart_b` is the statement's Chart B province list, one (province code, row 1
    gross income, row 4 salaries and wages) row for each province with a permanent establishment
    (a province with no row counts as 0), and the fiscal period runs 365 days, 184 of them in
    2024."""
    farm = {
        "wheat": wheat,
        "seeds_and_plants": seeds_and_plants,
        "salaries_wages_and_benefits": salaries_wages_and_benefits,
    }
    return {
        "farm": farm,
        "farm_chart_b_provinces_rows": chart_b,
        "farm_fiscal_period_days_entered": period_days,
        "farm_designated_province": province,
        "farm_days_in_2024": days_in_2024,
    }


def run_dw(
    *statements: Mapping[str, Any],
) -> dict[str, tuple[Worksheet, ...]]:
    """Return DW's starting artifacts with the statements given; the partnership credits are 0."""
    artifacts = starting(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        farm_statements=statements,
        fuel_charge_partnership_credit_on="0",
        fuel_charge_partnership_credit_mb="0",
        fuel_charge_partnership_credit_sk="0",
        fuel_charge_partnership_credit_ab="0",
        fuel_charge_partnership_credit_ns="0",
        fuel_charge_partnership_credit_pe="0",
        fuel_charge_partnership_credit_nl="0",
        fuel_charge_partnership_credit_nb="0",
    )
    return service().compute(CA_ON, 2025, *artifacts)


def only(worksheets: tuple[Worksheet, ...]) -> Worksheet:
    (worksheet,) = worksheets
    return worksheet


# The worked example: one statement in Ontario and Quebec, Chart B for Ontario only.
EXAMPLE = statement(
    wheat="100000",
    seeds_and_plants="6500",
    salaries_wages_and_benefits="30000",
    chart_b=((ONTARIO, "60000", "15000"),),
)


# --- the worked example (Form T2043 Chart B, Ontario) ---------------------------------------------


def test_the_worked_example_gives_row_3_60_row_6_50_and_row_7_110_percent() -> None:
    # Row 3: 60,000 of 100,000 is 60%. Row 6: 15,000 of 30,000 is 50%. Row 7: 60 plus 50.
    farm = only(run_dw(EXAMPLE)["ca/t2042"])

    assert farm.get(FARM_CHART_B_ROW_3_ON).value == D("60")
    assert farm.get(FARM_CHART_B_ROW_6_ON).value == D("50")
    assert farm.get(FARM_CHART_B_ROW_7_ON).value == D("110")


def test_the_worked_example_gives_row_8_55_percent_because_note_9_does_not_apply() -> None:
    # Rows 2 and 5 are not 0, so row 7 is multiplied by 50%: 110 times 50% is 55.
    farm = only(run_dw(EXAMPLE)["ca/t2042"])

    assert farm.get(FARM_CHART_B_NOTE_9_APPLIES).value == 0
    assert farm.get(FARM_CHART_B_ROW_8_ON).value == D("55")


def test_the_worked_example_gives_row_9_20075_and_row_11_10120() -> None:
    # Row 9: 36,500 (amount 6) times 55% is 20,075.00. Row 11: 20,075.00 times 184/365, which is
    # 3,693,800 / 365 = 10,120.00 exactly.
    farm = only(run_dw(EXAMPLE)["ca/t2042"])

    assert farm.get(FARM_CHART_A_GROSS_EXPENSES).value == D("36500.00")
    assert farm.get(FARM_CHART_B_ROW_9_ON).value == D("20075.00")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("10120.00")


def test_the_worked_example_gives_chart_c_23_17_and_line_47556_of_23_17() -> None:
    # Chart C amount 7: 10,120.00 times 0.229% is 23.1748, which rounds half-up to 23.17. With no
    # Part 2 business and no partnership credit, 5A is 0 and 5B (amount 4I) is 23.17 = 5D.
    result = run_dw(EXAMPLE)
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("23.17")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("60000.00")
    assert form.get(FUEL_CHARGE_CHART_B_SALARIES_ON).value == D("15000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME).value == D("100000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_SALARIES).value == D("30000.00")
    assert form.get(FUEL_CHARGE_CHART_C_TOTAL_ON).value == D("23.17")
    assert form.get(FUEL_CHARGE_PART_4_TOTAL).value == D("23.17")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("23.17")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("23.17")


# --- Return DW: a Chart B business and a Part 2 business in one return ----------------------------


def test_return_dw_gives_5a_21_07_and_5b_23_17_and_line_47556_of_44_24() -> None:
    # Part 2: the Ontario farm of 18,250 (amount 6, amount 8 9,200.00) at 0.229% is 21.068, 21.07.
    # Part 1 line 67061 is 36,500 + 18,250 = 54,750, which reaches 25,000, so 5A is 21.07; 5B is
    # 23.17; 5C is 0; 5D (line 47556) is 21.07 + 23.17 = 44.24.
    result = run_dw(
        EXAMPLE,
        statement(
            wheat="48250",
            seeds_and_plants="18250",
            province=ONTARIO,
        ),
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("54750.00")
    assert form.get(FUEL_CHARGE_CREDIT_ON).value == D("21.07")
    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("21.07")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("21.07")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("23.17")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("44.24")


def test_return_dw_part_3_has_the_ontario_row_1_and_row_4_and_the_row_2_and_5_totals() -> None:
    result = run_dw(
        EXAMPLE,
        statement(wheat="48250", seeds_and_plants="18250", province=ONTARIO),
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("60000.00")
    assert form.get(FUEL_CHARGE_CHART_B_SALARIES_ON).value == D("15000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME).value == D("100000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_SALARIES).value == D("30000.00")


# --- the extra cases: note 9, zero totals, a non-terminating percent, MB, two Chart Bs -----------


def test_note_9_with_zero_salaries_leaves_row_7_unhalved_so_row_8_is_60() -> None:
    # Row 5 is 0 (no salaries), so note 9 applies: row 6 is 0 (a zero divisor), row 7 is 60 and row
    # 8 is 60 times 100% = 60. Row 9: 36,500 times 60% is 21,900.00. Row 11: 21,900 times 184/365
    # is 11,040.00. Chart C: 11,040 times 0.229% is 25.2816, which is 25.28.
    farm = only(
        run_dw(
            statement(
                wheat="100000",
                seeds_and_plants="36500",
                chart_b=((ONTARIO, "60000", "0"),),
            )
        )["ca/t2042"]
    )

    assert farm.get(FARM_CHART_B_NOTE_9_APPLIES).value == 1
    assert farm.get(FARM_CHART_B_ROW_6_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_7_ON).value == D("60")
    assert farm.get(FARM_CHART_B_ROW_8_ON).value == D("60")
    assert farm.get(FARM_CHART_B_ROW_9_ON).value == D("21900.00")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("11040.00")
    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("25.28")


def test_zero_rows_2_and_5_give_zero_percentages_and_zero_credit_without_an_error() -> None:
    # Row 2 and row 5 are 0: rows 3 and 6 are 0 (a zero divisor), note 9 applies, and every later
    # row is 0. The credit is 0.
    result = run_dw(statement(wheat="0", chart_b=()))
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_B_ROW_3_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_8_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("0")
    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0")


def test_one_of_three_is_33_333333333333_percent_rounded_half_up() -> None:
    # Row 1 of 1 over row 2 of 3: 100 x 1/3 = 33.333..., which is 33.333333333333 (twelve
    # decimals of a percent: no source prints a rounding rule, and twelve keep the cents of the
    # later rows unchanged except in rare ties at very large amounts).
    farm = only(
        run_dw(
            statement(wheat="3", chart_b=((ONTARIO, "1", "0"),)),
        )["ca/t2042"]
    )

    assert farm.get(FARM_CHART_B_ROW_3_ON).value == D("33.333333333333")


def test_a_second_province_gives_its_own_column_manitoba_40_percent_of_gross_income() -> None:
    # Manitoba: row 1 of 40,000 of 100,000 is 40%; row 4 of 6,000 of 30,000 is 20%; row 7 is 60%;
    # note 9 does not apply, so row 8 is 30%. Row 9: 36,500 times 30% is 10,950.00. Row 11:
    # 10,950 times 184/365 is 5,520.00. Chart C: 5,520 times 0.229% is 12.6408, which is 12.64.
    result = run_dw(
        statement(
            wheat="100000",
            seeds_and_plants="6500",
            salaries_wages_and_benefits="30000",
            chart_b=((MANITOBA, "40000", "6000"),),
        )
    )
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_B_ROW_3_MB).value == D("40")
    assert farm.get(FARM_CHART_B_ROW_6_MB).value == D("20")
    assert farm.get(FARM_CHART_B_ROW_8_MB).value == D("30")
    assert farm.get(FARM_CHART_B_ROW_9_MB).value == D("10950.00")
    assert farm.get(FARM_CHART_B_ROW_11_MB).value == D("5520.00")
    assert farm.get(FARM_CHART_C_AMOUNT_MB).value == D("12.64")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_MB).value == D("40000.00")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("12.64")


def test_part_3_and_part_4_add_across_two_chart_b_statements() -> None:
    # The worked example and a second statement: Ontario row 1 of 20,000 and row 4 of 5,000, gross
    # income 50,000 and salaries 10,000 (line 9898 is 20,000). Its row 3 is 40%, row 6 is 50%, row 7
    # is 90%, row 8 is 45%, row 9 is 20,000 times 45% = 9,000.00, row 11 is 9,000 times 184/365 =
    # 4,536.99 (rounded half-up), and Chart C is 4,536.99 times 0.229% = 10.39.
    # Part 3 adds the rows: line 67067 is 60,000 + 20,000 = 80,000; line 67071 is 15,000 + 5,000 =
    # 20,000; line 67075 is 100,000 + 50,000 = 150,000; line 67076 is 30,000 + 10,000 = 40,000.
    # Part 4 is 23.17 + 10.39 = 33.56, and line 5B is the same.
    result = run_dw(
        EXAMPLE,
        statement(
            wheat="50000",
            seeds_and_plants="10000",
            salaries_wages_and_benefits="10000",
            chart_b=((ONTARIO, "20000", "5000"),),
        ),
    )
    form = only(result["ca/t2043"])
    second = result["ca/t2042"][1]

    assert second.get(FARM_CHART_B_ROW_3_ON).value == D("40")
    assert second.get(FARM_CHART_B_ROW_11_ON).value == D("4536.99")
    assert second.get(FARM_CHART_C_AMOUNT_ON).value == D("10.39")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("80000.00")
    assert form.get(FUEL_CHARGE_CHART_B_SALARIES_ON).value == D("20000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_GROSS_INCOME).value == D("150000.00")
    assert form.get(FUEL_CHARGE_CHART_B_TOTAL_SALARIES).value == D("40000.00")
    assert form.get(FUEL_CHARGE_CHART_C_TOTAL_ON).value == D("33.56")
    assert form.get(FUEL_CHARGE_PART_4_TOTAL).value == D("33.56")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("33.56")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("33.56")


# --- review findings: line 5B gated like 5A; a Chart B statement is not also counted in Part 2 ---


def test_a_chart_b_business_under_25000_of_expenses_gives_no_5b_credit() -> None:
    # Line 67061 is the 20,000 of amount 6 (no other business), under the 25,000 threshold: 5A and
    # 5B are both gated to 0, though Chart C still gives 15.58. Row 6 is 15,000 of 20,000 (75%), so
    # row 7 is 135 and row 8 is 67.5%; row 9 is 13,500.00, row 11 is 13,500 times 184/365, which
    # is 6,805.48, and 6,805.48 times 0.229% is 15.5845, which is 15.58.
    result = run_dw(
        statement(
            wheat="100000",
            salaries_wages_and_benefits="20000",
            chart_b=((ONTARIO, "60000", "15000"),),
        )
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_GROSS_FARMING_EXPENSES).value == D("20000.00")
    assert form.get(FUEL_CHARGE_CHART_C_TOTAL_ON).value == D("15.58")
    assert form.get(FUEL_CHARGE_PART_4_TOTAL).value == D("15.58")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("0")


def test_a_statement_with_chart_b_and_province_1_gives_only_the_chart_b_credit() -> None:
    # The worked example, with the designated province left as Ontario (code 1). Part 2 would also
    # count its Chart A amount 8 (the Ontario farm of 36,500), but the statement uses Chart B, so
    # the Part 2 condition fails and the statement counts only through Chart B: 5A is 0, 5B is
    # 23.17 and line 47556 is 23.17, not 23.17 plus a second credit.
    result = run_dw(
        statement(
            wheat="100000",
            seeds_and_plants="6500",
            salaries_wages_and_benefits="30000",
            province=ONTARIO,
            chart_b=((ONTARIO, "60000", "15000"),),
        )
    )
    form = only(result["ca/t2043"])

    assert form.get(FUEL_CHARGE_PART_2_TOTAL).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("23.17")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("23.17")


# --- the Chart B province list: one statement with two provinces, a province with no row, two rows
# for one province, and the refusals -------------------------------------------------------------


def test_one_statement_with_ontario_and_manitoba_rows_gives_each_province_its_own_column() -> None:
    # The worked example's Ontario row (60,000 and 15,000) and a Manitoba row (40,000 and 6,000) on
    # one statement: rows 2 and 5 are still 100,000 and 30,000. Ontario is as in the worked example:
    # row 8 is 55, row 9 is 20,075.00, row 11 is 10,120.00 and Chart C is 23.17. Manitoba is as in
    # the Manitoba case: row 3 is 40, row 6 is 20, row 7 is 60, row 8 is 30 (note 9 does not
    # apply), row 9 is 36,500 times 30% = 10,950.00, row 11 is 10,950 times 184/365 = 5,520.00, and
    # Chart C is 5,520 times 0.229% = 12.6408, which is 12.64. Part 4 is 23.17 + 12.64 = 35.81. No
    # Part 2 business, so 5A is 0; 36,500 of expenses is over 25,000, so 5B is 35.81 and line 47556
    # is 35.81.
    result = run_dw(
        statement(
            wheat="100000",
            seeds_and_plants="6500",
            salaries_wages_and_benefits="30000",
            chart_b=((ONTARIO, "60000", "15000"), (MANITOBA, "40000", "6000")),
        )
    )
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_B_ROW_8_ON).value == D("55")
    assert farm.get(FARM_CHART_B_ROW_9_ON).value == D("20075.00")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("10120.00")
    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("23.17")
    assert farm.get(FARM_CHART_B_ROW_3_MB).value == D("40")
    assert farm.get(FARM_CHART_B_ROW_6_MB).value == D("20")
    assert farm.get(FARM_CHART_B_ROW_8_MB).value == D("30")
    assert farm.get(FARM_CHART_B_ROW_9_MB).value == D("10950.00")
    assert farm.get(FARM_CHART_B_ROW_11_MB).value == D("5520.00")
    assert farm.get(FARM_CHART_C_AMOUNT_MB).value == D("12.64")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("60000.00")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_MB).value == D("40000.00")
    assert form.get(FUEL_CHARGE_PART_4_TOTAL).value == D("35.81")
    assert form.get(FUEL_CHARGE_PART_5A_CREDIT).value == D("0")
    assert form.get(FUEL_CHARGE_PART_5B_CREDIT).value == D("35.81")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("35.81")


def test_a_province_with_no_row_counts_as_zero_and_the_other_province_still_computes() -> None:
    # Only a Manitoba row (40,000 and 6,000): Ontario has no row, so its row 1 and row 4 are 0. Its
    # row 3 is 0 of 100,000 and its row 6 is 0 of 30,000, so row 7, row 8, rows 9 and 11 and Chart C
    # are 0 for Ontario. Manitoba is as in the Manitoba case: Chart C is 12.64, and that is the
    # whole credit.
    result = run_dw(
        statement(
            wheat="100000",
            seeds_and_plants="6500",
            salaries_wages_and_benefits="30000",
            chart_b=((MANITOBA, "40000", "6000"),),
        )
    )
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_B_ROW_3_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_6_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("0")
    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("0")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("0")
    assert farm.get(FARM_CHART_B_ROW_3_MB).value == D("40")
    assert farm.get(FARM_CHART_C_AMOUNT_MB).value == D("12.64")
    assert form.get(FUEL_CHARGE_CREDIT_FARMERS).value == D("12.64")


def test_two_rows_for_one_province_add_into_its_column() -> None:
    # Two Ontario rows of 30,000 and 7,500 each make the column 60,000 and 15,000, as in the worked
    # example, so every figure is the worked example's: row 3 is 60, row 6 is 50, row 9 is
    # 20,075.00, row 11 is 10,120.00, Chart C is 23.17, and Part 3 has 60,000 of Ontario gross
    # income.
    result = run_dw(
        statement(
            wheat="100000",
            seeds_and_plants="6500",
            salaries_wages_and_benefits="30000",
            chart_b=((ONTARIO, "30000", "7500"), (ONTARIO, "30000", "7500")),
        )
    )
    farm = only(result["ca/t2042"])
    form = only(result["ca/t2043"])

    assert farm.get(FARM_CHART_B_ROW_3_ON).value == D("60")
    assert farm.get(FARM_CHART_B_ROW_6_ON).value == D("50")
    assert farm.get(FARM_CHART_B_ROW_9_ON).value == D("20075.00")
    assert farm.get(FARM_CHART_B_ROW_11_ON).value == D("10120.00")
    assert farm.get(FARM_CHART_C_AMOUNT_ON).value == D("23.17")
    assert form.get(FUEL_CHARGE_CHART_B_GROSS_INCOME_ON).value == D("60000.00")


@pytest.mark.parametrize("code", [0, 9])
def test_a_province_code_outside_one_to_eight_is_refused_naming_its_item(code: int) -> None:
    # The second row's code is neither 1 nor 8: the statement is refused, naming item 2 of the list.
    with pytest.raises(InvalidRecordError, match="item 2"):
        run_dw(statement(wheat="100000", chart_b=((ONTARIO, "60000", "15000"), (code, "1", "0"))))


def test_a_negative_chart_b_amount_is_refused_by_the_list_naming_its_item() -> None:
    with pytest.raises(
        NegativeArtifactError,
        match=r"item 1: ca/farm_chart_b_province_gross_income cannot be negative, got -1",
    ):
        run_dw(statement(wheat="100000", chart_b=((ONTARIO, "-1", "0"),)))
