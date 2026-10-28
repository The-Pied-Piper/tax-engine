"""CA-ON 2025 end to end: return JB, Schedule 8 Part 4 and Part 5 completed as yes or no answers.

Part 4 and Part 5 of Schedule 8 are each a yes or no answer, a count of 1 for yes and 0 for no. A
count of 2 is not two copies of the Part's lines: it is refused as an input error naming the flag,
as the other yes or no flags are (`ca/yes_or_no_count`), before the Part's lines are counted. The
case is the one of `test_return_iz.py` (no employment income, line 27 of 20,000, so Part 4 gives
1,963.50 on line 42100 when it is completed once).
"""

from __future__ import annotations

import re

import pytest

from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.jurisdictions.ca.catalog import (
    CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    ReturnAndSchedule8,
    compute_with_schedule_8,
    routed_statement,
)


def return_jb(**completed: int) -> ReturnAndSchedule8:
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


def test_part_4_completed_of_2_alone_is_refused_as_a_yes_or_no_answer() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape("ca/cpp_part_4_completed 2 is above a yes or no answer of 1"),
    ):
        return_jb(cpp_part_4_completed=2)


def test_part_5_completed_of_2_alone_is_refused_as_a_yes_or_no_answer() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=re.escape("ca/cpp_part_5_completed 2 is above a yes or no answer of 1"),
    ):
        return_jb(cpp_part_5_completed=2)


def test_part_4_completed_of_1_alone_still_gives_1963_50() -> None:
    worksheet = return_jb(cpp_part_4_completed=1)

    assert worksheet.get(CPP_PAYABLE_ON_SELF_EMPLOYMENT_AND_OTHER_EARNINGS).value == D("1963.50")
