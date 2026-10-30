"""CA-ON 2025 end to end: return DI, the disability supports deduction of Form T929.

Return DI is `returns/2025_return_di.yaml`: a student for 20 weeks with $12,000.00 paid and nothing
reimbursed, $2,000.00 of employment income and $18,000.00 of other income. The other tests here
vary that return: a non-student with earned income of 30,000, a claim the expenses limit, 52 weeks,
a statement of business income with a loss, and a return with no copy of the form.
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.errors import CapabilityContractError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    DEDUCTIONS_FROM_TOTAL_INCOME,
    DISABILITY_SUPPORTS_DEDUCTION,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    T929_LINE_3,
    T929_LINE_4,
    T929_LINE_7,
    T929_LINE_9,
    T929_LINE_10,
    T929_LINE_11,
    T929_NET_BUSINESS_INCOME,
    TAXABLE_INCOME,
    TOTAL_INCOME,
)
from tests.jurisdictions.ca_on.end_to_end.support import D, run


def run_di(employment: str = "2000", **overrides: Any) -> dict[str, tuple[Worksheet, ...]]:
    """Return DI's inputs, as in `returns/2025_return_di.yaml`, over the keyword overrides given.

    The seven required arguments of `starting` are passed as the other returns pass them: the
    employment income, no dispositions, and zeros for the RRSP, union dues and the rest.
    """
    inputs: dict[str, Any] = {
        "other_income": "18000",
        "t929_expenses_paid": "12000",
        "t929_expenses_reimbursed": "0",
        "t929_weeks_attended": 20,
        "t929_copies": 1,
        "resident_in_canada_throughout_2025": 1,
        "aged_18_or_older_at_end_of_2025": 1,
    }
    return run(employment, (), "0", "0", "0", "0", "0", **{**inputs, **overrides})


def test_the_student_of_return_di_keeps_net_income_at_20000_and_claims_9500() -> None:
    result = run_di()
    form = result["ca/t929"][0]
    return_worksheet = result["ca-on/return"][0]

    # Form T929 line 5 is the net income with no claim: 20000.00, not reduced by the claim.
    assert form.get(NET_INCOME).value == D("20000.00")
    assert form.get(T929_LINE_3).value == D("12000.00")
    assert form.get(T929_LINE_4).value == D("2000.00")
    assert form.get(T929_LINE_7).value == D("18000.00")
    assert form.get(T929_LINE_9).value == D("7500.00")
    assert form.get(T929_LINE_10).value == D("7500.00")
    assert form.get(T929_LINE_11).value == D("9500.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("9500.00")
    assert return_worksheet.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("9500.00")
    assert return_worksheet.get(DEDUCTIONS_FROM_TOTAL_INCOME).value == D("9500.00")
    assert return_worksheet.get(NET_INCOME_BEFORE_ADJUSTMENTS).value == D("10500.00")
    assert return_worksheet.get(NET_INCOME).value == D("10500.00")
    assert return_worksheet.get(TAXABLE_INCOME).value == D("10500.00")


def test_a_non_student_with_earned_income_of_30000_claims_the_4000_net_expenses() -> None:
    result = run_di(
        employment="30000",
        other_income="0",
        t929_expenses_paid="5000",
        t929_expenses_reimbursed="1000",
        t929_weeks_attended=0,
    )
    form = result["ca/t929"][0]

    assert form.get(T929_LINE_3).value == D("4000.00")
    # No weeks attended: line 7 is not above 0 (net income is below the earned income), so line 10
    # is 0.00 and line 11 is the earned income alone.
    assert form.get(T929_LINE_7).value == D("0")
    assert form.get(T929_LINE_10).value == D("0.00")
    assert form.get(T929_LINE_11).value == D("30000.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("4000.00")
    assert result["ca-on/return"][0].get(DISABILITY_SUPPORTS_DEDUCTION).value == D("4000.00")


def test_52_weeks_caps_line_10_at_the_15000_maximum() -> None:
    result = run_di(t929_weeks_attended=52, t929_expenses_paid="20000")
    form = result["ca/t929"][0]

    # Line 7 is 18000.00 and line 9 is 52 x $375 = 19500.00, so line 10 is the $15,000 maximum.
    assert form.get(T929_LINE_7).value == D("18000.00")
    assert form.get(T929_LINE_9).value == D("19500.00")
    assert form.get(T929_LINE_10).value == D("15000.00")
    assert form.get(T929_LINE_11).value == D("17000.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("17000.00")


def test_the_claim_is_the_expenses_when_they_are_less_than_line_11() -> None:
    result = run_di(t929_expenses_paid="5000")
    form = result["ca/t929"][0]
    return_worksheet = result["ca-on/return"][0]

    # Line 3 is 5000.00, below line 11 of 9500.00, so line 12 and line 21500 are 5000.00.
    assert form.get(T929_LINE_3).value == D("5000.00")
    assert form.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("5000.00")
    assert return_worksheet.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("5000.00")
    assert return_worksheet.get(NET_INCOME).value == D("15000.00")


def test_a_business_statement_of_4000_and_a_loss_of_1500_counts_4000_in_line_4() -> None:
    result = run_di(
        employment="0",
        other_income="0",
        t929_expenses_paid="0",
        t929_weeks_attended=0,
        business_statements=(
            {"business": {"gross_sales": "4000"}},
            {"business": {"advertising": "1500"}},
        ),
    )
    form = result["ca/t929"][0]

    # A loss counts 0 in line 4: the net self-employment income is the positive statement alone.
    assert form.get(T929_NET_BUSINESS_INCOME).value == D("4000.00")
    assert form.get(T929_LINE_4).value == D("4000.00")


def test_with_no_copy_of_the_form_line_21500_is_zero_and_nothing_else_changes() -> None:
    without = run_di(t929_copies=0)
    with_copy = run_di(t929_expenses_paid="0")

    assert without["ca/t929"] == ()
    assert len(with_copy["ca/t929"]) == 1
    without_return = without["ca-on/return"][0]
    with_return = with_copy["ca-on/return"][0]
    assert without_return.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("0")
    assert with_return.get(DISABILITY_SUPPORTS_DEDUCTION).value == D("0")
    for kind in (
        TOTAL_INCOME,
        DEDUCTIONS_FROM_TOTAL_INCOME,
        NET_INCOME_BEFORE_ADJUSTMENTS,
        NET_INCOME,
        TAXABLE_INCOME,
    ):
        assert without_return.get(kind) == with_return.get(kind), kind.identifier
    assert without_return.get(NET_INCOME).value == D("20000.00")


def test_reimbursement_above_the_expenses_refuses_the_return() -> None:
    # Line 3 is the expenses less the reimbursement, 1000.00 - 3000.00 = -2000.00. Line 3 is not
    # floored as printed, so line 12 (the lesser of line 3 and line 11) is -2000.00, and the
    # disability supports deduction cannot be negative: the copy's capability breaks its contract
    # and the return is refused, naming the copy and the deduction.
    with pytest.raises(
        CapabilityContractError,
        match=(
            r"ca/t929, instance 1: LesserOf produced ca/disability_supports_deduction -2000, "
            r"which cannot be negative"
        ),
    ):
        run_di(t929_expenses_paid="1000", t929_expenses_reimbursed="3000")
