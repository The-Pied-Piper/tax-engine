"""CA-ON 2025 end to end: Form RC381 as a form of none or one copy."""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import ValidationError
from tax_engine.jurisdictions.ca.catalog import (
    CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    CPP_OVERPAYMENT,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    NET_INCOME,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run

LINES = (
    RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN,
    RC381_CPP_OVERPAYMENT_ON_RETURN,
    RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
)

# The T1 line each result of the form is entered on (`05j_cpp_lines.yaml` for lines 30800, 22215
# and 44800; the sums of lines 42100, 31000 and 22200 add the result to Part 4 and Part 5 of
# Schedule 8).
T1_LINES = (
    (CPP_BASE_CONTRIBUTIONS_ON_RETURN, RC381_CPP_BASE_CONTRIBUTIONS_ON_RETURN),
    (CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN, RC381_CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN),
    (CPP_OVERPAYMENT, RC381_CPP_OVERPAYMENT_ON_RETURN),
    (CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS, RC381_CPP_PAYABLE_ON_SELF_EMPLOYMENT),
    (
        CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        RC381_CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ),
    (
        CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
        RC381_CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
    ),
)


def test_a_return_with_no_rc381_gives_all_six_totals_0_and_no_form_worksheet() -> None:
    # Employment income of 60000 and a T4 box 16 total of 3361.75 would give a CPP overpayment on a
    # copy of Form RC381 (line 44800); with an empty list of copies the form does not run and each
    # total of its results is 0. The default is no copy of the form.
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3361.75",
    )

    assert result["ca/rc381"] == ()
    (worksheet,) = result["ca-on/return"]
    for kind in LINES:
        assert worksheet.get(kind).value == D("0"), kind.identifier
    assert worksheet.get(TOTAL_INCOME).value == D("60000")


def test_a_return_with_neither_form_has_no_cpp_on_the_t1_lines() -> None:
    result = run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=0, rc381_copies=0)

    assert result["ca/schedule_8"] == ()
    assert result["ca/rc381"] == ()
    (worksheet,) = result["ca-on/return"]
    for line, _ in T1_LINES:
        assert worksheet.get(line).value == D("0"), line.identifier
    assert worksheet.get(NET_INCOME).value == D("60000.00")


def test_a_return_with_one_rc381_totals_the_results_of_that_copy() -> None:
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3361.75",
        schedule_8_copies=0,
        rc381_copies=1,
    )

    (rc381,) = result["ca/rc381"]
    (worksheet,) = result["ca-on/return"]
    # The pensionable earnings are the employment income of 60000 (T4 box 26), so the box 16 total
    # of 3361.75 is the contribution required on them: line 30800 is 2796.75, with no overpayment.
    assert rc381.get(RC381_CPP_OVERPAYMENT_ON_RETURN).value == D("0")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    for kind in LINES:
        assert worksheet.get(kind).value == rc381.get(kind).value, kind.identifier


def test_the_t1_lines_of_a_return_with_one_rc381_are_the_results_of_that_copy() -> None:
    # Employment income of 60000 and a T4 box 16 total of 3361.75 on pensionable earnings (box 26)
    # of 60000: the box 16 total is the contribution required, so Part 3a gives no overpayment
    # (line 74), and line 44800 is 0.
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        cpp_t4_base_and_first_additional_contributions="3361.75",
        schedule_8_copies=0,
        rc381_copies=1,
    )

    (rc381,) = result["ca/rc381"]
    (worksheet,) = result["ca-on/return"]
    assert worksheet.get(CPP_OVERPAYMENT).value == D("0")
    for line, result_kind in T1_LINES:
        assert worksheet.get(line).value == rc381.get(result_kind).value, line.identifier


def test_an_rc381_return_with_all_earnings_outside_quebec_has_schedule_8s_t1_lines() -> None:
    # With all of the pensionable earnings outside Quebec and employment income only, Form RC381
    # gives what Schedule 8 gives on the same income: line 30800 2796.75 and line 22215 565.00.
    rc381 = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        t4_cpp_pensionable_earnings_outside_quebec="60000",
        schedule_8_copies=0,
        rc381_copies=1,
    )
    schedule_8 = run("60000", (), "0", "0", "0", "0", "0")

    (rc381_return,) = rc381["ca-on/return"]
    (schedule_8_return,) = schedule_8["ca-on/return"]
    assert rc381_return.get(CPP_BASE_CONTRIBUTIONS_ON_RETURN).value == D("2796.75")
    assert rc381_return.get(CPP_ENHANCED_CONTRIBUTIONS_ON_RETURN).value == D("565.00")
    assert rc381_return.get(NET_INCOME).value == D("59435.00")
    assert schedule_8["ca/rc381"] == ()
    for line, _ in T1_LINES:
        assert rc381_return.get(line).value == schedule_8_return.get(line).value, line.identifier


def test_the_self_employment_t1_lines_of_a_return_with_one_rc381_are_its_part_4() -> None:
    # The same self-employment income as Return BN's case (20000) with all the pensionable earnings
    # outside Quebec: Part 4 gives line 42100 1764.20, line 31000 559.35 and line 22200 1343.10.
    result = run(
        "60000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=({"business": {"gross_sales": "20000"}, "business_income_line": 2},),
        cpp_t4_base_and_first_additional_contributions="3500.00",
        t4_cpp_pensionable_earnings_outside_quebec="60000",
        schedule_8_copies=0,
        rc381_copies=1,
    )

    (rc381,) = result["ca/rc381"]
    (worksheet,) = result["ca-on/return"]
    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1764.20")
    assert worksheet.get(CPP_BASE_CONTRIBUTIONS_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D(
        "559.35"
    )
    assert worksheet.get(CPP_DEDUCTION_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1343.10")
    for line, result_kind in T1_LINES:
        assert worksheet.get(line).value == rc381.get(result_kind).value, line.identifier


def test_a_second_rc381_is_refused_naming_the_form() -> None:
    with pytest.raises(ValidationError, match="ca/rc381"):
        run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=0, rc381_copies=2)


def test_schedule_8_and_form_rc381_together_are_refused_by_the_exclusive_group() -> None:
    with pytest.raises(ValidationError, match="ca/cpp_calculation"):
        run("60000", (), "0", "0", "0", "0", "0", schedule_8_copies=1, rc381_copies=1)
