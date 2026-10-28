"""CA-ON 2025 end to end: return q."""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.caregiver_amount import CaregiverAmount
from tax_calculator.jurisdictions.ca.catalog import (
    CANADA_WORKERS_BENEFIT,
    CAREGIVER_AMOUNT,
    DEPENDANT_NET_INCOME,
    ELIGIBLE_DEPENDANT_AMOUNT,
    FEDERAL_TAX_AFTER_CREDITS,
    INFIRM_CHILDREN_AMOUNT,
    INFIRM_DEPENDANTS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca.trace import CaregiverClaimLine
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute


def return_q() -> Worksheet:
    """Return Q's inputs (`returns/2025_return_q.yaml`): Return I's and two infirm dependants."""
    return compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        income_tax_deducted="4800",
        infirm_dependants=("5000", "25000"),
    )


def test_return_qs_two_infirm_dependants_are_claimed_one_by_one_on_line_30450() -> None:
    # Return Q is Return I (employment income of 48000, taxable income 47555.00, federal tax on
    # it 6895.48, Ontario tax 1934.56 after the LIFT credit and the health premium, with no food
    # donations)
    # with two infirm dependants age 18 or older, of net incomes 5000 and 25000. Schedule 5 line
    # 30450, per dependant: 28798.00 - 5000 = 23798.00, at most 8601: 8601; 28798.00 - 25000 =
    # 3798.00; the total of the allowable amounts is 8601 + 3798.00 = 12399.00 (pooled, 28798.00
    # - 30000 would be negative and give 0). The amount for an eligible dependant is not claimed
    # for them (0 eligible dependants), the age, spouse and spouse caregiver amounts (lines 30100,
    # 30300 and 30425) are 0 from inputs at their no-claim values, and the Ontario caregiver
    # amount (ON428 line 58185) is computed from an empty list of dependants, 0. The federal
    # credit amounts are 16129 + 0 +
    # 0 + 0 + 0 + 12399.00 + 0 + 2202.75 + 787.20 + 1471 = 32988.95; 14.5% of it is
    # 4783.39775, rounded half-up to the cent: 4783.40, so the federal tax after credits is
    # 6895.48 - 4783.40 = 2112.08. The Ontario total of credit amounts is unchanged, 15736.95.
    # The total payable is 2112.08 + 1934.56 = 4046.64, and with the chosen tax deducted of 4800
    # and no Canada workers benefit, line 167 is 4046.64 - 4800 = -753.36, a refund.
    worksheet = return_q()

    assert worksheet.get(INFIRM_DEPENDANTS).value == RecordList(
        INFIRM_DEPENDANTS.fields,
        [{DEPENDANT_NET_INCOME: D("5000")}, {DEPENDANT_NET_INCOME: D("25000")}],
    )
    assert worksheet.producer_of(INFIRM_DEPENDANTS) is None
    assert isinstance(worksheet.producer_of(CAREGIVER_AMOUNT), CaregiverAmount)
    assert worksheet.get(CAREGIVER_AMOUNT).value == D("12399.00")
    assert worksheet.get(ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(INFIRM_CHILDREN_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("32988.95")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("4783.40")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("2112.08")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")
    assert worksheet.get(ONTARIO_TAX).value == D("1934.56")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4046.64")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-753.36")


def test_return_qs_trace_names_each_dependant_and_totals_the_credit_amounts() -> None:
    worksheet = return_q()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, CaregiverClaimLine | ItemsTotalLine) and line.output == CAREGIVER_AMOUNT
    ]
    assert lines == [
        CaregiverClaimLine(
            output=CAREGIVER_AMOUNT,
            position=1,
            base=Amount(D("28798.00")),
            net_income=D("5000"),
            maximum=Amount(D("8601")),
            rounding=CENT,
            result=D("8601.00"),
        ),
        CaregiverClaimLine(
            output=CAREGIVER_AMOUNT,
            position=2,
            base=Amount(D("28798.00")),
            net_income=D("25000"),
            maximum=Amount(D("8601")),
            rounding=CENT,
            result=D("3798.00"),
        ),
        ItemsTotalLine(
            output=CAREGIVER_AMOUNT,
            items=((1, D("8601.00")), (2, D("3798.00"))),
            total=D("12399.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "caregiver_amount: dependant 1: 28798 less net income 5000, at most 8601 = 8601 "
        "(half-up to 0.01)"
    )
    assert rendered[first : first + 3] == (
        "caregiver_amount: dependant 1: 28798 less net income 5000, at most 8601 = 8601 "
        "(half-up to 0.01)",
        "caregiver_amount: dependant 2: 28798 less net income 25000, at most 8601 = 3798 "
        "(half-up to 0.01)",
        "caregiver_amount: item 1 8601 + item 2 3798 = 12399",
    )
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 16129 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 "
        "+ caregiver_amount_for_spouse_or_dependant 0 "
        "+ caregiver_amount 12399 + infirm_children_amount 0 "
        "+ cpp_base_contributions_on_return 2202.75 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 0 + ei_premiums 787.2 "
        "+ ei_premiums_on_self_employment 0 + volunteer_firefighters_credit 0 + "
        "search_and_rescue_credit 0 + canada_employment_amount 1471 "
        "+ home_buyers_credit 0 + home_accessibility_credit 0 + adoption_credit 0 + "
        "pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + amounts_transferred_from_spouse 0 + "
        "medical_claim 0 = "
        "32988.95"
    ) in rendered


def test_infirm_dependants_pooled_would_give_the_wrong_line_30450() -> None:
    separate = compute("48000", (), "0", "0", "8640", "0", "0", infirm_dependants=("5000", "25000"))
    pooled = compute("48000", (), "0", "0", "8640", "0", "0", infirm_dependants=("30000",))

    assert separate.get(CAREGIVER_AMOUNT).value == D("12399.00")
    assert pooled.get(CAREGIVER_AMOUNT).value == D("0")


def test_no_infirm_dependants_claim_nothing_on_line_30450() -> None:
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(CAREGIVER_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("20589.95")


def test_infirm_dependants_do_not_change_the_ontario_credits() -> None:
    # ON428 line 58185 (the Ontario caregiver amount) is computed from an empty list here: 0.
    without = compute("48000", (), "0", "0", "8640", "0", "0")
    with_dependants = return_q()

    assert with_dependants.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS) == (
        without.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS)
    )
