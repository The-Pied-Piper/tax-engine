"""CA-ON 2025 end to end: return FY (Schedule 8 with Part 5 completed: the employment income is
over-contributed and a CPT20 election is made, so line 24 of Part 3 is positive and Part 5 lines
75 and 77 are non-zero).

Return FY is `returns/2025_return_fy.yaml`: one Schedule 8 and no Form RC381, all Ontario
employment, with the CPT20 election on 8000 of employment earnings not shown on a T4. The figures
are chosen and worked out by hand from the form text, as CRA prints no Schedule 8 example. The
tests check the hand figure of each line the catalog names; the lines the catalog does not name
(for example Part 3 lines 4, 5 and 7) are checked in the YAML's description only, and the tax
figures are the engine's and are checked in the YAML only.
"""

from __future__ import annotations

from typing import Any

from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_CONTRIBUTIONS_DIFFERENCE,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_LINE_24_POSITIVE,
    CPP_OVERPAYMENT,
    CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_PART_3_OVERPAYMENT,
    CPP_PART_5_LINE_4,
    CPP_PART_5_LINE_22,
    CPP_PART_5_LINE_30,
    CPP_PART_5_LINE_43,
    CPP_PART_5_LINE_44,
    CPP_PART_5_LINE_45,
    CPP_PART_5_LINE_46,
    CPP_PART_5_LINE_47,
    CPP_PART_5_LINE_48,
    CPP_PART_5_LINE_49,
    CPP_PART_5_LINE_57,
    CPP_PART_5_LINE_69,
    CPP_PART_5_LINE_70,
    CPP_PART_5_LINE_71,
    CPP_PART_5_LINE_72,
    CPP_PART_5_LINE_73,
    CPP_PART_5_LINE_74,
    CPP_PART_5_LINE_75,
    CPP_PART_5_LINE_75_BASE,
    CPP_PART_5_LINE_77,
    CPP_PART_5_LINE_80,
    CPP_PART_5_LINE_83,
    CPP_PART_5_LINE_84,
    CPP_PART_5_LINE_87,
    CPP_PART_5_LINE_88,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE,
    NET_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_fy(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return FY's inputs (`returns/2025_return_fy.yaml`): employment income of 50000 on one T4 slip
    for Ontario employment (box 26 of 50500, box 16 of 3000.00 and box 16A of 0), with 12 months
    for CPP, no self-employment income, and the CPT20 election on 8000 of employment earnings not
    shown on a T4, with Part 5 completed. The return carries one Schedule 8 and no Form RC381."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "50500",
        "cpp_t4_base_and_first_additional_contributions": "3000.00",
        "cpp_t4_second_additional_contributions": "0",
        "income_tax_deducted": "13000",
        "cpt20_earnings": "8000",
        "cpp_part_5_completed": 1,
        "schedule_8_copies": 1,
        "rc381_copies": 0,
    }
    return run("50000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def schedule_8_fy(**overrides: Any) -> Worksheet:
    (schedule_8,) = run_fy(**overrides)["ca/schedule_8"]
    return schedule_8


def return_fy(**overrides: Any) -> Worksheet:
    (worksheet,) = run_fy(**overrides)["ca-on/return"]
    return worksheet


def test_return_fy_carries_schedule_8_and_no_form_rc381() -> None:
    result = run_fy()

    assert result["ca/rc381"] == ()
    assert len(result["ca/schedule_8"]) == 1


def test_return_fy_part_3_lines_20_23_and_24_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "203.50"),
        (CPP_SECOND_ADDITIONAL_CONTRIBUTIONS_DIFFERENCE, "0.00"),
        (CPP_CONTRIBUTIONS_DIFFERENCE, "203.50"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_line_24_is_positive_so_part_3a_is_the_employment_route() -> None:
    schedule_8 = schedule_8_fy()

    assert schedule_8.get(CPP_LINE_24_POSITIVE).value == 1


def test_return_fy_part_3a_lines_are_the_hand_figures() -> None:
    # Part 3a is the employment route for a positive line 24. Its line 29 (203.50) is computed, but
    # Part 5 is completed, so the return takes Part 5's results instead.
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_PART_3_BASE_CONTRIBUTIONS_ON_RETURN, "2326.50"),
        (CPP_PART_3_ENHANCED_CONTRIBUTIONS_ON_RETURN, "470.00"),
        (CPP_PART_3_OVERPAYMENT, "203.50"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_part_5_lines_4_22_and_30_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_PART_5_LINE_4, "8000"),
        (CPP_PART_5_LINE_22, "8000"),
        (CPP_PART_5_LINE_30, "8000"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_part_5_lines_43_to_49_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_PART_5_LINE_43, "792.00"),
        (CPP_PART_5_LINE_44, "160.00"),
        (CPP_PART_5_LINE_45, "0.00"),
        (CPP_PART_5_LINE_46, "160.00"),
        (CPP_PART_5_LINE_47, "952.00"),
        (CPP_PART_5_LINE_48, "407.00"),
        (CPP_PART_5_LINE_49, "545.00"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_part_5_line_57_is_the_base_contributions_on_the_employment_income() -> None:
    schedule_8 = schedule_8_fy()

    assert schedule_8.get(CPP_PART_5_LINE_57).value == D("2326.50")


def test_return_fy_part_5_lines_69_to_74_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_PART_5_LINE_69, "470.00"),
        (CPP_PART_5_LINE_70, "396.00"),
        (CPP_PART_5_LINE_71, "80.00"),
        (CPP_PART_5_LINE_72, "476.00"),
        (CPP_PART_5_LINE_73, "203.50"),
        (CPP_PART_5_LINE_74, "272.50"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_part_5_line_a_is_split_by_line_75_and_line_77_is_the_remainder() -> None:
    # Line A is the lesser of line 72 (476.00) and line 73 (203.50). Line 75 is line A multiplied by
    # 83.1933%, and line 77 is line A less line 76 (the amount of line 75).
    schedule_8 = schedule_8_fy()

    assert schedule_8.get(CPP_PART_5_LINE_75_BASE).value == D("203.50")
    assert schedule_8.get(CPP_PART_5_LINE_75).value == D("169.30")
    assert schedule_8.get(CPP_PART_5_LINE_77).value == D("34.20")


def test_return_fy_part_5_lines_80_83_84_87_and_88_are_the_hand_figures() -> None:
    schedule_8 = schedule_8_fy()

    for kind, expected in (
        (CPP_PART_5_LINE_80, "226.70"),
        (CPP_PART_5_LINE_83, "45.80"),
        (CPP_PART_5_LINE_84, "0.00"),
        (CPP_PART_5_LINE_87, "0.00"),
        (CPP_PART_5_LINE_88, "352.50"),
    ):
        assert schedule_8.get(kind).value == D(expected), kind.identifier


def test_return_fy_t1_line_30800_is_part_5_line_57() -> None:
    assert return_fy().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2326.50")


def test_return_fy_t1_line_22215_is_part_5_line_69() -> None:
    assert return_fy().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("470.00")


def test_return_fy_t1_line_44800_is_zero_because_part_5_line_49_is_positive() -> None:
    # Part 5 line 50 (the overpayment) is taken only for a negative line 49 (545.00 here), so the
    # Part 3a overpayment of 203.50 is not carried to the return.
    assert return_fy().get(CPP_OVERPAYMENT).value == D("0")


def test_return_fy_t1_lines_42100_31000_and_22200_are_part_5_lines_49_70_and_88() -> None:
    worksheet = return_fy()

    for kind, expected in (
        (CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS, "545.00"),
        (CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS, "396.00"),
        (CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS, "352.50"),
    ):
        assert worksheet.get(kind).value == D(expected), kind.identifier


def test_return_fy_net_income_is_total_income_less_the_two_cpp_deductions() -> None:
    worksheet = return_fy()

    assert worksheet.get(TOTAL_INCOME).value == D("50000.00")
    # 50000.00 less the deductions of line 22215 (470.00) and line 22200 (352.50).
    assert worksheet.get(NET_INCOME).value == D("49177.50")
    assert worksheet.get(TAXABLE_INCOME).value == D("49177.50")
