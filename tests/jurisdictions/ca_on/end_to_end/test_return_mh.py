"""CA-ON 2025 end to end: return mh, Form T936 "Calculation of Cumulative Net Investment Loss (CNIL)
to December 31, 2025" as its own form, and the two amounts Form T657 reads from it.

The worked return `returns/2025_return_mh.yaml` (every line of Parts 1 to 3 and Chart A of the form
non-zero) is checked by `test_worked_returns.py`. This module computes the cases it does not
express: the printed sentences of Chart A that send a line to 0, the floors, the signs, the
lesser-of of Part 1 line 7, the negative Part 2 line 10, the amounts of Form T2048 (Return BE),
and the two figures Form T657 takes from the form (Step 1 line 15, Step 2 line 16).

Every figure is worked by hand from the printed form (`pdftotext -layout t936-25e.pdf`), as in the
comments of each test.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    T657_CUMULATIVE_NET_INVESTMENT_LOSS,
    T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS,
    T936_ADDITIONAL_INVESTMENT_EXPENSES,
    T936_ADDITIONAL_INVESTMENT_INCOME,
    T936_CHART_A_LINE_3,
    T936_CHART_A_LINE_7,
    T936_CHART_A_LINE_8,
    T936_CHART_A_LINE_9,
    T936_CHART_A_LINE_11,
    T936_CHART_A_LINE_13,
    T936_CHART_A_LINE_14,
    T936_CHART_A_LINE_14_BEFORE_GATE,
    T936_CHART_A_LINE_17,
    T936_CHART_A_LINE_19,
    T936_CHART_A_LINE_19_BEFORE_GATE,
    T936_CNIL,
    T936_CUMULATIVE_INVESTMENT_EXPENSES,
    T936_CUMULATIVE_INVESTMENT_INCOME,
    T936_EXPLORATION_EXPENSES_AT_HALF,
    T936_INVESTMENT_INCOME,
    T936_LINE_16,
    T936_NET_RENTAL_INCOME,
    T936_NET_RENTAL_LOSS,
    T936_OTHER_INVESTMENT_EXPENSES,
    T936_OTHER_PROPERTY_INCOME,
    T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS,
    T936_PARTNERSHIP_LOSSES,
    T936_RECOVERY_OF_EXPLORATION_EXPENSES,
    T936_T2048_LINE_17215,
    T936_T2048_LINE_17216,
    T936_T2048_LINE_17218,
    T936_T2048_LINE_17218_FOR_2025,
    T936_TOTAL_INVESTMENT_EXPENSES,
    T936_TOTAL_INVESTMENT_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    assert_values,
    run_be,
    service,
    starting,
)

T936 = "ca/t936"
RETURN = "ca-on/return"

# The figures of return MH that Form T936 reads and the filer enters: Part 3 line 15 (4,000), line
# 20 (2,500), the 2024 part of line 17 (700), and Chart A lines 15 and 16 (box 21 and box 30 of
# the T3 slips, 800 and 300).
MH_T936 = {
    "investment_expenses_previous_years": "4000",
    "investment_income_previous_years": "2500",
    "t2048_line_17218_for_2024": "700",
    "t3_box_21_capital_gains": "800",
    "t3_box_30_capital_gains": "300",
}
# The T776 statement of return MH: no income, advertising of 900, so the net rental income is -900.
MH_RENTAL = {"rental_expenses": {"advertising": ("900", "0", "0")}}


def mh_inputs(**overrides: Any) -> dict[str, Any]:
    """The inputs of `returns/2025_return_mh.yaml` as keyword arguments of `starting`, with the
    `overrides` replacing any of them (`t936_amounts` replaces the five T936 amounts)."""
    inputs: dict[str, Any] = {
        "employment_income": "0",
        "share_dispositions": (("10000", "7000", "0"),),
        "unused_rrsp_contributions": "0",
        "rrsp_contributions": "0",
        "rrsp_deduction_limit": "0",
        "rrsp_amount_deducted": "0",
        "union_dues": "0",
        "qsbcs_dispositions": (("5000", "3000", "0"),),
        "qffp_dispositions": (("2400", "1400", "0"),),
        "qffp_foreclosure_dispositions": (("1000", "600", "0"),),
        "rental_statements": (MH_RENTAL,),
        "total_carrying_charges": "1000",
        "total_interest_expenses": "200",
        "limited_partnership_at_risk_amount": "1000",
        "limited_partnership_losses_of_other_years": "300",
        "exploration_and_development_expenses": "2000",
        "t5_investment_income": "3000",
        "other_income": "800",
        "qbt_exploration_recovery_income": "800",
        "net_partnership_income": "1000",
        "partnership_taxable_capital_gains": "400",
        "non_active_partnership_losses": "700",
        "other_investment_expenses": "150",
        "other_property_income": "250",
        "t3_capital_gains_or_losses": "800",
        "partnership_gains_at_full_inclusion": "600",
        "t2017_amounts": {1: "500"},
        "unapplied_net_capital_losses_2001_to_2024": "5000",
        "net_capital_losses_claimed": "1800",
        "t936_amounts": MH_T936,
    }
    return {**inputs, **overrides}


def run_mh(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return MH (a share disposition of 10,000 with a cost base of
    7,000, and the rest of `mh_inputs`), with the keyword overrides given."""
    artifacts = starting(**mh_inputs(**overrides))
    return service().compute(CA_ON, 2025, *artifacts)


def return_mh(**overrides: Any) -> Worksheet:
    (worksheet,) = run_mh(**overrides)[RETURN]
    return worksheet


def t936_form(**overrides: Any) -> Worksheet:
    (worksheet,) = run_mh(**overrides)[T936]
    return worksheet


# The inputs of a filer whose only gain is on QSBCS: Schedule 3 line 19900 is 50% x 2,000 = 1,000,
# and Chart A line 13 is the same 1,000, so line 14 is 0 although line 1 is not.
ONLY_QSBCS = {
    "share_dispositions": (),
    "qffp_dispositions": (),
    "qffp_foreclosure_dispositions": (),
    "t3_capital_gains_or_losses": "0",
    "partnership_gains_at_full_inclusion": "0",
    "t2017_amounts": {},
    "net_capital_losses_claimed": "0",
}
# The inputs of a filer with no gains at all: Schedule 3 line 19900 is 0 (line 1 of Chart A).
NO_GAINS = {**ONLY_QSBCS, "qsbcs_dispositions": ()}


# --- Chart A of return MH ----------------------------------------------------------------------


def test_chart_a_lines_1_to_14_are_worked_from_the_printed_form() -> None:
    # Line 1 is 4,450.00 (3,850.00 + 600.00); line 2 is 0 (no Form T2048); line 3 is 4,450.00. Lines
    # 4 to 6 are 2,000, 1,000 and 400, so line 7 is 3,400. Line 19200 of Schedule 3 is reported
    # (500), so line 8 is line 13 of Form T2017, 500. Line 9 is 3,900; line 10 is 50%, so line 11
    # is 1,950.00. Line 12 is 0, line 13 is 1,950.00 and line 14 is 4,450.00 - 1,950.00 = 2,500.00.
    assert_values(
        t936_form(),
        (
            (T936_T2048_LINE_17215, "0"),
            (T936_CHART_A_LINE_3, "4450.00"),
            (T936_CHART_A_LINE_7, "3400.00"),
            (T936_CHART_A_LINE_8, "500.00"),
            (T936_CHART_A_LINE_9, "3900.00"),
            (T936_CHART_A_LINE_11, "1950.00"),
            (T936_T2048_LINE_17216, "0"),
            (T936_CHART_A_LINE_13, "1950.00"),
            (T936_CHART_A_LINE_14_BEFORE_GATE, "2500.00"),
            (T936_CHART_A_LINE_14, "2500.00"),
        ),
    )


def test_chart_a_lines_15_to_20_are_worked_from_the_printed_form() -> None:
    # Box 21 is 800 and box 30 is 300: line 17 is 500; line 18 is 50%, so line 19 is 250.00; line
    # 20 is 2,500.00 - 250.00 = 2,250.00.
    assert_values(
        t936_form(),
        (
            (T936_CHART_A_LINE_17, "500"),
            (T936_CHART_A_LINE_19_BEFORE_GATE, "250.00"),
            (T936_CHART_A_LINE_19, "250.00"),
            (T936_ADDITIONAL_INVESTMENT_INCOME, "2250.00"),
        ),
    )


def test_a_negative_line_17_is_kept_signed_and_adds_to_line_20() -> None:
    # Box 21 is 0 and box 30 is 400: line 17 is -400 (no floor is printed), line 19 is 50% x -400 =
    # -200.00 and line 20 is 2,500.00 - (-200.00) = 2,700.00.
    found = t936_form(
        t936_amounts={**MH_T936, "t3_box_21_capital_gains": "0", "t3_box_30_capital_gains": "400"}
    )

    assert_values(
        found,
        (
            (T936_CHART_A_LINE_17, "-400"),
            (T936_CHART_A_LINE_19, "-200.00"),
            (T936_ADDITIONAL_INVESTMENT_INCOME, "2700.00"),
        ),
    )


def test_without_a_t3_slip_line_19_is_0_and_line_20_is_line_14() -> None:
    # Boxes 21 and 30 both 0: line 17 and line 19 are 0 and line 20 is line 14, 2,500.00.
    found = t936_form(
        t936_amounts={**MH_T936, "t3_box_21_capital_gains": "0", "t3_box_30_capital_gains": "0"}
    )

    assert_values(
        found,
        ((T936_CHART_A_LINE_19, "0"), (T936_ADDITIONAL_INVESTMENT_INCOME, "2500.00")),
    )


def test_line_14_of_0_sends_a_negative_line_19_to_0() -> None:
    # "If the total from line 14 is "0", do not complete lines 15 to 19, and enter "0" on line 20".
    # Only QSBCS gains of 2,000: line 1 is 1,000.00, line 3 is 1,000.00, line 7 is 2,000, line 8 is
    # 0 (no line 19200), line 9 is 2,000, line 11 is 1,000.00, line 13 is 1,000.00 and line 14 is
    # 1,000.00 - 1,000.00 = 0. Box 30 of 400 would give line 19 = 50% x -400 = -200.00 and line 20 =
    # 0 - (-200.00) = 200.00 if lines 15 to 19 were completed: line 19 is 0 and line 20 is 0.
    found = t936_form(
        **ONLY_QSBCS,
        t936_amounts={**MH_T936, "t3_box_21_capital_gains": "0", "t3_box_30_capital_gains": "400"},
    )

    assert_values(
        found,
        (
            (T936_CHART_A_LINE_3, "1000.00"),
            (T936_CHART_A_LINE_13, "1000.00"),
            (T936_CHART_A_LINE_14, "0"),
            (T936_CHART_A_LINE_19_BEFORE_GATE, "-200.00"),
            (T936_CHART_A_LINE_19, "0"),
            (T936_ADDITIONAL_INVESTMENT_INCOME, "0"),
        ),
    )


def test_line_1_of_0_makes_line_14_and_line_20_0() -> None:
    # "If the amount is "0", do not complete lines 2 to 17, and enter "0" on line 20": no gains, so
    # line 1 is 0 and lines 3, 7, 9, 11 and 13 are 0; line 14 is 0 and so are lines 19 and 20 even
    # with box 30 of 400 entered.
    found = t936_form(
        **NO_GAINS,
        t936_amounts={**MH_T936, "t3_box_21_capital_gains": "0", "t3_box_30_capital_gains": "400"},
    )

    assert_values(
        found,
        (
            (T936_CHART_A_LINE_3, "0"),
            (T936_CHART_A_LINE_7, "0"),
            (T936_CHART_A_LINE_11, "0"),
            (T936_CHART_A_LINE_13, "0"),
            (T936_CHART_A_LINE_14, "0"),
            (T936_CHART_A_LINE_19, "0"),
            (T936_ADDITIONAL_INVESTMENT_INCOME, "0"),
        ),
    )


def test_a_negative_schedule_3_line_19900_is_signed_on_line_1_and_line_14_is_0() -> None:
    # Share loss of 3,000 (proceeds 4,000, cost 7,000) and no other gain or loss: line 1 of Chart A
    # is "if negative, show the amount in brackets": 50% x -3,000 = -1,500.00. Line 3 is -1,500.00,
    # line 13 is 0 and line 14 is the floor "if negative, enter "0"" of -1,500.00 - 0.
    found = t936_form(**{**NO_GAINS, "share_dispositions": (("4000", "7000", "0"),)})

    assert_values(
        found,
        (
            (T936_CHART_A_LINE_3, "-1500.00"),
            (T936_CHART_A_LINE_13, "0"),
            (T936_CHART_A_LINE_14, "0"),
            (T936_ADDITIONAL_INVESTMENT_INCOME, "0"),
        ),
    )


# --- Part 1 of return MH -------------------------------------------------------------------------


def test_part_1_lines_1_to_6_and_the_total_a() -> None:
    # Line 1 (line 22100) is 1,000 + 200 = 1,200; line 2 is the net rental loss 900; line 3 is the
    # non-active partnership losses 700; line 4 (line 25100) is 300; line 5 is 50% x 2,000 =
    # 1,000.00; line 6 is 150; line 7 is the lesser of line 20 of Chart A (2,250.00) and line 25300
    # (1,800.00), 1,800.00. A is 1,200 + 900 + 700 + 300 + 1,000 + 150 + 1,800 = 6,050.00.
    assert_values(
        t936_form(),
        (
            (T936_NET_RENTAL_LOSS, "900"),
            (T936_PARTNERSHIP_LOSSES, "700"),
            (T936_EXPLORATION_EXPENSES_AT_HALF, "1000.00"),
            (T936_OTHER_INVESTMENT_EXPENSES, "150"),
            (T936_ADDITIONAL_INVESTMENT_EXPENSES, "1800.00"),
            (T936_TOTAL_INVESTMENT_EXPENSES, "6050.00"),
        ),
    )


def test_line_7_is_line_20_of_chart_a_when_that_is_the_lesser() -> None:
    # Line 25300 of 3,000 is above line 20 of Chart A (2,250.00): line 7 is 2,250.00 and A is
    # 6,050.00 - 1,800.00 + 2,250.00 = 6,500.00.
    found = t936_form(net_capital_losses_claimed="3000")

    assert_values(
        found,
        (
            (T936_ADDITIONAL_INVESTMENT_EXPENSES, "2250.00"),
            (T936_TOTAL_INVESTMENT_EXPENSES, "6500.00"),
        ),
    )


# --- Part 2 of return MH -------------------------------------------------------------------------


def test_part_2_lines_8_to_13_and_the_total_b() -> None:
    # Line 8 is 0.00 + 3,000 = 3,000; line 9 (a net rental loss) is 0; line 10 is 1,000 - 400 =
    # 600; line 11 is 250; line 12 is 50% x 800 (the recovery of exploration and development
    # expenses, all of the 800 on line 13000) = 400.00; line 13 is line 20 of Chart A, 2,250.00.
    # B is 3,000 + 0 + 600 + 250 + 400 + 2,250 = 6,500.00.
    assert_values(
        t936_form(),
        (
            (T936_INVESTMENT_INCOME, "3000"),
            (T936_NET_RENTAL_INCOME, "0"),
            (T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS, "600"),
            (T936_OTHER_PROPERTY_INCOME, "250"),
            (T936_RECOVERY_OF_EXPLORATION_EXPENSES, "400.00"),
            (T936_TOTAL_INVESTMENT_INCOME, "6500.00"),
        ),
    )


def test_a_positive_net_rental_income_is_line_9_and_not_a_line_2_loss() -> None:
    # Rental income of 1,500 and advertising of 900: net rental income 600. Line 2 is 0 and line 9
    # is 600. A is 6,050 - 900 = 5,150.00; B is 6,500 + 600 = 7,100.00. Line 16 is 5,150 + 4,000 =
    # 9,150; line 18 is 9,150 - 700 = 8,450; line 21 is 7,100 + 2,500 = 9,600; C is 8,450 - 9,600 =
    # -1,150 and is entered as 0.
    found = t936_form(rental_statements=({"rental_other_income": "1500", **MH_RENTAL},))

    assert_values(
        found,
        (
            (T936_NET_RENTAL_LOSS, "0"),
            (T936_NET_RENTAL_INCOME, "600"),
            (T936_TOTAL_INVESTMENT_EXPENSES, "5150.00"),
            (T936_TOTAL_INVESTMENT_INCOME, "7100.00"),
            (T936_CUMULATIVE_INVESTMENT_EXPENSES, "8450.00"),
            (T936_CUMULATIVE_INVESTMENT_INCOME, "9600.00"),
            (T936_CNIL, "0"),
        ),
    )


def test_taxable_capital_gains_above_line_12200_leave_line_10_negative() -> None:
    # Line 10 is "Net income from limited or non-active partnership (line 12200) other than taxable
    # capital gains" and the form prints no limit or floor: a line 12200 amount of 1,000 holding
    # 1,000.01 of taxable capital gains (the partnership's other income is a loss of 0.01) gives
    # line 10 of (0.01), and line B is 0.01 below its figure with gains of 1,000.
    found = t936_form(partnership_taxable_capital_gains="1000.01")
    at_line_12200 = t936_form(partnership_taxable_capital_gains="1000")

    assert found.get(T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("-0.01")
    assert at_line_12200.get(T936_TOTAL_INVESTMENT_INCOME).value - found.get(
        T936_TOTAL_INVESTMENT_INCOME
    ).value == D("0.01")


def test_taxable_capital_gains_equal_to_line_12200_leave_line_10_at_0() -> None:
    found = t936_form(partnership_taxable_capital_gains="1000")

    assert found.get(T936_PARTNERSHIP_INCOME_OTHER_THAN_GAINS).value == D("0")


# --- Part 3 of return MH -------------------------------------------------------------------------


def test_part_3_lines_16_to_21_and_line_c() -> None:
    # Line 14 is A, 6,050.00; line 15 is 4,000; line 16 is 10,050.00. Line 17 is the 2024 part 700
    # plus the 2025 part (0, no Form T2048) = 700; line 18 is 10,050.00 - 700 = 9,350.00. Line 19
    # is B, 6,500.00; line 20 is 2,500; line 21 is 9,000.00. C is 9,350.00 - 9,000.00 = 350.00.
    assert_values(
        t936_form(),
        (
            (T936_LINE_16, "10050.00"),
            (T936_T2048_LINE_17218_FOR_2025, "0"),
            (T936_T2048_LINE_17218, "700"),
            (T936_CUMULATIVE_INVESTMENT_EXPENSES, "9350.00"),
            (T936_CUMULATIVE_INVESTMENT_INCOME, "9000.00"),
            (T936_CNIL, "350.00"),
        ),
    )


def test_line_18_is_signed_and_c_is_floored_at_0() -> None:
    # Line 15 of 0 and line 17 (2024 part) of 7,000: line 16 is 6,050.00 and line 18 is 6,050.00 -
    # 7,000 = -950.00 (no floor is printed on line 18); line 21 is 9,000.00; C = -950.00 - 9,000.00
    # is negative and is entered as 0.
    found = t936_form(
        t936_amounts={
            **MH_T936,
            "investment_expenses_previous_years": "0",
            "t2048_line_17218_for_2024": "7000",
        }
    )

    assert_values(
        found,
        ((T936_CUMULATIVE_INVESTMENT_EXPENSES, "-950.00"), (T936_CNIL, "0")),
    )


def test_a_c_above_zero_when_the_income_of_previous_years_is_less() -> None:
    # Line 20 of 1,000 instead of 2,500: line 21 is 6,500 + 1,000 = 7,500.00 and C is 9,350.00 -
    # 7,500.00 = 1,850.00.
    found = t936_form(t936_amounts={**MH_T936, "investment_income_previous_years": "1000"})

    assert_values(found, ((T936_CNIL, "1850.00"),))


# --- Form T657 reads the form --------------------------------------------------------------------


def test_form_t657_step_1_line_15_and_step_2_line_16_are_the_two_exports_of_the_form() -> None:
    # Step 1 line 15 is line 14 of Chart A, 2,500.00; Step 2 line 16 is line C, 350.00.
    worksheet = return_mh()

    assert worksheet.get(T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("2500.00")
    assert worksheet.get(T657_CUMULATIVE_NET_INVESTMENT_LOSS).value == D("350.00")


def test_the_two_t657_amounts_follow_the_form_when_its_inputs_change() -> None:
    # Line 20 of 1,000 instead of 2,500 (C is 1,850.00, above) and a box 30 of 400 with box 21 of
    # 0 (line 17 is -400, line 19 is -200.00, line 20 of Chart A is 2,700.00, line 7 is the lesser
    # of 2,700.00 and 1,800.00 = 1,800.00, so A is unchanged at 6,050.00; B is 6,500.00 + 450.00 =
    # 6,950.00). Line 21 is 6,950.00 + 1,000 = 7,950.00 and C is 9,350.00 - 7,950.00 = 1,400.00.
    worksheet = return_mh(
        t936_amounts={
            **MH_T936,
            "investment_income_previous_years": "1000",
            "t3_box_21_capital_gains": "0",
            "t3_box_30_capital_gains": "400",
        }
    )

    assert worksheet.get(T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("2500.00")
    assert worksheet.get(T657_CUMULATIVE_NET_INVESTMENT_LOSS).value == D("1400.00")


def test_the_return_without_gains_has_both_t657_amounts_at_0_except_the_cnil() -> None:
    # No gains: Chart A line 14 is 0, so Step 1 line 15 is 0. Part 3 is unaffected by the gate
    # except through lines 7 and 13 (both 0 with line 20 of 0): A = 1,200 + 900 + 700 + 300 +
    # 1,000 + 150 + 0 = 4,250.00; B = 3,000 + 0 + 600 + 250 + 400 + 0 = 4,250.00; line 18 = 4,250 +
    # 4,000 - 700 = 7,550.00; line 21 = 4,250 + 2,500 = 6,750.00; C = 800.00.
    worksheet = return_mh(**NO_GAINS)

    assert worksheet.get(T657_NET_NON_ELIGIBLE_TAXABLE_CAPITAL_GAINS).value == D("0")
    assert worksheet.get(T657_CUMULATIVE_NET_INVESTMENT_LOSS).value == D("800.00")


# --- Form T2048 amounts on lines 2, 12 and 17 (Return BE) -------------------------------------


def test_chart_a_lines_2_and_12_and_part_3_line_17_take_the_t2048_figures_of_return_be() -> None:
    # Return BE's Form T2048 has line 17215 of 70,000.00, line 17216 of 70,000.00 (QSBCS) and line
    # 17218 of 5,500.00. Line 17 is 0 (2024 part) + 5,500.00.
    found = run_be()[T936][0]

    assert_values(
        found,
        (
            (T936_T2048_LINE_17215, "70000.00"),
            (T936_T2048_LINE_17216, "70000.00"),
            (T936_T2048_LINE_17218_FOR_2025, "5500.00"),
            (T936_T2048_LINE_17218, "5500.00"),
        ),
    )


def test_the_2024_part_of_line_17_is_added_to_the_t2048_2025_figure() -> None:
    # 1,000 for 2024 + 5,500.00 for 2025 = 6,500.00.
    found = run_be(t936_amounts={"t2048_line_17218_for_2024": "1000"})[T936][0]

    assert found.get(T936_T2048_LINE_17218).value == D("6500.00")


def test_a_recovery_of_exploration_expenses_above_line_13000_is_refused_naming_both_kinds() -> None:
    # Part 2 line 12 is "50% of income from the recovery of exploration and development expenses
    # (line 13000)": the recovery is a part of the 800 of line 13000, so 800.01 cannot be in it, an
    # input error, not capped. 800 itself is allowed (line 12 is 50% x 800 = 400.00, above), and 500
    # gives 50% x 500 = 250.00.
    with pytest.raises(InputAboveBoundError) as raised:
        run_mh(qbt_exploration_recovery_income="800.01")

    assert "ca/qbt_exploration_recovery_income 800.01 is above ca/other_income 800" in str(
        raised.value
    )
    assert t936_form(qbt_exploration_recovery_income="500").get(
        T936_RECOVERY_OF_EXPLORATION_EXPENSES
    ).value == D("250.00")
