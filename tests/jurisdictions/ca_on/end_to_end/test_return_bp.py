"""CA-ON 2025 end to end: return bp (the worked example of Form RC381: a T4 for Ontario employment
and a T4 for Quebec employment, employment income only, carried to the T1 lines)."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    NET_FEDERAL_TAX,
    NET_INCOME,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_PART_3_LINE_6,
    RC381_PART_3_LINE_7,
    RC381_PART_3_LINE_8,
    RC381_PART_3_LINE_9,
    RC381_PART_3_LINE_10,
    RC381_PART_3_LINE_11,
    RC381_PART_3_LINE_16,
    RC381_PART_3_LINE_18,
    RC381_PART_3_LINE_20,
    RC381_PART_3_LINE_21,
    RC381_PART_3_LINE_22,
    RC381_PART_3_LINE_23,
    RC381_PART_3_LINE_27,
    RC381_PART_3_LINE_29,
    RC381_PART_3_LINE_31,
    RC381_PART_3_LINE_38,
    RC381_PART_3_LINE_40,
    RC381_PART_3_LINE_41,
    RC381_PART_3_LINE_42,
    RC381_PART_3_LINE_43,
    RC381_PART_3_LINE_52,
    RC381_PART_3_LINE_53,
    RC381_PART_3_LINE_59,
    RC381_PART_3_LINE_60,
    RC381_PART_3_LINE_61,
    RC381_PART_3_LINE_68,
    RC381_PART_3_LINE_69,
    REFUND_OR_BALANCE_OWING,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on.catalog import ONTARIO_TAX
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_bp(**overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return BP's inputs (`returns/2025_return_bp.yaml`): employment income of 70000 on a T4 for
    Ontario employment (box 26 of 30000 and box 16 of 1785.00) and a T4 for Quebec employment (box
    26 of 40000 and box 17 of 2500.00), with 12 months for CPP and QPP, and no election and no
    other income. The return carries one Form RC381 and no Schedule 8."""
    arguments: dict[str, Any] = {
        "cpp_months": 12,
        "qpp_months": 12,
        "t4_cpp_pensionable_earnings_outside_quebec": "30000",
        "t4_qpp_pensionable_earnings_in_quebec": "40000",
        "cpp_t4_base_and_first_additional_contributions": "1785.00",
        "t4_qpp_contributions_box_17": "2500.00",
        "income_tax_deducted": "12000",
        "schedule_8_copies": 0,
        "rc381_copies": 1,
    }
    return run("70000", (), "0", "0", "0", "0", "0", **{**arguments, **overrides})


def form_bp(**overrides: Any) -> Worksheet:
    (rc381,) = run_bp(**overrides)["ca/rc381"]
    return rc381


def return_bp(**overrides: Any) -> Worksheet:
    (worksheet,) = run_bp(**overrides)["ca-on/return"]
    return worksheet


def test_return_bp_carries_form_rc381_and_no_schedule_8() -> None:
    result = run_bp()

    assert result["ca/schedule_8"] == ()
    assert len(result["ca/rc381"]) == 1


def test_return_bp_part_3_line_6_is_30000_over_70000_cut_at_the_fifth_decimal_place() -> None:
    assert form_bp().get(RC381_PART_3_LINE_6).value == Rate(D("0.42857"))


def test_return_bp_lines_7_to_10_are_the_table_amounts_times_line_6() -> None:
    rc381 = form_bp()

    assert rc381.get(RC381_PART_3_LINE_7).value == D("34799.88")
    assert rc381.get(RC381_PART_3_LINE_8).value == D("30557.04")
    # 3500.00 x 0.42857 = 1499.995, which rounds half up to 1500.00.
    assert rc381.get(RC381_PART_3_LINE_9).value == D("1500.00")
    assert rc381.get(RC381_PART_3_LINE_10).value == D("4242.84")


def test_return_bp_the_cpp_side_of_part_3_is_the_tickets_example() -> None:
    rc381 = form_bp()

    for kind, expected in (
        (RC381_PART_3_LINE_11, "30000.00"),
        (RC381_PART_3_LINE_16, "30000.00"),
        (RC381_PART_3_LINE_18, "28500.00"),
        (RC381_PART_3_LINE_20, "1485.00"),
        (RC381_PART_3_LINE_21, "300.00"),
        (RC381_PART_3_LINE_22, "1410.75"),
        (RC381_PART_3_LINE_23, "285.00"),
    ):
        assert rc381.get(kind).value == D(expected), kind.identifier


def test_return_bp_the_qpp_side_of_part_3_is_the_tickets_example() -> None:
    rc381 = form_bp()

    for kind, expected in (
        (RC381_PART_3_LINE_27, "46400.12"),
        (RC381_PART_3_LINE_29, "2000.00"),
        (RC381_PART_3_LINE_31, "40000.00"),
        (RC381_PART_3_LINE_38, "38000.00"),
        (RC381_PART_3_LINE_40, "2109.38"),
        (RC381_PART_3_LINE_41, "390.62"),
        (RC381_PART_3_LINE_42, "2052.00"),
        (RC381_PART_3_LINE_43, "380.00"),
    ):
        assert rc381.get(kind).value == D(expected), kind.identifier


def test_return_bp_the_totals_of_part_3_are_the_tickets_example() -> None:
    rc381 = form_bp()

    for kind, expected in (
        (RC381_PART_3_LINE_52, "3462.75"),
        (RC381_PART_3_LINE_53, "131.63"),
        (RC381_PART_3_LINE_59, "665.00"),
        (RC381_PART_3_LINE_60, "25.62"),
        (RC381_PART_3_LINE_61, "157.25"),
        (RC381_PART_3_LINE_68, "0"),
        (RC381_PART_3_LINE_69, "157.25"),
    ):
        assert rc381.get(kind).value == D(expected), kind.identifier


def test_return_bp_line_69_is_positive_so_part_3a_gives_the_three_results() -> None:
    # Part 4 is not completed (no self-employment income and no election), so the final selection
    # returns to Part 3a: line 70 (3,462.75), line 73 (665.00) and line 74 (157.25).
    rc381 = form_bp()

    assert rc381.get(RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3462.75")
    assert rc381.get(RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("665.00")
    assert rc381.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value == D("157.25")


def test_return_bp_t1_line_30800_and_on428_line_58240_are_3462_75() -> None:
    # ON428 line 58240 "Amount from line 30800 of your return" reads the same T1 line.
    assert return_bp().get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("3462.75")


def test_return_bp_t1_line_22215_is_665_00() -> None:
    assert return_bp().get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("665.00")


def test_return_bp_t1_line_44800_is_157_25() -> None:
    assert return_bp().get(CPP_OVERPAYMENT).value == D("157.25")


def test_return_bp_lines_42100_31000_and_22200_are_zero() -> None:
    worksheet = return_bp()

    for kind in (
        CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ):
        assert worksheet.get(kind).value == D("0"), kind.identifier


def test_return_bp_the_enhanced_deduction_is_taken_from_total_income() -> None:
    worksheet = return_bp()

    assert worksheet.get(TOTAL_INCOME).value == D("70000.00")
    assert worksheet.get(NET_INCOME).value == D("69335.00")


def test_return_bp_the_overpayment_is_a_credit_and_the_tax_is_the_engines() -> None:
    worksheet = return_bp()

    assert worksheet.get(NET_FEDERAL_TAX).value == D("7560.85")
    assert worksheet.get(ONTARIO_TAX).value == D("3902.81")
    assert worksheet.get(TOTAL_PAYABLE).value == D("11463.66")
    # The income tax deducted (12000.00) plus the CPP overpayment of line 44800 (157.25).
    assert worksheet.get(TOTAL_CREDITS).value == D("12157.25")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-693.59")


def test_return_bp_with_schedule_8_instead_the_cpp_lines_come_from_the_box_26_total() -> None:
    # The same slips on a return that carries Schedule 8 and no Form RC381 (the other form of the
    # exclusive group): Schedule 8 line 1 is the box 26 total (30000), so the required
    # contributions are 1311.75 and 265.00 (on 26500 above the exemption) and the box 16 total
    # (1785.00) is 208.25 more: 1311.75 on line 30800, 265.00 on line 22215 and 208.25 on line
    # 44800.
    worksheet = return_bp(schedule_8_copies=1, rc381_copies=0)

    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("1311.75")
    assert worksheet.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("265.00")
    assert worksheet.get(CPP_OVERPAYMENT).value == D("208.25")
