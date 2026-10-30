"""CA-ON 2025 end to end: return IZ, Schedule 8 Part 4 and Part 5 completed.

Schedule 8 (5000-S8, 2025), "Parts you have to complete": Part 4 "Complete this part if you are
reporting only self-employment income or other earnings you are electing to pay CPP contributions
on.", and Part 5 "Complete this part if you are reporting both:" employment income (complete Part 3
first) and self-employment income or other earnings. The two are alternatives: Part 4 alone and
Part 5 alone compute, and both completed is refused as an input error naming both, not added twice.
The case is the Part 4 and Part 5 cases of `test_return_bn.py` (no employment income, line 27 of
20,000, so Part 4 gives 1,963.50 on line 42100).
"""

from __future__ import annotations

import re

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputOutOfRangeError
from tax_engine.jurisdictions.ca.catalog import (
    CPP_PART_4_AND_PART_5_BOTH_CHECKED,
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
    "ca/cpp_part_4_and_part_5_both 1 is refused: Part 4 and Part 5 of Schedule 8 are both "
    "completed, but Part 4 is for self-employment income only and Part 5 for employment income "
    "as well"
)


def return_iz(**completed: int) -> ReturnAndSchedule8:
    """Schedule 8 with no employment income and line 27 of 20,000, with the Part 4 and Part 5
    completed counts given."""
    return compute_with_schedule_8(
        "0",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        business_statements=(routed_statement("20000", 2),),
        **completed,
    )


def test_part_4_alone_gives_the_self_employment_contributions_of_1963_50() -> None:
    worksheet = return_iz(cpp_part_4_completed=1)

    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1963.50")
    assert worksheet.get(CPP_PART_4_AND_PART_5_BOTH_CHECKED).value == 0


def test_part_5_alone_gives_the_same_1963_50() -> None:
    worksheet = return_iz(cpp_part_5_completed=1)

    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1963.50")
    assert worksheet.get(CPP_PART_4_AND_PART_5_BOTH_CHECKED).value == 0


def test_part_4_and_part_5_both_completed_is_refused_not_added_twice() -> None:
    # Both at 1 would add Part 4's lines 14, 15 and 17 to Part 5's lines 49, 70 and 88, counting the
    # same self-employment contributions twice. The two parts are alternatives, so the return is
    # refused as an input error naming both parts.
    with pytest.raises(InputOutOfRangeError, match=re.escape(REFUSED_MESSAGE)):
        return_iz(cpp_part_4_completed=1, cpp_part_5_completed=1)


def test_both_parts_with_form_rc381_are_refused_by_the_rc381_guard_first() -> None:
    # The RC381 guard (`ca/count_without_records`) checks Parts 4 and 5 before this check reads
    # them, so a return with a copy of Form RC381 is refused for Part 4 (its own input error), and
    # the Part 4 and Part 5 check is not reached.
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
            cpp_part_4_completed=1,
            cpp_part_5_completed=1,
        )

    assert "ca/cpp_part_4_completed" in str(raised.value)
    assert "ca/cpp_part_4_and_part_5_both" not in str(raised.value)
