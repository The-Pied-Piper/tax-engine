"""CA-ON 2025 end to end: return dg."""

from __future__ import annotations

from typing import Any

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.errors import InputAboveBoundError
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADDITIONAL_DEDUCTIONS,
    ADOPTION_CHILD_EXPENSES,
    ADOPTION_CREDIT,
    ADOPTION_EXPENSE_CHILDREN,
    FEDERAL_TAX_AFTER_CREDITS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
    HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED,
    HOME_ACCESSIBILITY_CREDIT,
    HOME_ACCESSIBILITY_EXPENSES,
    HOME_ACCESSIBILITY_LINE_2,
    HOME_BUYERS_CLAIM,
    HOME_BUYERS_CREDIT,
    HOME_BUYERS_MAXIMUM,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    PENSION_ANNUITY_CONDITIONS_MET,
    PENSION_ANNUITY_PAYMENTS,
    PENSION_CHART_LINE_5,
    PENSION_CHART_LINE_6,
    PENSION_CHART_LINE_7,
    PENSION_CHART_LINE_8,
    PENSION_FOREIGN_INCOME,
    PENSION_INCOME_CREDIT,
    PENSION_RRIF_TRANSFERRED,
    PENSION_US_IRA_INCOME,
    SEARCH_AND_RESCUE_CONDITIONS_MET,
    SEARCH_AND_RESCUE_CREDIT,
    STUDENT_LOAN_INTEREST,
    VOLUNTEER_AMOUNT_MAXIMUM,
    VOLUNTEER_CREDITS_CHECKED,
    VOLUNTEER_CREDITS_CLAIMED,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
    VOLUNTEER_FIREFIGHTERS_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting

# The inputs of return dg that are new to the line 33500 sum, by their short names. Each one the
# test does not give is 0 (no claim, not a condition met), so the return is the same as one that
# leaves the new lines out.
_COUNT_INPUTS: dict[str, ArtifactKind[Any]] = {
    "volunteer_firefighters_conditions_met": VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET,
    "search_and_rescue_conditions_met": SEARCH_AND_RESCUE_CONDITIONS_MET,
    "pension_annuity_conditions_met": PENSION_ANNUITY_CONDITIONS_MET,
}
_AMOUNT_INPUTS: dict[str, ArtifactKind[Any]] = {
    "home_buyers_claim": HOME_BUYERS_CLAIM,
    "home_accessibility_expenses": HOME_ACCESSIBILITY_EXPENSES,
    "home_accessibility_claimed_by_others": HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS,
    "pension_foreign_income": PENSION_FOREIGN_INCOME,
    "additional_deductions": ADDITIONAL_DEDUCTIONS,
    "pension_us_ira_income": PENSION_US_IRA_INCOME,
    "pension_rrif_transferred": PENSION_RRIF_TRANSFERRED,
    "pension_annuity_payments": PENSION_ANNUITY_PAYMENTS,
    "student_loan_interest": STUDENT_LOAN_INTEREST,
}


def return_dg(
    *,
    other_pensions: str = "0",
    adoption_children: tuple[str, ...] = (),
    **inputs: str | int,
) -> Worksheet:
    """Return DG's inputs as in `returns/2025_return_dg.yaml`, over the keyword inputs given.

    The filer has 100,000 of employment income (a chosen figure) and no spouse. `other_pensions`
    is the pension on line 11500 (the worked example gives 20,000), `adoption_children` the
    filer's eligible expenses for each child, one record each, and the other inputs are named as
    in `_COUNT_INPUTS` and `_AMOUNT_INPUTS`.
    """
    artifacts: list[Artifact[Any]] = []
    for name, kind in _COUNT_INPUTS.items():
        artifacts.append(Artifact(kind, int(inputs.get(name, 0))))
    for name, kind in _AMOUNT_INPUTS.items():
        artifacts.append(Artifact(kind, D(str(inputs.get(name, "0")))))
    records = [{ADOPTION_CHILD_EXPENSES: D(amount)} for amount in adoption_children]
    artifacts.append(
        Artifact(ADOPTION_EXPENSE_CHILDREN, RecordList(ADOPTION_EXPENSE_CHILDREN.fields, records))
    )
    base = starting(
        "100000", (), "0", "0", "0", "0", "0", other_pensions_and_superannuation=other_pensions
    )
    given = {artifact.kind for artifact in artifacts}
    rest = [artifact for artifact in base if artifact.kind not in given]
    return service().compute(CA_ON, 2025, *rest, *artifacts)["ca-on/return"][0]


def test_the_worked_example_adds_46600_to_the_line_33500_sum() -> None:
    # Adult filer: VFA with the conditions met 6,000; home buyers' 10,000; home accessibility
    # receipts 25,000 with none claimed by others 20,000; adoption expenses 8,000 for one child
    # 8,000; a pension of 20,000 with nothing excluded, so line 31400 is 2,000; student loan
    # interest 600. These add 46,600.00 to the amounts summed into line 33500.
    worksheet = return_dg(
        volunteer_firefighters_conditions_met=1,
        home_buyers_claim="10000",
        home_accessibility_expenses="25000",
        adoption_children=("8000",),
        other_pensions="20000",
        student_loan_interest="600",
    )
    without_the_new_inputs = return_dg(other_pensions="0")

    assert worksheet.get(VOLUNTEER_FIREFIGHTERS_CREDIT).value == D("6000.00")
    assert worksheet.get(HOME_BUYERS_CREDIT).value == D("10000.00")
    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("20000.00")
    assert worksheet.get(ADOPTION_CREDIT).value == D("8000.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value - without_the_new_inputs.get(
        NON_REFUNDABLE_CREDIT_AMOUNTS
    ).value == D("46600.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("68633.58")


def test_the_worked_example_leaves_a_positive_federal_tax_after_credits() -> None:
    # Basic federal tax after credits: 17,972.14 with the pension and none of the new lines, less
    # 14.5% of 46,600.00 = 6,757.00, so 11,215.14, less the top-up tax credit's rise of 56.32
    # ((9,951.87 - 8,319.38) x 3.45%), so 11,158.82.
    worksheet = return_dg(
        volunteer_firefighters_conditions_met=1,
        home_buyers_claim="10000",
        home_accessibility_expenses="25000",
        adoption_children=("8000",),
        other_pensions="20000",
        student_loan_interest="600",
    )

    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("11158.82")


def test_the_new_lines_compute_to_zero_when_nothing_is_claimed() -> None:
    worksheet = return_dg()

    assert worksheet.get(VOLUNTEER_FIREFIGHTERS_CREDIT).value == D("0")
    assert worksheet.get(SEARCH_AND_RESCUE_CREDIT).value == D("0")
    assert worksheet.get(VOLUNTEER_CREDITS_CLAIMED).value == D("0")
    assert worksheet.get(HOME_BUYERS_CREDIT).value == D("0")
    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("0")
    assert worksheet.get(ADOPTION_CREDIT).value == D("0")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("22033.58")


def test_the_vfa_and_the_srva_both_set_is_refused_as_above_the_bound() -> None:
    # T1 guide 5000-G: "You can claim $6,000 for the volunteer firefighters' amount (VFA) or search
    # and rescue volunteers' amount (SRVA), but not both". Both conditions met is 12,000, above the
    # $6,000 maximum, an input error.
    with pytest.raises(InputAboveBoundError):
        return_dg(volunteer_firefighters_conditions_met=1, search_and_rescue_conditions_met=1)


def test_the_vfa_alone_gives_6000() -> None:
    worksheet = return_dg(volunteer_firefighters_conditions_met=1)

    assert worksheet.get(VOLUNTEER_FIREFIGHTERS_CREDIT).value == D("6000.00")
    assert worksheet.get(VOLUNTEER_CREDITS_CHECKED).value == D("6000.00")
    assert worksheet.get(VOLUNTEER_AMOUNT_MAXIMUM).value == D("6000.00")


def test_the_srva_alone_gives_6000() -> None:
    worksheet = return_dg(search_and_rescue_conditions_met=1)

    assert worksheet.get(SEARCH_AND_RESCUE_CREDIT).value == D("6000.00")
    assert worksheet.get(VOLUNTEER_CREDITS_CHECKED).value == D("6000.00")


def test_home_accessibility_with_receipts_of_15000_and_4000_claimed_by_others_gives_11000() -> None:
    # Federal Worksheet line 2: the lesser of 15,000 and $20,000, so 15,000.00; line 4: 15,000.00
    # less the 4,000.00 claimed by others, so 11,000.00.
    worksheet = return_dg(
        home_accessibility_expenses="15000", home_accessibility_claimed_by_others="4000"
    )

    assert worksheet.get(HOME_ACCESSIBILITY_LINE_2).value == D("15000.00")
    assert worksheet.get(HOME_ACCESSIBILITY_CLAIMED_BY_OTHERS_CHECKED).value == D("4000")
    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("11000.00")


def test_home_accessibility_claimed_by_others_equal_to_line_2_gives_0() -> None:
    # Line 3 may equal line 2: 5,000.00 less 5,000 is 0.00.
    worksheet = return_dg(
        home_accessibility_expenses="5000", home_accessibility_claimed_by_others="5000"
    )

    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("0.00")


def test_home_accessibility_claimed_by_others_above_line_2_is_refused() -> None:
    # Federal Worksheet line 4 "Line 2 minus line 3" prints no "if negative, enter 0": line 2 of
    # 5,000.00 and 8,000 claimed by others would be -3,000, so it is an input error, not floored.
    with pytest.raises(
        InputAboveBoundError,
        match="ca/home_accessibility_claimed_by_others 8000 is above "
        "ca/home_accessibility_line_2 5000.00",
    ):
        return_dg(home_accessibility_expenses="5000", home_accessibility_claimed_by_others="8000")


def test_home_accessibility_with_receipts_of_25000_and_none_claimed_gives_20000() -> None:
    # The lesser of 25,000 and $20,000 is 20,000.00, and nothing is claimed by others.
    worksheet = return_dg(
        home_accessibility_expenses="25000", home_accessibility_claimed_by_others="0"
    )

    assert worksheet.get(HOME_ACCESSIBILITY_LINE_2).value == D("20000.00")
    assert worksheet.get(HOME_ACCESSIBILITY_CREDIT).value == D("20000.00")


def test_a_home_buyers_claim_above_10000_is_refused_as_above_the_bound() -> None:
    # T1 line 31270, "Enter $10,000 on line 31270 of your return if you are not splitting the
    # amount": the claim is at most the $10,000 maximum, and above it is an input error.
    with pytest.raises(InputAboveBoundError):
        return_dg(home_buyers_claim="12000")


def test_a_home_buyers_claim_of_10000_gives_10000() -> None:
    worksheet = return_dg(home_buyers_claim="10000")

    assert worksheet.get(HOME_BUYERS_MAXIMUM).value == D("10000.00")
    assert worksheet.get(HOME_BUYERS_CREDIT).value == D("10000.00")


def test_pension_of_20000_with_5000_foreign_pension_gives_line_6_15000_and_credit_2000() -> None:
    # Worksheet for line 31400: line 1 is 20,000 (line 11500), line 2 is 5,000 of foreign pension,
    # line 4 is 0, so line 5 is 5,000 and line 6 is 15,000.00. Line 8 is 15,000.00 (no annuity
    # payments), and line 31400 is the lesser of that and $2,000.
    # The foreign pension income is deducted on line 25600 (the additional deductions), so it is
    # given with that deduction of 5,000.
    worksheet = return_dg(
        other_pensions="20000", pension_foreign_income="5000", additional_deductions="5000"
    )

    assert worksheet.get(PENSION_CHART_LINE_5).value == D("5000.00")
    assert worksheet.get(PENSION_CHART_LINE_6).value == D("15000.00")
    assert worksheet.get(PENSION_CHART_LINE_8).value == D("15000.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_pension_of_1500_gives_a_pension_income_credit_of_1500() -> None:
    worksheet = return_dg(other_pensions="1500")

    assert worksheet.get(PENSION_CHART_LINE_6).value == D("1500.00")
    assert worksheet.get(PENSION_INCOME_CREDIT).value == D("1500.00")


def test_the_annuity_gate_at_0_leaves_line_7_zero_and_at_1_adds_the_payments() -> None:
    # Worksheet for line 31400, line 7: the annuity payments count only when the gate is 1 (aged
    # 65 or older on December 31, 2025, or the payments because of a spouse's death). With 1,500 of
    # pension and 1,000 of payments: line 8 is 1,500.00 at gate 0 and 2,500.00 at gate 1, so the
    # credit is 1,500.00 at gate 0 and 2,000.00 at gate 1.
    closed = return_dg(other_pensions="1500", pension_annuity_payments="1000")
    open_gate = return_dg(
        other_pensions="1500", pension_annuity_payments="1000", pension_annuity_conditions_met=1
    )

    assert closed.get(PENSION_CHART_LINE_7).value == D("0.00")
    assert closed.get(PENSION_INCOME_CREDIT).value == D("1500.00")
    assert open_gate.get(PENSION_CHART_LINE_7).value == D("1000.00")
    assert open_gate.get(PENSION_CHART_LINE_8).value == D("2500.00")
    assert open_gate.get(PENSION_INCOME_CREDIT).value == D("2000.00")


def test_no_adopted_children_in_the_list_gives_0() -> None:
    worksheet = return_dg(adoption_children=())

    assert worksheet.get(ADOPTION_CREDIT).value == D("0")


def test_two_children_adoption_expenses_of_8000_and_3000_give_11000() -> None:
    # Line 31300 adds the list: one record per child, the filer's eligible expenses for each.
    worksheet = return_dg(adoption_children=("8000", "3000"))

    assert worksheet.get(ADOPTION_CREDIT).value == D("11000.00")


def test_a_pension_exclusion_above_line_11500_is_refused_as_above_the_bound() -> None:
    # Federal Worksheet for line 31400, line 5 "Add lines 2 to 4." (5,000 of foreign pension
    # income) is "included in the amount on line 11500" (1,500), so it is refused above line 1 as
    # an input error, not taken as not below zero to 0.00 on line 6.
    with pytest.raises(InputAboveBoundError):
        return_dg(
            other_pensions="1500", pension_foreign_income="5000", additional_deductions="5000"
        )
