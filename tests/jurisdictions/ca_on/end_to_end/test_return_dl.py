"""CA-ON 2025 end to end: return dl (the Ontario adoption, pension and student loan lines)."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import Artifact
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import (
    ADOPTION_CHILD_EXPENSES,
    ADOPTION_EXPENSE_CHILDREN,
    REFUND_OR_BALANCE_OWING,
    STUDENT_LOAN_INTEREST,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, D, service, starting


def return_dl(
    *,
    other_pensions: str = "1500",
    adoption_children: tuple[str, ...] = ("10000", "20000"),
    student_loan_interest: str = "600",
) -> Worksheet:
    """Return DL's inputs as in `returns/2025_return_dl.yaml`, over the keyword inputs given.

    The filer has 100,000 of employment income (a chosen figure) and no spouse; the keywords are
    the pension on line 11500, the filer's eligible adoption expenses for each child (one record
    each) and the student loan interest on line 31900.
    """
    records = [{ADOPTION_CHILD_EXPENSES: D(amount)} for amount in adoption_children]
    given = (
        Artifact(
            ADOPTION_EXPENSE_CHILDREN,
            RecordList(ADOPTION_EXPENSE_CHILDREN.fields, records),
        ),
        Artifact(STUDENT_LOAN_INTEREST, D(student_loan_interest)),
    )
    base = starting(
        "100000", (), "0", "0", "0", "0", "0", other_pensions_and_superannuation=other_pensions
    )
    kinds = {artifact.kind for artifact in given}
    rest = [artifact for artifact in base if artifact.kind not in kinds]
    return service().compute(CA_ON, 2025, *rest, *given)["ca-on/return"][0]


def test_the_worked_example_gives_the_three_ontario_lines() -> None:
    # ON428 line 23 and line 58330: 10,000 + the lesser of 20,000 and 15,551 = 25,551. Line 27 and
    # line 58360: the lesser of 1,762 and the line 31400 amount 1,500 = 1,500. Line 32 and line
    # 58520: the line 31900 amount, 600.
    worksheet = return_dl()

    assert worksheet.get(ontario.ADOPTION_CREDIT).value == D("25551.00")
    assert worksheet.get(ontario.PENSION_INCOME_CREDIT).value == D("1500.00")
    assert worksheet.get(STUDENT_LOAN_INTEREST).value == D("600")


def test_the_adoption_cap_is_applied_child_by_child_in_the_trace() -> None:
    rendered = EnglishTraceRenderer().render_all(return_dl().trace)

    assert "adoption_credit: item 1: 10000, at most 15551 = 10000 (half-up to 0.01)" in rendered
    assert "adoption_credit: item 2: 20000, at most 15551 = 15551 (half-up to 0.01)" in rendered
    assert "adoption_credit: item 1 10000 + item 2 15551 = 25551" in rendered


def test_line_44_is_the_sum_of_the_ontario_credit_amounts_with_the_three_lines() -> None:
    # Line 31 (through the disability transfer): 12,747.00 + 3,356.10 + 1,077.48 + 25,551.00 +
    # 1,500.00 = 44,231.58; line 35 and line 44 add the student loan interest 600: 44,831.58.
    # Line 46 is 5.05% of 44,831.58 = 2,263.9948, half-up 2,263.99.
    worksheet = return_dl()
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(ontario.CREDIT_AMOUNTS_THROUGH_DISABILITY_TRANSFER).value == D("44231.58")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("44831.58")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("2263.99")
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 0 "
        "+ cpp_base_contributions_on_return 3356.1 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 1077.48 + ei_premiums_on_self_employment 0 + adoption_credit 25551 "
        "+ pension_income_credit 1500 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 600 "
        "+ unused_tuition_claimed 0 + amounts_transferred_from_spouse 0 + medical_claim 0 "
        "= 44831.58"
    ) in rendered


def test_the_ontario_tax_and_the_balance_owing_follow_from_line_44() -> None:
    # Ontario tax on 100,426.00: 2,670.743 + 4,349.91 = 7,020.653, so 7,020.65, less 2,263.99 =
    # 4,756.66 (no surtax, tax reduction or LIFT credit) plus the health premium 750.00 =
    # 5,506.66. Net federal tax 9,295.47, so the total payable and balance owing are 14,802.13.
    worksheet = return_dl()

    assert worksheet.get(ontario.ONTARIO_TAX).value == D("5506.66")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("14802.13")


def test_no_adopted_children_and_no_pension_leave_the_ontario_lines_at_0() -> None:
    # The Ontario credit amounts are the basic personal amount 12,747.00, the CPP base
    # contributions 3,356.10 and the EI premiums 1,077.48: 17,180.58.
    worksheet = return_dl(other_pensions="0", adoption_children=(), student_loan_interest="0")

    assert worksheet.get(ontario.ADOPTION_CREDIT).value == D("0")
    assert worksheet.get(ontario.PENSION_INCOME_CREDIT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("17180.58")
