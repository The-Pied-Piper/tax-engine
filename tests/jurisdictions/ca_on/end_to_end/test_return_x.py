"""CA-ON 2025 end to end: return x."""

from __future__ import annotations

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.parameters.claim_reduction import ClaimReduction
from tax_engine.domain.parameters.rate import Rate
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.other_dependants_medical import (
    OtherDependantsMedical,
)
from tax_engine.jurisdictions.ca.catalog import (
    CANADA_WORKERS_BENEFIT,
    DEPENDANT_NET_INCOME,
    FEDERAL_TAX_AFTER_CREDITS,
    MEDICAL_CLAIM,
    MEDICAL_EXPENSES,
    MEDICAL_EXPENSES_OVER_THRESHOLD,
    MEDICAL_NET_INCOME_SHARE,
    MEDICAL_SUPPLEMENT_LINE_11,
    MEDICAL_SUPPLEMENT_LINE_13,
    MEDICAL_SUPPLEMENT_LINE_14,
    MEDICAL_SUPPLEMENT_LINE_15,
    MEDICAL_THRESHOLD,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_DEPENDANT_MEDICAL_EXPENSES,
    OTHER_DEPENDANTS,
    OTHER_DEPENDANTS_MEDICAL,
    REFUND_OR_BALANCE_OWING,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca.trace import OtherDependantMedicalLine
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute


def return_x() -> Worksheet:
    """Return X's inputs (`returns/2025_return_x.yaml`): Return I's, own medical expenses and two
    other dependants."""
    return compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        income_tax_deducted="4800",
        medical_expenses="4500",
        other_dependants=(("3000", "10000"), ("1000", "40000")),
    )


def test_return_xs_medical_expenses_are_claimed_on_lines_33099_and_33199() -> None:
    # Return X is Return I (employment income of 48000, net income 47555.00, taxable income
    # 47555.00, federal tax on it 6895.48) with medical expenses of 4500 for
    # the filer (a chosen figure, T1 line 107, line 33099) and two other dependants (a chosen
    # figure) with expenses 3000 and net income 10000, and expenses 1000 and net income 40000.
    # Line 108 is 3% of 47555.00 = 1426.65; line 109 is the lesser of 2834 and 1426.65 = 1426.65;
    # line 110 is 4500 - 1426.65 = 3073.35. Line 33199, per dependant: 3000 - lesser(300.00,
    # 2834) = 2700.00; 1000 - lesser(1200.00, 2834) is negative, so 0; the total, line 111, is
    # 2700.00 (pooled, 4000 - lesser(1500.00, 2834) = 2500.00 is the wrong figure). Line 112
    # (line 33200) is 3073.35 + 2700.00 = 5773.35. The federal credit amounts are 16129 + 0 + 0 +
    # 0 + 0 + 0 + 0 + 2202.75 + 787.20 + 1471 = 20589.95, plus 5773.35 = 26363.30; 14.5% of it is
    # 3822.6785, rounded half-up to the cent: 3822.68, so the federal tax after credits is
    # 6895.48 - 3822.68 = 3072.80. ON428 has the same lines: line 39 is 3% of 47555.00 =
    # 1426.65; line 40 is the lesser of 2885 and 1426.65 = 1426.65; line 41 is 4500 - 1426.65 =
    # 3073.35. Line 58729, per dependant: 3000 - lesser(300.00, 2885) = 2700.00; 1000 -
    # lesser(1200.00, 2885) is negative, so 0, neither near the maximum of 15551; the total,
    # line 42, is 2700.00. Line 43 (line 58769) is 3073.35 + 2700.00 = 5773.35. The Ontario total
    # of credit amounts (line 58800) is 12747 + 0 + 0 + 0 + 2202.75 + 787.20 + 5773.35 =
    # 21510.30; 5.05% of it is 1086.27015, rounded half-up to the cent: 1086.27, so the Ontario
    # tax after credits is 2401.53 - 1086.27 = 1315.26, below the surtax thresholds. The tax
    # reduction is 0 (twice 294.00 is less than the tax), the LIFT credit is 122.25 and the food
    # credit 0.00 (no food donations): 1315.26 - 122.25 - 0.00 = 1193.01, and with the health
    # premium of 450, the Ontario tax is 1643.01. The total payable is 3072.80 + 1643.01 =
    # 4715.81, and with the chosen tax deducted of 4800 and no Canada workers benefit, line 167
    # is 4715.81 - 4800 = -84.19, a refund.
    worksheet = return_x()

    assert worksheet.get(MEDICAL_EXPENSES).value == D("4500")
    assert worksheet.producer_of(MEDICAL_EXPENSES) is None
    assert worksheet.producer_of(OTHER_DEPENDANTS) is None
    assert worksheet.get(OTHER_DEPENDANTS).value == RecordList(
        OTHER_DEPENDANTS.fields,
        [
            {OTHER_DEPENDANT_MEDICAL_EXPENSES: D("3000"), DEPENDANT_NET_INCOME: D("10000")},
            {OTHER_DEPENDANT_MEDICAL_EXPENSES: D("1000"), DEPENDANT_NET_INCOME: D("40000")},
        ],
    )
    assert worksheet.get(NET_INCOME).value == D("47555.00")
    assert worksheet.get(MEDICAL_NET_INCOME_SHARE).value == D("1426.65")
    assert worksheet.get(MEDICAL_THRESHOLD).value == D("1426.65")
    assert worksheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("3073.35")
    assert worksheet.get(OTHER_DEPENDANTS_MEDICAL).value == D("2700.00")
    assert worksheet.get(MEDICAL_CLAIM).value == D("5773.35")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("26363.30")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("3822.68")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("3072.80")
    assert worksheet.producer_of(ontario.MEDICAL_NET_INCOME_SHARE) is not None
    assert worksheet.get(ontario.MEDICAL_NET_INCOME_SHARE).value == D("1426.65")
    assert worksheet.get(ontario.MEDICAL_THRESHOLD).value == D("1426.65")
    assert worksheet.get(ontario.MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("3073.35")
    assert worksheet.get(ontario.OTHER_DEPENDANTS_MEDICAL).value == D("2700.00")
    assert worksheet.get(ontario.MEDICAL_CLAIM).value == D("5773.35")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("21510.30")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("1086.27")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1315.26")
    assert worksheet.get(ONTARIO_TAX).value == D("1643.01")
    assert worksheet.get(TOTAL_PAYABLE).value == D("4715.81")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    # T1 line 154 (line 45200): line 16 of the Federal Worksheet, 25% of the medical claim of
    # 5773.35 (1443.34) less 5% of the net income of 47555.00 over 33294.00 (713.05).
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_11).value == D("5773.35")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_13).value == D("1443.34")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_14).value == D("1443.34")
    assert worksheet.get(MEDICAL_SUPPLEMENT_LINE_15).value == D("713.05")
    assert worksheet.get(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT).value == D("730.29")
    assert worksheet.get(TOTAL_CREDITS).value == D("5530.29")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-814.48")


def test_return_xs_trace_names_each_step_and_each_dependant() -> None:
    worksheet = return_x()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, OtherDependantMedicalLine | ItemsTotalLine)
        and line.output == OTHER_DEPENDANTS_MEDICAL
    ]
    assert lines == [
        OtherDependantMedicalLine(
            output=OTHER_DEPENDANTS_MEDICAL,
            position=1,
            expenses=D("3000"),
            net_income=D("10000"),
            reduction=ClaimReduction(Rate(D("0.03")), D("2834")),
            rounding=CENT,
            result=D("2700.00"),
        ),
        OtherDependantMedicalLine(
            output=OTHER_DEPENDANTS_MEDICAL,
            position=2,
            expenses=D("1000"),
            net_income=D("40000"),
            reduction=ClaimReduction(Rate(D("0.03")), D("2834")),
            rounding=CENT,
            result=D("0"),
        ),
        ItemsTotalLine(
            output=OTHER_DEPENDANTS_MEDICAL,
            items=((1, D("2700.00")), (2, D("0"))),
            total=D("2700.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "other_dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2834 = 2700 (half-up to 0.01)"
    )
    assert rendered[first : first + 3] == (
        "other_dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2834 = 2700 (half-up to 0.01)",
        "other_dependants_medical: dependant 2: expenses 1000 less the lesser of 3% of net income "
        "40000 and 2834 = 0 (half-up to 0.01)",
        "other_dependants_medical: item 1 2700 + item 2 0 = 2700",
    )
    for sentence in (
        "medical_net_income_share: 3% of net_income 47555 (half-up to 0.01)",
        "medical_threshold: lesser of medical_net_income_share 1426.65 and 2834 (half-up to 0.01)",
        "medical_expenses_over_threshold: medical_expenses 4500 less medical_threshold 1426.65, "
        "not below 0 = 3073.35",
        "medical_claim: medical_expenses_over_threshold 3073.35 + other_dependants_medical 2700 "
        "= 5773.35",
        "non_refundable_credit_amounts: basic_personal_amount 16129 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 "
        "+ caregiver_amount_for_spouse_or_dependant 0 "
        "+ caregiver_amount 0 + infirm_children_amount 0 "
        "+ cpp_base_contributions_on_return 2202.75 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 0 + ei_premiums 787.2 "
        "+ ei_premiums_on_self_employment 0 + volunteer_firefighters_credit 0 + "
        "search_and_rescue_credit 0 + canada_employment_amount 1471 "
        "+ home_buyers_credit 0 + home_accessibility_credit 0 + adoption_credit 0 + "
        "pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + amounts_transferred_from_spouse 0 + "
        "medical_claim "
        "5773.35 = 26363.3",
    ):
        assert sentence in rendered


def test_other_dependants_pooled_would_give_the_wrong_line_33199() -> None:
    separate = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        other_dependants=(("3000", "10000"), ("1000", "40000")),
    )
    pooled = compute("48000", (), "0", "0", "8640", "0", "0", other_dependants=(("4000", "50000"),))

    assert separate.get(OTHER_DEPENDANTS_MEDICAL).value == D("2700.00")
    # 4000 - lesser(1500.00, 2834) = 2500.00, not 2700.00.
    assert pooled.get(OTHER_DEPENDANTS_MEDICAL).value == D("2500.00")


def test_no_medical_expenses_claim_nothing_on_line_33200() -> None:
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(OTHER_DEPENDANTS_MEDICAL).value == D("0")
    assert worksheet.get(MEDICAL_CLAIM).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("20589.95")


def test_medical_expenses_below_the_threshold_claim_nothing_on_line_33099() -> None:
    # 3% of 47555.00 is 1426.65: expenses of 1426.65 or less give line 110 of 0.
    at = compute("48000", (), "0", "0", "8640", "0", "0", medical_expenses="1426.65")
    over = compute("48000", (), "0", "0", "8640", "0", "0", medical_expenses="1426.66")

    assert at.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("0")
    assert over.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("0.01")


def test_the_threshold_on_line_109_stops_at_2834() -> None:
    # 3% of a net income above 94466.67 is above the 2834 ceiling, so expenses of 5000 leave
    # 5000 - 2834 = 2166 on line 110.
    worksheet = compute("115000", (), "0", "0", "0", "0", "0", medical_expenses="5000")

    assert worksheet.get(MEDICAL_NET_INCOME_SHARE).value > D("2834")
    assert worksheet.get(MEDICAL_THRESHOLD).value == D("2834")
    assert worksheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("2166")


def test_return_xs_ontario_trace_names_each_step_and_each_dependant() -> None:
    worksheet = return_x()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, OtherDependantMedicalLine | ItemsTotalLine)
        and line.output == ontario.OTHER_DEPENDANTS_MEDICAL
    ]
    reduction = ClaimReduction(Rate(D("0.03")), D("2885"), D("15551"))
    assert lines == [
        OtherDependantMedicalLine(
            output=ontario.OTHER_DEPENDANTS_MEDICAL,
            position=1,
            expenses=D("3000"),
            net_income=D("10000"),
            reduction=reduction,
            rounding=CENT,
            result=D("2700.00"),
        ),
        OtherDependantMedicalLine(
            output=ontario.OTHER_DEPENDANTS_MEDICAL,
            position=2,
            expenses=D("1000"),
            net_income=D("40000"),
            reduction=reduction,
            rounding=CENT,
            result=D("0"),
        ),
        ItemsTotalLine(
            output=ontario.OTHER_DEPENDANTS_MEDICAL,
            items=((1, D("2700.00")), (2, D("0"))),
            total=D("2700.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "other_dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2885 = 2700, at most 15551 (half-up to 0.01)"
    )
    assert rendered[first : first + 3] == (
        "other_dependants_medical: dependant 1: expenses 3000 less the lesser of 3% of net income "
        "10000 and 2885 = 2700, at most 15551 (half-up to 0.01)",
        "other_dependants_medical: dependant 2: expenses 1000 less the lesser of 3% of net income "
        "40000 and 2885 = 0, at most 15551 (half-up to 0.01)",
        "other_dependants_medical: item 1 2700 + item 2 0 = 2700",
    )
    for sentence in (
        "medical_threshold: lesser of medical_net_income_share 1426.65 and 2885 (half-up to 0.01)",
        "medical_expenses_over_threshold: medical_expenses 4500 less medical_threshold 1426.65, "
        "not below 0 = 3073.35",
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 0 "
        "+ cpp_base_contributions_on_return 2202.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 787.2 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 "
        "+ medical_claim 5773.35 = 21510.3",
        "credit_amounts_at_credit_rate: 5.05% of non_refundable_credit_amounts 21510.3 "
        "(half-up to 0.01)",
    ):
        assert sentence in rendered


def test_ontario_shares_the_filers_expenses_and_the_dependants_with_the_t1() -> None:
    worksheet = return_x()

    assert worksheet.producer_of(ontario.MEDICAL_CLAIM) is not worksheet.producer_of(MEDICAL_CLAIM)
    ontario_dependants = worksheet.producer_of(ontario.OTHER_DEPENDANTS_MEDICAL)
    assert isinstance(ontario_dependants, OtherDependantsMedical)
    assert ontario_dependants.consumes == frozenset({OTHER_DEPENDANTS})
    assert worksheet.producer_of(MEDICAL_EXPENSES) is None
    assert worksheet.get(ontario.MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("3073.35")


def test_ontario_medical_expenses_change_only_the_ontario_credits_by_the_claim() -> None:
    without = compute("48000", (), "0", "0", "8640", "0", "0")
    with_medical = return_x()

    assert without.get(ontario.MEDICAL_CLAIM).value == D("0")
    assert with_medical.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == (
        without.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value + D("5773.35")
    )
