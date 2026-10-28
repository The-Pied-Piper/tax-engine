"""CA-ON 2025 end to end: return w."""

from __future__ import annotations

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.errors import ValidationError
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.jurisdictions.ca.catalog import (
    CANADA_WORKERS_BENEFIT,
    CAREGIVER_AMOUNT,
    DEPENDANT_NET_INCOME,
    FEDERAL_TAX_AFTER_CREDITS,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.capabilities.caregiver_amount import OntarioCaregiverAmount
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
    ONTARIO_TAX_AFTER_CREDITS,
)
from tax_calculator.jurisdictions.ca_on.trace import CaregiverClaimLessClaimedLine
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, return_w


def test_return_ws_two_ontario_caregiver_dependants_are_claimed_one_by_one_on_line_58185() -> None:
    # Return W is Return Q (employment income of 48000, taxable income 47555.00, the Ontario tax
    # on it 2401.53) with two dependants for the Ontario caregiver amount, of net incomes 5000
    # and 25000, neither claimed on line 58160. Worksheet ON428 line 58185, per dependant:
    # 26562.00 - 5000 = 21562.00, at most 6008: 6008; 26562.00 - 25000 = 1562.00; line 4 is 0 for
    # both, so line 5 is line 3 and the total is 6008 + 1562.00 = 7570.00 (pooled, 26562.00 -
    # 30000 would be negative and give 0). ON428 line 58800 is 12747 + 0 + 0 + 0 + 7570.00 +
    # 2202.75 + 787.20 = 23306.95; 5.05% of it is 1177.000975, rounded half-up to the cent:
    # 1177.00, so the Ontario tax after credits is 2401.53 - 1177.00 = 1224.53, with no surtax
    # and no tax reduction (588.00 less 1224.53 is negative). After the LIFT credit of 122.25
    # that is 1102.28, with no food donations the food credit is 0.00 and it stays 1102.28, and
    # with the health premium of 450 the Ontario tax is 1552.28. The federal side is Return Q's:
    # the tax after credits is 2112.08, the total payable 2112.08 + 1552.28 = 3664.36 and, with
    # the chosen tax deducted of 4800 and no Canada workers benefit, line 167 is 3664.36 - 4800
    # = -1135.64, a refund.
    worksheet = return_w()

    assert worksheet.get(ontario.CAREGIVER_DEPENDANTS).value == RecordList(
        ontario.CAREGIVER_DEPENDANTS.fields,
        [
            {DEPENDANT_NET_INCOME: D("5000"), ontario.CLAIMED_AS_ELIGIBLE_DEPENDANT: 0},
            {DEPENDANT_NET_INCOME: D("25000"), ontario.CLAIMED_AS_ELIGIBLE_DEPENDANT: 0},
        ],
    )
    assert worksheet.producer_of(ontario.CAREGIVER_DEPENDANTS) is None
    assert isinstance(worksheet.producer_of(ontario.CAREGIVER_AMOUNT), OntarioCaregiverAmount)
    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("7570.00")
    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("23306.95")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("1177.00")
    assert worksheet.get(ONTARIO_TAX_AFTER_CREDITS).value == D("1224.53")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("1102.28")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("1102.28")
    assert worksheet.get(ONTARIO_TAX).value == D("1552.28")
    assert worksheet.get(CAREGIVER_AMOUNT).value == D("12399.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("32988.95")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("2112.08")
    assert worksheet.get(TOTAL_PAYABLE).value == D("3664.36")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-1135.64")


def test_return_ws_trace_names_each_ontario_dependant_and_totals_the_credit_amounts() -> None:
    worksheet = return_w()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, CaregiverClaimLessClaimedLine | ItemsTotalLine)
        and line.output == ontario.CAREGIVER_AMOUNT
    ]
    assert lines == [
        CaregiverClaimLessClaimedLine(
            output=ontario.CAREGIVER_AMOUNT,
            position=1,
            base=Amount(D("26562.00")),
            net_income=D("5000"),
            maximum=Amount(D("6008")),
            allowable_before_claimed=D("6008.00"),
            claimed=D("0"),
            rounding=CENT,
            result=D("6008.00"),
        ),
        CaregiverClaimLessClaimedLine(
            output=ontario.CAREGIVER_AMOUNT,
            position=2,
            base=Amount(D("26562.00")),
            net_income=D("25000"),
            maximum=Amount(D("6008")),
            allowable_before_claimed=D("1562.00"),
            claimed=D("0"),
            rounding=CENT,
            result=D("1562.00"),
        ),
        ItemsTotalLine(
            output=ontario.CAREGIVER_AMOUNT,
            items=((1, D("6008.00")), (2, D("1562.00"))),
            total=D("7570.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "caregiver_amount: dependant 1: 26562 less net income 5000, at most 6008 = 6008, "
        "less claimed 0 = 6008 (half-up to 0.01)"
    )
    assert rendered[first : first + 3] == (
        "caregiver_amount: dependant 1: 26562 less net income 5000, at most 6008 = 6008, "
        "less claimed 0 = 6008 (half-up to 0.01)",
        "caregiver_amount: dependant 2: 26562 less net income 25000, at most 6008 = 1562, "
        "less claimed 0 = 1562 (half-up to 0.01)",
        "caregiver_amount: item 1 6008 + item 2 1562 = 7570",
    )
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 7570 "
        "+ cpp_base_contributions_on_return 2202.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 787.2 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 + medical_claim 0 = 23306.95"
    ) in rendered


def test_the_ontario_dependants_pooled_would_give_the_wrong_line_58185() -> None:
    separate = return_w()
    pooled = return_w(caregiver_dependants=(("30000", 0),))

    assert separate.get(ontario.CAREGIVER_AMOUNT).value == D("7570.00")
    assert pooled.get(ontario.CAREGIVER_AMOUNT).value == D("0")


def test_no_ontario_caregiver_dependants_claim_nothing_on_line_58185() -> None:
    worksheet = return_w(caregiver_dependants=())

    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")
    assert worksheet.get(CAREGIVER_AMOUNT).value == D("12399.00")


def test_the_ontario_caregiver_dependants_are_a_list_of_their_own() -> None:
    # The list of line 30450 (Schedule 5) and that of line 58185 are separate inputs: the Ontario
    # amount may be claimed for the line 30400 dependant too, which line 30450 excludes.
    only_ontario = return_w(infirm_dependants=())
    only_federal = return_w(caregiver_dependants=())

    assert only_ontario.get(CAREGIVER_AMOUNT).value == D("0")
    assert only_ontario.get(ontario.CAREGIVER_AMOUNT).value == D("7570.00")
    assert only_federal.get(CAREGIVER_AMOUNT).value == D("12399.00")
    assert only_federal.get(ontario.CAREGIVER_AMOUNT).value == D("0")


def test_the_dependant_claimed_on_line_58160_takes_it_off_line_58185() -> None:
    # Return W with an eligible dependant of net income 9000, claimed on ON428 line 58160 (and on
    # line 30400): line 58160 is 11905.00 - 9000 = 2905.00, at most 10823, for 1 eligible
    # dependant. That dependant is also listed for the Ontario caregiver amount, flagged: line 3
    # is 26562.00 - 9000 = 17562.00, at most 6008: 6008; line 4 is the 2905.00 of line 58160;
    # line 5 is 6008 - 2905.00 = 3103.00. The other dependant (net income 25000, unflagged) has
    # line 3 of 1562.00 and a line 4 of 0: 1562.00. Line 58185 is 3103.00 + 1562.00 = 4665.00,
    # and ON428 line 58800 is 12747 + 0 + 0 + 2905.00 + 4665.00 + 2202.75 + 787.20 = 23306.95,
    # the same total as without the eligible dependant (2905.00 + 4665.00 = 7570.00): what line
    # 58160 claims, line 58185 does not claim again.
    worksheet = return_w(
        eligible_dependants=1,
        dependant_net_income="9000",
        infirm_dependants=("25000",),
        caregiver_dependants=(("9000", 1), ("25000", 0)),
    )

    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("2905.00")
    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("4665.00")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("23306.95")
    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, CaregiverClaimLessClaimedLine | ItemsTotalLine)
        and line.output == ontario.CAREGIVER_AMOUNT
    ]
    assert lines == [
        CaregiverClaimLessClaimedLine(
            output=ontario.CAREGIVER_AMOUNT,
            position=1,
            base=Amount(D("26562.00")),
            net_income=D("9000"),
            maximum=Amount(D("6008")),
            allowable_before_claimed=D("6008.00"),
            claimed=D("2905.00"),
            rounding=CENT,
            result=D("3103.00"),
        ),
        CaregiverClaimLessClaimedLine(
            output=ontario.CAREGIVER_AMOUNT,
            position=2,
            base=Amount(D("26562.00")),
            net_income=D("25000"),
            maximum=Amount(D("6008")),
            allowable_before_claimed=D("1562.00"),
            claimed=D("0"),
            rounding=CENT,
            result=D("1562.00"),
        ),
        ItemsTotalLine(
            output=ontario.CAREGIVER_AMOUNT,
            items=((1, D("3103.00")), (2, D("1562.00"))),
            total=D("4665.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "caregiver_amount: dependant 1: 26562 less net income 9000, at most 6008 = 6008, "
        "less claimed 2905 = 3103 (half-up to 0.01)"
    ) in rendered
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 2905 + caregiver_amount 4665 "
        "+ cpp_base_contributions_on_return 2202.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 787.2 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 + medical_claim 0 = 23306.95"
    ) in rendered


def test_a_line_58160_amount_above_line_3_leaves_line_5_at_zero_not_a_negative() -> None:
    # An eligible dependant with no net income claims 11905.00 - 0, at most 10823 on line 58160.
    # Flagged on the worksheet, its line 3 is 6008 and its line 4 10823, so line 3 minus line 4 is
    # negative and line 5 is "0"; the other dependant keeps its 1562.00. Line 58185 is 1562.00,
    # not 6008 + 1562.00 - 10823 (negative), and ON428 line 58800 is 12747 + 0 + 0 + 10823 +
    # 1562.00 + 2202.75 + 787.20 = 28121.95.
    worksheet = return_w(
        eligible_dependants=1,
        dependant_net_income="0",
        infirm_dependants=("25000",),
        caregiver_dependants=(("0", 1), ("25000", 0)),
    )

    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("10823")
    claim_lines = [
        line
        for line in worksheet.trace
        if isinstance(line, CaregiverClaimLessClaimedLine)
        and line.output == ontario.CAREGIVER_AMOUNT
    ]
    assert [(line.allowable_before_claimed, line.claimed, line.result) for line in claim_lines] == [
        (D("6008.00"), D("10823"), D("0")),
        (D("1562.00"), D("0"), D("1562.00")),
    ]
    assert not claim_lines[0].result.is_signed()
    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("1562.00")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("28121.95")


def test_an_unflagged_dependant_takes_nothing_off_line_58185_whatever_line_58160_is() -> None:
    worksheet = return_w(
        eligible_dependants=1,
        dependant_net_income="9000",
        infirm_dependants=("25000",),
        caregiver_dependants=(("5000", 0), ("25000", 0)),
    )

    assert worksheet.get(ontario.ELIGIBLE_DEPENDANT_AMOUNT).value == D("2905.00")
    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("7570.00")


def test_a_caregiver_dependant_flag_of_2_is_refused_through_the_return() -> None:
    # The flag is 0 or 1: 2 used to be read as claimed on line 58160, with no error.
    with pytest.raises(ValidationError, match=r"dependant 2.*flag is 2"):
        return_w(caregiver_dependants=(("5000", 0), ("5000", 2)))


def test_two_flagged_caregiver_dependants_are_refused_with_one_eligible_dependant() -> None:
    # Return W claims one eligible dependant (ca/eligible_dependants 1, so line 30400 and line
    # 58160 for one). Both caregiver dependants are flagged as the one claimed on line 58160: the
    # second flagged row is refused, as at most one dependant can be the eligible dependant.
    with pytest.raises(
        ValidationError,
        match=(
            r"dependant 2: the amount claimed on line 58160 flag is 1 but only 1 eligible "
            r"dependant\(s\) are claimed on line 30400"
        ),
    ):
        return_w(
            eligible_dependants=1,
            dependant_net_income="9000",
            infirm_dependants=("25000",),
            caregiver_dependants=(("9000", 1), ("25000", 1)),
        )


def test_a_flagged_caregiver_dependant_is_refused_with_no_eligible_dependant() -> None:
    # With no eligible dependant claimed (ca/eligible_dependants 0) there is no line 58160 claim
    # for a caregiver dependant to be flagged against: the flagged row is refused.
    with pytest.raises(
        ValidationError,
        match=(
            r"dependant 1: the amount claimed on line 58160 flag is 1 but only 0 eligible "
            r"dependant\(s\) are claimed on line 30400"
        ),
    ):
        return_w(
            eligible_dependants=0,
            infirm_dependants=("25000",),
            caregiver_dependants=(("9000", 1), ("25000", 0)),
        )
