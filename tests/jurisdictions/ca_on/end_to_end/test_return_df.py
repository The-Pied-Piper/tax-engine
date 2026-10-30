"""CA-ON 2025 end to end: return df."""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import ValidationError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    HOME_RENOVATION_CLAIMED_BY_OTHERS,
    HOME_RENOVATION_EXPENDITURES,
    HOME_RENOVATION_LINE_3,
    HOME_RENOVATION_LINE_6,
    HOME_RENOVATION_LINE_8,
    HOME_RENOVATION_REIMBURSED,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
    TOTAL_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# (expenditures, reimbursed, claimed by other eligible individuals), as lines 1, 2 and 5.
ONE = ("60000", "0", "0")
TWO = ("30000", "5000", "10000")


def return_df(*renovations: tuple[str, str, str]) -> Worksheet:
    """Return DF's worksheet with the renovation records given, in order (none by default).

    The filer has no income and no other entries, so the renovation records are the only inputs
    of Schedule 12 that the return has.
    """
    rows: list[dict[Any, Any]] = [
        {
            HOME_RENOVATION_EXPENDITURES: D(expenditures),
            HOME_RENOVATION_REIMBURSED: D(reimbursed),
            HOME_RENOVATION_CLAIMED_BY_OTHERS: D(claimed),
        }
        for expenditures, reimbursed, claimed in renovations
    ]
    artifacts = starting("0", (), "0", "0", "0", "0", "0", home_renovations=tuple(rows))
    return service().compute(CA_ON, 2025, *artifacts)["ca-on/return"][0]


def test_two_renovations_give_lines_3_6_and_8_and_the_credit_of_10875() -> None:
    # Renovation 1: line 3 is 60,000 capped at 50,000, line 6 is 50,000 less nothing, line 7 is
    # 50,000. Renovation 2: line 3 is 30,000 less 5,000 (25,000), line 6 is 50,000 less 10,000
    # (40,000), line 7 is 25,000. Totals: line 3 75,000, line 6 90,000, line 8 75,000, and line 10
    # 75,000 x 14.5% = 10,875.00.
    worksheet = return_df(ONE, TWO)

    assert worksheet.get(HOME_RENOVATION_LINE_3).value == D("75000.00")
    assert worksheet.get(HOME_RENOVATION_LINE_6).value == D("90000.00")
    assert worksheet.get(HOME_RENOVATION_LINE_8).value == D("75000.00")
    assert worksheet.get(MULTIGENERATIONAL_HOME_RENOVATION_CREDIT).value == D("10875.00")


def test_the_credit_is_added_to_total_credits_by_10875_over_the_same_return_without_it() -> None:
    with_renovations = return_df(ONE, TWO).get(TOTAL_CREDITS).value
    without_renovations = return_df().get(TOTAL_CREDITS).value

    assert with_renovations - without_renovations == D("10875.00")


def test_one_renovation_at_the_maximum_gives_7250() -> None:
    worksheet = return_df(ONE)

    assert worksheet.get(HOME_RENOVATION_LINE_8).value == D("50000.00")
    assert worksheet.get(MULTIGENERATIONAL_HOME_RENOVATION_CREDIT).value == D("7250.00")


def test_one_renovation_reimbursed_and_claimed_by_others_gives_3625() -> None:
    worksheet = return_df(TWO)

    assert worksheet.get(HOME_RENOVATION_LINE_8).value == D("25000.00")
    assert worksheet.get(MULTIGENERATIONAL_HOME_RENOVATION_CREDIT).value == D("3625.00")


def test_no_renovations_give_no_credit() -> None:
    worksheet = return_df()

    assert worksheet.get(HOME_RENOVATION_LINE_3).value == D("0")
    assert worksheet.get(HOME_RENOVATION_LINE_6).value == D("0")
    assert worksheet.get(HOME_RENOVATION_LINE_8).value == D("0")
    assert worksheet.get(MULTIGENERATIONAL_HOME_RENOVATION_CREDIT).value == D("0")


def test_reimbursed_above_expenditures_is_refused_through_the_return() -> None:
    # Renovation 1: line 2 of 50,000.00 is above its line 1 of 40,000.00. Schedule 12 line 2 is
    # "included in the amount on line 1", so the return is refused, naming the renovation.
    with pytest.raises(ValidationError, match=r"renovation 1.*line 2.*line 1"):
        return_df(("40000", "50000", "0"))


def test_claimed_by_others_above_the_maximum_is_refused_through_the_return() -> None:
    # Renovation 1: line 5 of 60,000.00 is above the 50,000.00 maximum of line 4, so the return is
    # refused, naming the renovation.
    with pytest.raises(ValidationError, match=r"renovation 1.*line 5.*line 4"):
        return_df(("40000", "0", "60000"))


def test_reimbursed_equal_to_expenditures_and_claimed_equal_to_the_maximum_give_no_credit() -> None:
    # Each value at its bound is accepted: line 3 is 40,000 less 40,000 (0), and line 6 is 50,000
    # less 50,000 (0), so line 7 is 0 for both renovations.
    worksheet = return_df(("40000", "40000", "0"), ("40000", "0", "50000"))

    assert worksheet.get(HOME_RENOVATION_LINE_8).value == D("0")
    assert worksheet.get(MULTIGENERATIONAL_HOME_RENOVATION_CREDIT).value == D("0")
