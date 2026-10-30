"""CA-ON 2025 end to end: return dm, T1 line 31400 when the filer elects to split pension income.

The Federal Worksheet for line 31400 ends "However, if you are electing to split your eligible
pension with your spouse or common-law partner, complete Form T1032 ... to calculate the amount to
enter on line 31400 of your return instead." The return takes the form's amount when line 22 of
the form (the amount elected, on line 21000 of the transferring spouse's return) is above 0.
"""

from __future__ import annotations

import pytest

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    PENSION_INCOME_CREDIT,
    PENSION_WORKSHEET_AMOUNT,
    T1032_ELECTION_APPLIES,
    T1032_LINE_31,
    T1032_LINE_31400_TRANSFERRING,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def computed(*, pension: str = "20000", elected: str = "2000") -> dict[str, tuple[Worksheet, ...]]:
    """Return DG's filer (100,000 of employment income and a pension on line 11500), who is the
    transferring spouse of a joint election: line 1 of Form T1032 is the pension (line 8 of the
    Federal Worksheet for line 31400) and `elected` is on line 21000."""
    artifacts = starting(
        "100000",
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        other_pensions_and_superannuation=pension,
        t1032_line_22=elected,
        t1032_eligible_pension_income=pension,
        t1032_filer_is_transferring_spouse=1,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def return_dm(*, pension: str = "20000", elected: str = "2000") -> Worksheet:
    """The return's worksheet of `computed`."""
    return computed(pension=pension, elected=elected)["ca-on/return"][0]


def form_dm(*, pension: str = "20000", elected: str = "2000") -> Worksheet:
    """The worksheet of Form T1032 of `computed`."""
    return computed(pension=pension, elected=elected)["ca/t1032"][0]


def test_no_amount_elected_leaves_line_31400_as_the_worksheet_gives_it() -> None:
    # Federal Worksheet for line 31400: the lesser of line 8 (20,000.00) and $2,000. Line 22 of the
    # form is 0, so the form is not filed and the worksheet amount stands.
    worksheet = return_dm(elected="0")

    assert worksheet.get(T1032_ELECTION_APPLIES).value == 0
    assert worksheet.get(PENSION_WORKSHEET_AMOUNT).value == D("2000.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_an_amount_elected_enters_the_form_t1032_amount_on_line_31400() -> None:
    # Pension 20,000.00, elected 2,000.00: line 31 = 20,000.00 - 2,000.00 = 18,000.00 (line 29 is
    # 0, no RCA), so line 31400 is the lesser of $2,000 and 18,000.00, 2,000.00.
    worksheet = return_dm(elected="2000")

    assert worksheet.get(T1032_ELECTION_APPLIES).value == 1
    assert form_dm(elected="2000").get(T1032_LINE_31).value == D("18000.00")
    assert form_dm(elected="2000").get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_the_form_t1032_amount_below_2000_is_line_31400_whatever_the_worksheet_gives() -> None:
    # Pension 3,000.00 (the worksheet gives 2,000.00), elected 1,500.00, the most line 21 allows
    # (50% of 3,000.00): line 31 = 3,000.00 - 1,500.00 = 1,500.00, so line 31400 is 1,500.00.
    worksheet = return_dm(pension="3000", elected="1500")

    assert worksheet.get(PENSION_WORKSHEET_AMOUNT).value == D("2000.00")
    assert form_dm(pension="3000", elected="1500").get(T1032_LINE_31).value == D("1500.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("1500.00")


def test_a_pension_all_elected_up_to_line_21_gives_the_form_amount_of_line_31() -> None:
    # Pension 2,400.00, elected 1,200.00 (line 21): line 31 = 1,200.00.
    worksheet = return_dm(pension="2400", elected="1200")

    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("1200.00")


def test_an_amount_elected_of_one_cent_above_line_21_is_refused_not_capped() -> None:
    # Line 21 is 50% of 3,000.00, 1,500.00: "The split-pension amount cannot be more than the
    # amount from line 21."
    with pytest.raises(InputAboveBoundError):
        return_dm(pension="3000", elected="1500.01")


def test_the_ontario_pension_credit_is_the_federal_amount_at_most_its_1762_maximum() -> None:
    # Ontario pension income amount (ON428 line 58360), the lesser of the federal amount and the
    # Ontario maximum of 1,762: min(2000, 1762) = 1762, and min(1500, 1762) = 1500.
    assert return_dm(elected="2000").get(ontario.PENSION_INCOME_CREDIT).value == D("1762.00")
    assert return_dm(pension="3000", elected="1500").get(ontario.PENSION_INCOME_CREDIT).value == D(
        "1500.00"
    )
