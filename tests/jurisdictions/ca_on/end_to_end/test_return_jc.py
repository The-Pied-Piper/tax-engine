"""CA-ON 2025 end to end: return JC, Schedule 8 Part 4 completed with employment earnings.

Schedule 8 (5000-S8, 2025), "Part 4 - Contributions on self-employment income and other earnings
only (no employment income)": Part 4 is for a filer with no employment income. Part 3 line 1, the
CPP pensionable earnings outside Quebec from T4 slips
(`ca/t4_cpp_pensionable_earnings_outside_quebec`), is the employment input that Part 5 and Part 3
use. Part 4 completed with that input above 0 is refused as an input error naming Part 4 and the
Part 5 route, not added. Part 5 alone with no employment earnings is not refused: the form says only
"(complete Part 3 first)", and a T4 with zero box 14 is legitimate. The case of
`test_return_iz.py` (no employment income, line 27 of 20,000, so Part 4 gives 1,963.50 on line
42100).
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_calculator.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    ReturnAndSchedule8,
    compute_form,
    compute_with_schedule_8,
    routed_statement,
)

REFUSED_MESSAGE = (
    "ca/cpp_part_4_with_employment_earnings 1 is refused: Part 4 is completed, but Part 4 is for "
    "self-employment income and other earnings only (no employment income); use Part 5 when you "
    "also have employment income"
)


def return_jc(employment: str = "0", **arguments: Any) -> ReturnAndSchedule8:
    """Schedule 8 with line 27 of 20,000 and employment income `employment` (0 unless given), with
    the arguments of `starting(...)` given, such as the Part 4 and Part 5 completed counts."""
    return compute_with_schedule_8(
        employment,
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        **arguments,
    )


def test_part_4_alone_with_no_employment_earnings_gives_1963_50() -> None:
    worksheet = return_jc(cpp_part_4_completed=1)

    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1963.50")
    assert worksheet.get(CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED).value == 0


def test_part_5_alone_with_zero_t4_earnings_passes_through_unchanged() -> None:
    # Part 5 is not refused by this check: with no employment earnings the Part 5 completed count
    # stands, and the same 1,963.50 is given as for Part 4 alone (`test_return_iz.py`).
    worksheet = return_jc(cpp_part_5_completed=1)

    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1963.50")
    assert worksheet.get(CPP_PART_4_WITH_EMPLOYMENT_EARNINGS_CHECKED).value == 0


def test_part_4_with_employment_earnings_above_0_is_refused_not_added() -> None:
    # Part 4 completed with T4 pensionable earnings of 20,000 is an input error: Part 4 is for a
    # filer with no employment income, and the form's Part 5 is the route with employment income.
    with pytest.raises(InputOutOfRangeError, match=re.escape(REFUSED_MESSAGE)):
        return_jc(
            employment="20000",
            t4_cpp_pensionable_earnings_outside_quebec="20000",
            cpp_part_4_completed=1,
        )


def test_form_rc381_guard_speaks_first_for_part_4_with_employment_earnings() -> None:
    # The RC381 guard (`ca/count_without_records`) checks Part 4 before this check reads it, so a
    # return with a copy of Form RC381 is refused for Part 4 (its own input error), and the Part 4
    # with employment earnings check is not reached.
    with pytest.raises(InputAboveBoundError) as raised:
        compute_form(
            "ca-on/return",
            "60000",
            (),
            "0",
            "0",
            "0",
            "0",
            "0",
            t4_cpp_pensionable_earnings_outside_quebec="60000",
            cpp_part_4_completed=1,
        )

    assert "ca/cpp_part_4_completed" in str(raised.value)
    assert "ca/cpp_part_4_with_employment_earnings" not in str(raised.value)


def test_both_parts_with_employment_earnings_above_0_are_refused() -> None:
    # Part 4 and Part 5 completed together with T4 pensionable earnings of 20,000 break two rules
    # of the form (Part 4 is for no employment income, and the two parts are alternatives). Either
    # input error is correct; the two checks do not depend on each other, so which message is given
    # is not pinned, only that the return is refused.
    with pytest.raises(InputOutOfRangeError, match="is refused"):
        return_jc(
            employment="20000",
            t4_cpp_pensionable_earnings_outside_quebec="20000",
            cpp_part_4_completed=1,
            cpp_part_5_completed=1,
        )
