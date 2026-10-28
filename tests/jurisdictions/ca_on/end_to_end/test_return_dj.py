"""CA-ON 2025 end to end: return dj, Form RC359 copies for four employers on one return."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.errors import NoAmountForCountError
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    NET_FEDERAL_TAX,
    RC359_EMPLOYMENT_INCOME,
    RC359_EPSP_CONTRIBUTIONS,
    RC359_EXCESS_EPSP_AMOUNT,
    RC359_LINE_4,
    RC359_LINE_6,
    RC359_LINE_8,
    RC359_OTHER_EMPLOYMENT_INCOME,
    RC359_PROVINCE,
    RC359_TAX_ON_EXCESS_EPSP,
    RC359_TAX_TOTAL,
    REFUND_OR_BALANCE_OWING,
    SPECIAL_TAXES,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# One employer's copy of Form RC359 as (line 1 contributions, line 2 employment income, line 3
# other employment income, the province code of line 8): a chosen figure for each.
Copy = tuple[str, str, str, int]
EMPLOYER_A: Copy = ("10000", "20000", "0", 6)  # Ontario
EMPLOYER_B: Copy = ("1000", "20000", "0", 6)  # Ontario, contributions below the 20% line
MANITOBA_COPY: Copy = ("10000", "20000", "0", 7)  # employer A's figures, Manitoba
OTHER_COPY: Copy = ("10000", "20000", "0", 14)  # employer A's figures, Other (non-resident)


def employer(contributions: str, income: str, other: str, province: int) -> dict[Any, Any]:
    """One record of `ca/rc359_employers`: the form's four inputs for one copy."""
    return {
        RC359_EPSP_CONTRIBUTIONS: D(contributions),
        RC359_EMPLOYMENT_INCOME: D(income),
        RC359_OTHER_EMPLOYMENT_INCOME: D(other),
        RC359_PROVINCE: province,
    }


def run_dj(*copies: Copy) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of return DJ with one Form RC359 copy for each of `copies`.

    The filer has no other income: the RC359 copies are the only inputs of the return's special
    taxes (none given: no copy, and the return has no RC359 amount).
    """
    artifacts = starting(
        "0", (), "0", "0", "0", "0", "0", rc359_employers=tuple(employer(*each) for each in copies)
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_dj(*copies: Copy) -> Worksheet:
    """The return's worksheet of return DJ with the RC359 copies given."""
    return run_dj(*copies)["ca-on/return"][0]


def rc359_copies(*copies: Copy) -> tuple[Worksheet, ...]:
    """The worksheets of the Form RC359 copies, one for each copy given, in order."""
    return run_dj(*copies)["ca/rc359"]


def test_employer_a_copy_gives_line_4_6_7_and_9_of_20000_4000_6000_and_3211_80() -> None:
    # Line 4 is 20,000 less nothing; line 6 is 20% of it, 4,000; line 7 is 10,000 less 4,000,
    # 6,000; line 8 is Ontario's 53.53%; line 9 is 6,000 x 53.53% = 3,211.80.
    (copy,) = rc359_copies(EMPLOYER_A)

    assert copy.get(RC359_LINE_4).value == D("20000.00")
    assert copy.get(RC359_LINE_6).value == D("4000.00")
    assert copy.get(RC359_EXCESS_EPSP_AMOUNT).value == D("6000.00")
    assert copy.get(RC359_LINE_8).value == D("53.53")
    assert copy.get(RC359_TAX_ON_EXCESS_EPSP).value == D("3211.80")


def test_employer_b_copy_floors_line_7_at_zero_so_line_9_is_zero() -> None:
    # Line 7 is 1,000 less 4,000 = -3,000, which the form floors at "0".
    copy = rc359_copies(EMPLOYER_A, EMPLOYER_B)[1]

    assert copy.get(RC359_LINE_6).value == D("4000.00")
    assert copy.get(RC359_EXCESS_EPSP_AMOUNT).value == D("0.00")
    assert copy.get(RC359_TAX_ON_EXCESS_EPSP).value == D("0.00")


def test_a_manitoba_copy_gives_50_4_percent_of_the_excess_3024() -> None:
    # 6,000 x 50.4% = 3,024.00, the same excess as employer A's copy.
    (copy,) = rc359_copies(MANITOBA_COPY)

    assert copy.get(RC359_LINE_8).value == D("50.40")
    assert copy.get(RC359_EXCESS_EPSP_AMOUNT).value == D("6000.00")
    assert copy.get(RC359_TAX_ON_EXCESS_EPSP).value == D("3024.00")


def test_an_other_non_resident_copy_gives_49_percent_of_the_excess_2940() -> None:
    # 6,000 x 49% = 2,940.00: the chart's "Other (non-resident)" row is code 14.
    (copy,) = rc359_copies(OTHER_COPY)

    assert copy.get(RC359_LINE_8).value == D("49.00")
    assert copy.get(RC359_TAX_ON_EXCESS_EPSP).value == D("2940.00")


def test_line_41800_is_the_sum_of_the_copies_line_9_3211_80_0_3024_and_2940() -> None:
    worksheet = return_dj(EMPLOYER_A, EMPLOYER_B, MANITOBA_COPY, OTHER_COPY)

    assert worksheet.get(RC359_TAX_TOTAL).value == D("9175.80")
    assert worksheet.get(SPECIAL_TAXES).value == D("9175.80")


def test_line_41800_with_two_employers_is_the_sum_of_their_line_9_amounts() -> None:
    worksheet = return_dj(EMPLOYER_A, EMPLOYER_B)

    assert worksheet.get(SPECIAL_TAXES).value == D("3211.80")


def test_the_special_tax_is_carried_into_net_federal_tax_and_the_balance_owing() -> None:
    # No other tax, payment or refundable credit on the return: the net federal tax is line 41800,
    # and the refund or balance owing (line 167) is the balance owing of that amount.
    worksheet = return_dj(EMPLOYER_A, EMPLOYER_B, MANITOBA_COPY, OTHER_COPY)

    assert worksheet.get(NET_FEDERAL_TAX).value == D("9175.80")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("9175.80")


def test_a_return_without_employers_leaves_line_41800_unchanged_at_zero() -> None:
    # The return with no RC359 copy has the special taxes it had before: none, as its T1172 and
    # RL-10 amounts are 0.
    worksheet = return_dj()

    assert worksheet.get(RC359_TAX_TOTAL).value == D("0")
    assert worksheet.get(SPECIAL_TAXES).value == D("0")


def test_a_province_code_the_chart_does_not_list_is_refused() -> None:
    # Code 0 (no province) has no row in the chart, so the copy is refused rather than guessed.
    with pytest.raises(NoAmountForCountError):
        run_dj(("10000", "20000", "0", 0))
