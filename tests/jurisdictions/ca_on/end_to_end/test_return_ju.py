"""CA-ON 2025 end to end: return JU, Form T1032 "Joint Election to Split Pension Income" as its own
form `ca/t1032`, run once, with the elected amount the return carries on line 21000 (the
transferring spouse's return) or line 11600 (the receiving spouse's), as the filer's answer names.

The worked return `returns/2025_return_ju.yaml` (a transferring spouse with $30,000 of pension and
a $10,000 election) is checked by `test_worked_returns.py`. This module computes each line of the
form on its own, from the starting figures of the return, and pins the refusals the printed form
does not give: the form prints no limit on the starting figures, so each limit is refused, not
capped, and an elected amount above line 21 (the maximum split-pension amount) is an input error.
For a transferring spouse's return, line 1 must be line 8 of the return's own Federal Worksheet for
line 31400, which the return checks (a line 1 above or below it is an input error).
"""

from __future__ import annotations

from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InvalidCompositionError,
    ValidationError,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    ELECTED_SPLIT_PENSION_AMOUNT,
    ELECTED_SPLIT_PENSION_DEDUCTION,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    NET_INCOME,
    PENSION_INCOME_CREDIT,
    PENSION_WORKSHEET_AMOUNT,
    REFUND_OR_BALANCE_OWING,
    T1032_ELECTION_APPLIES,
    T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_3,
    T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED,
    T1032_LINE_5,
    T1032_LINE_7,
    T1032_LINE_8,
    T1032_LINE_12,
    T1032_LINE_13,
    T1032_LINE_15,
    T1032_LINE_16,
    T1032_LINE_17,
    T1032_LINE_18,
    T1032_LINE_19,
    T1032_LINE_21,
    T1032_LINE_22,
    T1032_LINE_22_CHECKED,
    T1032_LINE_29,
    T1032_LINE_30,
    T1032_LINE_31,
    T1032_LINE_34,
    T1032_LINE_35_CHECKED,
    T1032_LINE_36,
    T1032_LINE_39,
    T1032_LINE_42,
    T1032_LINE_31400_RECEIVING,
    T1032_LINE_31400_TRANSFERRING,
    T1032_LINE_43700,
    T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED,
    TAXABLE_INCOME,
    TOTAL_CREDITS,
    TOTAL_INCOME,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    CA_ON,
    D,
    service,
    starting,
)

FORM = "ca/t1032"
RETURN = "ca-on/return"

# The starting figures of return JU: the transferring spouse's eligible pension (line 1), with
# its other pensions of 30,000 on line 11500, the tax deducted on the pension (line 35) and the
# return's own total income tax deducted (T1 line 43700 before the election, which is lines 37 and
# 40 of the form). The elected amount is on line 21000 of this return, which is the transferring
# spouse's, so line 1 is line 8 of its Federal Worksheet for line 31400 (30,000).
ELIGIBLE_PENSION = "30000"
LINE_22 = "10000"
TAX_ON_PENSION = "3000"
INCOME_TAX_DEDUCTED = "3000"


# The receiving spouse's return: the transferring spouse's line 1 is 30,000.00 and its tax on the
# pension (line 35) 3,000.00; this return has employment income of 20,000.00, tax deducted of
# 1,500.00 (line 40) and 1,500.00 elected on line 11600. Line 17 = 30,000.00, so line 21 is
# 15,000.00, line 36 = 3,000.00 x 1,500.00 / 30,000.00 = 150.00, line 42 = 1,500.00 + 150.00 =
# 1,650.00, line 30 = 1,500.00 and line 34 = 0.00 + 1,500.00.
RECEIVING: dict[str, Any] = {
    "filer_is_transferring_spouse": 0,
    "employment_income": "20000",
    "other_pensions": "0",
    "line_22": "1500",
    "tax_on_pension": "3000",
    "income_tax_deducted": "1500",
}


def run(
    *,
    eligible_pension: str = ELIGIBLE_PENSION,
    box_128: str = "0",
    rca_box_17: str = "0",
    rca_payments_qualify: int = 0,
    marital_status_changed: int = 0,
    months_married: str = "12",
    months_in_tax_year: str = "12",
    transferring_spouse_died: int = 0,
    not_separated_90_days: int = 1,
    residents_of_canada: int = 1,
    receiving_pension: str = "0",
    tax_on_pension: str = TAX_ON_PENSION,
    income_tax_deducted: str = INCOME_TAX_DEDUCTED,
    line_22: str = LINE_22,
    filer_is_transferring_spouse: int = 1,
    other_pensions: str | None = None,
    other_income: str | None = None,
    employment_income: str = "0",
) -> dict[str, tuple[Worksheet, ...]]:
    """Every form's worksheets of the return with the starting figures of Form T1032 given.

    The return's other inputs are `starting(...)` with the spouse answer given (1, a spouse on
    December 31, 2025) and, unless `other_pensions` is given, other pensions and superannuation
    equal to line 1, the pension being the eligible pension income (line 8 of the Federal Worksheet
    for line 31400). The filer is the transferring spouse unless the answer is given as 0.
    """
    artifacts = starting(
        employment_income,
        (),
        "0",
        "0",
        "0",
        "0",
        "0",
        # Box 17 of the T4A-RCA slips is on T1 line 13000, so the other income is at least box 17.
        other_income=rca_box_17 if other_income is None else other_income,
        other_pensions_and_superannuation=eligible_pension
        if other_pensions is None
        else other_pensions,
        t1032_line_22=line_22,
        spouse_or_common_law_partner_on_december_31=1,
        t1032_eligible_pension_income=eligible_pension,
        t1032_t4a_box_128=box_128,
        t1032_t4a_rca_box_17=rca_box_17,
        t1032_rca_payments_qualify=rca_payments_qualify,
        t1032_marital_status_changed=marital_status_changed,
        t1032_filer_is_transferring_spouse=filer_is_transferring_spouse,
        t1032_months_married=months_married,
        t1032_months_in_tax_year=months_in_tax_year,
        t1032_transferring_spouse_died=transferring_spouse_died,
        t1032_not_separated_90_days=not_separated_90_days,
        t1032_residents_of_canada=residents_of_canada,
        t1032_receiving_spouse_pension_amount=receiving_pension,
        t1032_income_tax_deducted_on_pension=tax_on_pension,
        income_tax_deducted=income_tax_deducted,
    )
    return service().compute(CA_ON, 2025, *artifacts)


def form(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[FORM]
    return worksheet


def return_worksheet(**overrides: Any) -> Worksheet:
    (worksheet,) = run(**overrides)[RETURN]
    return worksheet


# --- the return's lines ---------------------------------------------------------------------------


def test_the_return_has_total_income_of_30000_and_net_income_after_the_election() -> None:
    found = return_worksheet()

    assert found.get(TOTAL_INCOME).value == D("30000.00")
    assert found.get(NET_INCOME).value == D("20000.00")
    assert found.get(TAXABLE_INCOME).value == D("20000.00")


# --- Step 2: the maximum split-pension amount ----------------------------------------------------


def test_line_3_is_line_1_with_no_box_128_amount() -> None:
    assert form().get(T1032_LINE_3).value == D("30000.00")


def test_line_3_is_line_1_less_the_veterans_box_128_amount() -> None:
    assert form(box_128="2000").get(T1032_LINE_3).value == D("28000.00")


def test_a_box_128_amount_above_line_1_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(box_128="30000.01")


def test_lines_5_and_13_are_the_printed_ceiling_of_131483_45() -> None:
    found = form()

    assert found.get(T1032_LINE_5).value == D("131483.45")
    assert found.get(T1032_LINE_13).value == D("131483.45")


def test_line_7_is_the_ceiling_less_line_3() -> None:
    assert form().get(T1032_LINE_7).value == D("101483.45")


def test_line_8_is_0_without_a_qualifying_rca_payment_whatever_line_4_is() -> None:
    found = form(rca_box_17="5000")

    assert found.get(T1032_LINE_8).value == D("0.00")


def test_line_8_is_the_lesser_of_line_4_and_line_7_with_a_qualifying_rca_payment() -> None:
    found = form(rca_box_17="5000", rca_payments_qualify=1)

    assert found.get(T1032_LINE_8).value == D("5000.00")


def test_line_8_takes_line_7_when_line_4_is_above_it() -> None:
    found = form(rca_box_17="200000", rca_payments_qualify=1)

    assert found.get(T1032_LINE_8).value == D("101483.45")


def test_line_16_is_the_lesser_of_box_128_and_line_15() -> None:
    found = form(box_128="2000")

    assert found.get(T1032_LINE_12).value == D("28000.00")
    assert found.get(T1032_LINE_15).value == D("103483.45")
    assert found.get(T1032_LINE_16).value == D("2000.00")


def test_line_17_is_lines_3_8_and_16_added() -> None:
    found = form(box_128="2000", rca_box_17="5000", rca_payments_qualify=1)

    assert found.get(T1032_LINE_17).value == D("35000.00")


def test_line_17_of_0_gives_line_21_of_0() -> None:
    found = form(eligible_pension="0", tax_on_pension="0", line_22="0", income_tax_deducted="0")

    assert found.get(T1032_LINE_17).value == D("0.00")
    assert found.get(T1032_LINE_21).value == D("0.00")


def test_line_18_is_line_17_for_12_of_12_months_married() -> None:
    assert form().get(T1032_LINE_18).value == D("30000.00")


def test_a_marital_status_change_of_6_months_of_12_takes_half_of_line_17_on_line_19() -> None:
    found = form(marital_status_changed=1, months_married="6", line_22="5000")

    assert found.get(T1032_LINE_18).value == D("15000.00")
    assert found.get(T1032_LINE_19).value == D("15000.00")
    assert found.get(T1032_LINE_21).value == D("7500.00")


def test_no_marital_status_change_takes_line_17_on_line_19_whatever_line_18_is() -> None:
    found = form(months_married="6")

    assert found.get(T1032_LINE_18).value == D("15000.00")
    assert found.get(T1032_LINE_19).value == D("30000.00")


def test_an_unchanged_marital_status_divides_line_18_by_the_printed_12_whatever_is_typed() -> None:
    found = form(months_married="0", months_in_tax_year="0")

    assert found.get(T1032_LINE_18).value == D("0.00")
    assert form(months_married="6").get(T1032_LINE_18).value == D("15000.00")


def test_a_deceased_transferring_spouse_divides_line_18_by_the_months_to_death() -> None:
    found = form(
        marital_status_changed=1,
        transferring_spouse_died=1,
        months_married="3",
        months_in_tax_year="6",
        line_22="5000",
    )

    assert found.get(T1032_LINE_18).value == D("15000.00")


def test_a_living_transferring_spouse_divides_line_18_by_the_printed_12_whatever_is_typed() -> None:
    # Married in July: 7 months married, and the form still divides by 12 (Note 1 is for a death).
    found = form(
        marital_status_changed=1,
        months_married="7",
        months_in_tax_year="7",
        line_22="5000",
    )

    assert found.get(T1032_LINE_18).value == D("17500.00")
    assert found.get(T1032_LINE_19).value == D("17500.00")


def test_a_deceased_transferring_spouse_with_0_months_in_the_tax_year_is_refused() -> None:
    with pytest.raises(ValidationError):
        run(
            marital_status_changed=1,
            transferring_spouse_died=1,
            months_married="0",
            months_in_tax_year="0",
        )


def test_months_married_above_the_months_in_the_tax_year_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(months_married="13")


def test_months_married_is_checked_against_the_printed_12_when_the_status_did_not_change() -> None:
    # Line 18 does not apply, so the typed months in the tax year are not the denominator.
    assert form(months_married="12", months_in_tax_year="5").get(T1032_LINE_19).value == D(
        "30000.00"
    )
    with pytest.raises(InputAboveBoundError):
        run(months_married="13", months_in_tax_year="13")


def test_months_in_the_tax_year_of_13_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(
            marital_status_changed=1,
            transferring_spouse_died=1,
            months_married="6",
            months_in_tax_year="13",
        )


def test_a_transferring_spouse_died_count_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(transferring_spouse_died=2)


def test_a_marital_status_count_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(marital_status_changed=2)


def test_an_elected_amount_is_refused_when_the_spouses_lived_separate_and_apart_90_days() -> None:
    with pytest.raises(InputAboveBoundError):
        run(not_separated_90_days=0, line_22="1000")


def test_an_elected_amount_is_refused_when_a_spouse_was_not_a_resident_of_canada() -> None:
    with pytest.raises(InputAboveBoundError):
        run(residents_of_canada=0, line_22="1000")


def test_no_election_is_fine_when_a_condition_of_page_1_is_not_met() -> None:
    found = form(not_separated_90_days=0, residents_of_canada=0, line_22="0")

    assert found.get(T1032_LINE_21).value == D("15000.00")


def test_a_condition_count_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(not_separated_90_days=2)
    with pytest.raises(InputAboveBoundError):
        run(residents_of_canada=2)


def test_line_21_is_half_of_line_19_at_the_maximum_split_rate() -> None:
    assert form().get(T1032_LINE_21).value == D("15000.00")


# --- Step 3: the elected amount, line 22 ---------------------------------------------------------


def test_line_22_is_the_elected_amount_of_line_21000_when_it_is_within_line_21() -> None:
    assert form().get(T1032_LINE_22_CHECKED).value == D("10000.00")


def test_an_elected_amount_one_cent_above_line_21_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(line_22="15000.01")


def test_an_elected_amount_on_line_11600_above_line_21_is_refused_not_capped() -> None:
    with pytest.raises(InputAboveBoundError):
        run(filer_is_transferring_spouse=0, line_22="15000.01")


def test_an_elected_amount_at_line_21_is_accepted_as_it_is() -> None:
    found = form(line_22="15000")

    assert found.get(T1032_LINE_22_CHECKED).value == D("15000.00")


def test_a_transferring_spouse_s_line_22_is_carried_on_line_21000_and_not_on_line_11600() -> None:
    found = form(line_22="5000")
    carried = return_worksheet(line_22="10000")

    assert found.get(T1032_LINE_22).value == D("5000.00")
    assert carried.get(ELECTED_SPLIT_PENSION_DEDUCTION).value == D("10000.00")
    assert carried.get(ELECTED_SPLIT_PENSION_AMOUNT).value == D("0.00")


def test_a_receiving_spouse_s_line_22_is_carried_on_line_11600_and_not_on_line_21000() -> None:
    found = form(filer_is_transferring_spouse=0, line_22="7000")
    carried = return_worksheet(filer_is_transferring_spouse=0, line_22="10000")

    assert found.get(T1032_LINE_22).value == D("7000.00")
    assert found.get(T1032_LINE_22_CHECKED).value == D("7000.00")
    assert carried.get(ELECTED_SPLIT_PENSION_AMOUNT).value == D("10000.00")
    assert carried.get(ELECTED_SPLIT_PENSION_DEDUCTION).value == D("0.00")


def test_the_t1_lines_21000_and_11600_are_no_longer_typed_beside_line_22() -> None:
    for kind in (ELECTED_SPLIT_PENSION_DEDUCTION, ELECTED_SPLIT_PENSION_AMOUNT):
        artifacts = starting("0", (), "0", "0", "0", "0", "0")

        with pytest.raises(InvalidCompositionError):
            service().compute(CA_ON, 2025, *artifacts, Artifact(kind, D("4000")))


def test_a_return_with_an_amount_on_line_21000_and_no_pension_is_refused_either_way() -> None:
    for answer in (0, 1):
        with pytest.raises(InputAboveBoundError):
            run(
                eligible_pension="0",
                other_pensions="0",
                tax_on_pension="0",
                income_tax_deducted="0",
                line_22="99999",
                filer_is_transferring_spouse=answer,
            )


def test_an_elected_amount_on_line_11600_alone_is_the_receiving_spouse_s_line_22() -> None:
    found = form(filer_is_transferring_spouse=0, line_22="10000")

    assert found.get(T1032_LINE_22_CHECKED).value == D("10000.00")


def test_a_filer_is_transferring_spouse_count_of_2_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(filer_is_transferring_spouse=2)


# --- line 1 against line 8 of the Federal Worksheet for line 31400 --------------------------------


def test_a_transferring_spouse_s_line_1_equal_to_worksheet_line_8_passes_the_check() -> None:
    found = return_worksheet()

    assert found.get(T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("30000.00")
    assert found.get(T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("30000.00")


def test_a_transferring_spouse_s_line_1_above_worksheet_line_8_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(eligible_pension="30000.01", other_pensions="30000")


def test_a_transferring_spouse_s_line_1_below_worksheet_line_8_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(eligible_pension="29999.99", other_pensions="30000")


def test_a_receiving_spouse_s_line_1_is_not_checked_against_this_return_s_worksheet() -> None:
    found = return_worksheet(
        filer_is_transferring_spouse=0,
        eligible_pension="50000",
        other_pensions="0",
        line_22="10000",
    )

    assert found.get(T1032_LINE_1_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("0.00")
    assert found.get(T1032_WORKSHEET_LINE_8_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("0.00")


# --- line 4 against the other income of T1 line 13000 ---------------------------------------------
# Guide 5000-G: T4A-RCA box 17 is "already included in box 16", and the amounts of the T4A-RCA go on
# line 13000 of the T1, so a transferring spouse's line 4 is at most the return's other income.


def test_a_transferring_spouse_s_line_4_within_the_other_income_passes_the_check() -> None:
    found = return_worksheet(rca_box_17="5000", rca_payments_qualify=1, other_income="5000")

    assert found.get(T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("5000.00")


def test_a_transferring_spouse_s_line_4_with_other_income_above_it_passes_the_check() -> None:
    found = return_worksheet(rca_box_17="5000", rca_payments_qualify=1, other_income="9000")

    assert found.get(T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("5000.00")


def test_return_y_with_a_box_17_of_200000_and_no_other_income_is_refused() -> None:
    # Employment income of 60000, no pension, the transferring answer 1, an RCA answer of 1 and
    # line 21000 of 65741.73: the box 17 of 200000 is on no line of the return, so it is refused
    # and net income cannot be taken to 0.
    with pytest.raises(
        InputAboveBoundError,
        match=r"t1032_line_4_of_transferring_spouse .* is above .*other_income",
    ):
        run(
            employment_income="60000",
            eligible_pension="0",
            other_pensions="0",
            tax_on_pension="0",
            income_tax_deducted="0",
            rca_box_17="200000",
            rca_payments_qualify=1,
            other_income="0",
            line_22="65741.73",
        )


def test_a_transferring_spouse_s_box_17_one_cent_above_the_other_income_is_refused() -> None:
    with pytest.raises(
        InputAboveBoundError,
        match=r"t1032_line_4_of_transferring_spouse .* is above .*other_income",
    ):
        run(rca_box_17="5000.01", rca_payments_qualify=1, other_income="5000")


def test_a_receiving_spouse_s_box_17_is_not_checked_against_this_return_s_other_income() -> None:
    found = return_worksheet(
        filer_is_transferring_spouse=0,
        eligible_pension="50000",
        other_pensions="0",
        rca_box_17="200000",
        rca_payments_qualify=1,
        other_income="0",
        line_22="10000",
    )

    assert found.get(T1032_LINE_4_OF_TRANSFERRING_SPOUSE_CHECKED).value == D("0.00")


# --- Step 4: the pension income amounts of line 31400 --------------------------------------------


def test_line_31400_of_the_transferring_spouse_is_capped_at_2000() -> None:
    found = form()

    assert found.get(T1032_LINE_31).value == D("20000.00")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")


def test_line_31400_of_the_transferring_spouse_is_line_31_below_the_cap() -> None:
    found = form(eligible_pension="3000", line_22="1500", tax_on_pension="0")

    assert found.get(T1032_LINE_31).value == D("1500.00")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("1500.00")


def test_line_29_is_line_22_times_line_8_over_line_17_rounded_to_the_cent() -> None:
    found = form(rca_box_17="5000", rca_payments_qualify=1)

    assert found.get(T1032_LINE_29).value == D("1428.57")
    assert found.get(T1032_LINE_30).value == D("8571.43")


def test_line_29_is_0_when_line_8_is_0() -> None:
    assert form().get(T1032_LINE_29).value == D("0.00")
    assert form().get(T1032_LINE_30).value == D("10000.00")


def test_line_31400_of_the_receiving_spouse_is_capped_at_2000() -> None:
    found = form()

    assert found.get(T1032_LINE_34).value == D("10000.00")
    assert found.get(T1032_LINE_31400_RECEIVING).value == D("2000.00")


def test_line_31400_of_the_receiving_spouse_adds_its_own_pension_amount_on_line_32() -> None:
    found = form(receiving_pension="500", line_22="1000")

    assert found.get(T1032_LINE_34).value == D("1500.00")
    assert found.get(T1032_LINE_31400_RECEIVING).value == D("1500.00")


# --- Step 5: the income tax deducted -------------------------------------------------------------


def test_line_36_is_line_35_times_line_22_over_line_17() -> None:
    assert form().get(T1032_LINE_36).value == D("1000.00")


def test_line_36_is_0_on_a_zero_line_17_and_line_39_is_all_the_tax_deducted() -> None:
    # No pension, so line 17 is 0; the tax deducted (lines 37 and 40) is on 30,000 of employment.
    found = form(
        employment_income="30000",
        eligible_pension="0",
        tax_on_pension="0",
        line_22="0",
    )

    assert found.get(T1032_LINE_36).value == D("0.00")
    assert found.get(T1032_LINE_39).value == D("3000.00")


def test_line_39_is_line_37_less_line_36_for_the_transferring_spouse() -> None:
    # Line 37 is the return's own income tax deducted (3,000.00), line 36 is 1,000.00.
    assert form().get(T1032_LINE_39).value == D("2000.00")


def test_line_39_follows_the_return_s_own_income_tax_deducted() -> None:
    found = form(income_tax_deducted="4500", tax_on_pension="1500")

    # Line 36 = 1,500.00 x 10,000.00 / 30,000.00 = 500.00; line 39 = 4,500.00 - 500.00.
    assert found.get(T1032_LINE_36).value == D("500.00")
    assert found.get(T1032_LINE_39).value == D("4000.00")


def test_line_42_is_line_40_plus_line_36_for_the_receiving_spouse() -> None:
    # The receiving spouse's return: line 40 is its own income tax deducted (1,500.00), line 35 the
    # transferring spouse's tax on the pension (3,000.00), line 36 = 3,000.00 x 1,500.00 / 30,000.00
    # = 150.00.
    found = form(**RECEIVING)

    assert found.get(T1032_LINE_36).value == D("150.00")
    assert found.get(T1032_LINE_42).value == D("1650.00")


def test_tax_on_the_pension_above_all_the_transferring_tax_is_refused() -> None:
    with pytest.raises(InputAboveBoundError):
        run(tax_on_pension="3000.01", income_tax_deducted="3000")


def test_tax_on_the_pension_is_not_checked_against_a_receiving_spouse_s_own_tax_deducted() -> None:
    # Line 37 is the transferring spouse's total, which the receiving spouse's return does not
    # hold: its own 1,500.00 is line 40, so line 35 (3,000.00) above it is accepted.
    found = form(**RECEIVING)

    assert found.get(T1032_LINE_35_CHECKED).value == D("3000.00")


# --- T1 line 43700 read from the form -------------------------------------------------------------
# Form T1032 "Enter the result on line 43700 of the transferring spouse's ... return" (line 39) and
# "... of the receiving spouse's ... return" (line 42): the figure the total credits use.


def test_a_transferring_spouse_s_line_43700_is_line_39_and_the_refund_moves() -> None:
    found = return_worksheet()

    assert found.get(T1032_ELECTION_APPLIES).value == 1
    assert found.get(T1032_LINE_43700).value == D("2000.00")
    assert found.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("2000.00")
    # The only credit is line 43700, line 39 (2,000.00), not the 3,000.00 deducted.
    assert found.get(TOTAL_CREDITS).value == D("2000.00")
    assert found.get(REFUND_OR_BALANCE_OWING).value == (
        found.get(TOTAL_PAYABLE).value - D("2000.00")
    )


def test_a_receiving_spouse_s_line_43700_is_line_42() -> None:
    found = return_worksheet(**RECEIVING)

    assert found.get(T1032_ELECTION_APPLIES).value == 1
    assert found.get(T1032_LINE_43700).value == D("1650.00")
    assert found.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("1650.00")


def test_without_an_election_line_43700_is_the_tax_deducted_as_it_was() -> None:
    # Line 22 is 0, so the T1032 is not filed: the whole 500.00 deducted is credited.
    found = return_worksheet(
        eligible_pension="1500",
        line_22="0",
        tax_on_pension="0",
        income_tax_deducted="500",
    )

    assert found.get(T1032_ELECTION_APPLIES).value == 0
    assert found.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("500.00")
    assert found.get(TOTAL_CREDITS).value == D("500.00")


def test_a_receiving_spouse_without_an_election_keeps_its_own_line_43700() -> None:
    found = return_worksheet(**{**RECEIVING, "line_22": "0"})

    assert found.get(T1032_ELECTION_APPLIES).value == 0
    assert found.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("1500.00")


def test_a_line_43700_without_an_election_is_accepted_above_the_pension_income() -> None:
    # Guide 5000-G prints no limit on line 43700: the total of the slips' tax deducted is claimed.
    found = return_worksheet(
        eligible_pension="1500", line_22="0", tax_on_pension="0", income_tax_deducted="1500.01"
    )

    assert found.get(INCOME_TAX_DEDUCTED_AFTER_ELECTION).value == D("1500.01")


# --- T1 line 31400 read from the form ------------------------------------------------------------
# Form T1032 Step 4: "Enter on line 31400 of the transferring spouse's ... return, whichever is
# less: $2,000 or the amount from line 31" (line 34 for the receiving spouse). The Federal
# Worksheet for line 31400 sends the filer to the form "instead" when electing to split.


def test_a_transferring_spouse_s_line_31400_is_the_forms_amount_capped_at_2000() -> None:
    assert return_worksheet().get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_a_transferring_spouse_s_line_31400_is_line_31_below_the_cap() -> None:
    # Line 1 of 3,000.00, elected 1,500.00: line 31 = 3,000.00 - 1,500.00 = 1,500.00, although the
    # worksheet alone gives 2,000.00.
    found = return_worksheet(
        eligible_pension="3000",
        line_22="1500",
        tax_on_pension="0",
        income_tax_deducted="0",
    )

    assert found.get(PENSION_WORKSHEET_AMOUNT).value == D("2000.00")
    assert found.get(PENSION_INCOME_CREDIT).value == D("1500.00")


def test_a_receiving_spouse_s_line_31400_is_the_lesser_of_2000_and_line_34() -> None:
    # Line 32 is 0.00, line 33 is line 30 (1,500.00 less 0.00 on line 29), line 34 = 1,500.00.
    assert return_worksheet(**RECEIVING).get(PENSION_INCOME_CREDIT).value == D("1500.00")


def test_a_receiving_spouse_s_line_34_adds_line_32_and_is_capped_at_2000() -> None:
    # Its own pension, 900.00 (line 32), plus line 30, 1,500.00: line 34 is 2,400.00, so 2,000.00.
    found = return_worksheet(**{**RECEIVING, "receiving_pension": "900", "other_pensions": "900"})

    assert found.get(PENSION_WORKSHEET_AMOUNT).value == D("900.00")
    assert found.get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_without_an_election_line_31400_is_the_worksheet_amount() -> None:
    # Line 22 is 0: the worksheet's line 8 (1,500.00) is below $2,000.
    found = return_worksheet(
        eligible_pension="1500",
        line_22="0",
        tax_on_pension="0",
        income_tax_deducted="500",
    )

    assert found.get(PENSION_INCOME_CREDIT).value == D("1500.00")


def test_a_receiving_spouse_without_an_election_keeps_its_own_worksheet_amount() -> None:
    found = return_worksheet(
        **{**RECEIVING, "line_22": "0", "receiving_pension": "900", "other_pensions": "900"}
    )

    assert found.get(PENSION_INCOME_CREDIT).value == D("900.00")


# --- the worked return's figures -----------------------------------------------------------------


def test_the_worked_return_figures_of_the_form_are_the_hand_worked_ones() -> None:
    found = form()

    assert found.get(T1032_LINE_17).value == D("30000.00")
    assert found.get(T1032_LINE_21).value == D("15000.00")
    assert found.get(T1032_LINE_22_CHECKED).value == D("10000.00")
    assert found.get(T1032_LINE_31400_TRANSFERRING).value == D("2000.00")
    assert found.get(T1032_LINE_31400_RECEIVING).value == D("2000.00")
    assert found.get(T1032_LINE_36).value == D("1000.00")
    assert found.get(T1032_LINE_39).value == D("2000.00")
    # Line 42 is line 40 (the return's own 3,000.00) plus line 36 (1,000.00); this return is the
    # transferring spouse's, so it reads line 39, not this line.
    assert found.get(T1032_LINE_42).value == D("4000.00")
