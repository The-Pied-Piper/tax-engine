"""CA-ON 2025 end to end: return ab."""

from __future__ import annotations

from typing import Any

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.parameters.amount import Amount
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.trace import ItemsTotalLine
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.capabilities.disability_transfer_amount import (
    DisabilityTransferAmount,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CANADA_WORKERS_BENEFIT,
    CAREGIVER_AMOUNT,
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
    FEDERAL_TAX_AFTER_CREDITS,
    MEDICAL_CLAIM,
    MEDICAL_EXPENSES_OVER_THRESHOLD,
    MEDICAL_THRESHOLD,
    NET_INCOME,
    NON_REFUNDABLE_CREDIT_AMOUNTS,
    NON_REFUNDABLE_TAX_CREDITS,
    OTHER_DEPENDANTS_MEDICAL,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    TOTAL_PAYABLE,
)
from tax_calculator.jurisdictions.ca.trace import DisabilityTransferLine
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tax_calculator.jurisdictions.ca_on.capabilities.disability_transfer_amount import (
    OntarioDisabilityTransferAmount,
)
from tax_calculator.jurisdictions.ca_on.catalog import (
    ONTARIO_TAX,
)
from tests.jurisdictions.ca_on.end_to_end.support import CENT, D, compute, return_w


def return_ab(**overrides: Any) -> Worksheet:
    """Return AB's inputs (`returns/2025_return_ab.yaml`): Return W's and a dependant aged 20.

    The dependant is listed for the T1 (line 98 of their return 16129) and for ON428 (line 28 of
    their ON428 15000, a chosen figure). `overrides` replace any keyword of `return_w`, for the
    variants below.
    """
    given: dict[str, Any] = {
        "disability_dependants": ((0, "0", "16129", "20000"),),
        "ontario_disability_dependants": ((0, "0", "15000", "20000"),),
    }
    return return_w(**{**given, **overrides})


def test_return_abs_dependant_with_a_disability_transfers_6267_on_line_31800() -> None:
    # Return AB is Return W (employment income of 48000, taxable income 47555.00, federal tax on
    # it 6895.48, the Ontario figures of Return W, the Canada caregiver amount for two infirm
    # dependants 12399.00) with one dependant with a disability, aged 20 (so worksheet line 7 is
    # "0"), no care expenses, line 98 of their return 16129 and their taxable income 20000, all
    # chosen figures. Federal Worksheet line 31800: line 8 = 10138.00 + 0; line 10 = 10138.00 +
    # 16129 = 26267.00; line 12 = 26267.00 - 20000 = 6267.00; line 13 = lesser(10138.00,
    # 6267.00) = 6267.00, the total of the allowable amounts. The federal credit amounts are
    # 16129 + 0 + 0 + 0 + 0 + 12399.00 + 0 + 2202.75 + 787.20 + 1471 + 6267.00 = 39255.95; 14.5%
    # of it is 5692.11275, rounded half-up to the cent: 5692.11, so the federal tax after
    # credits is 6895.48 - 5692.11 = 1203.37. The Ontario total of credit amounts is Return W's,
    # 23306.95, plus the Ontario disability amount, ON428 line 58480, 5298.00 (the next test):
    # 28604.95, so the Ontario tax is 1284.73. The total payable is 1203.37 + 1284.73 = 2488.10,
    # and with the chosen tax deducted of 4800 and no Canada workers benefit, line 167 is
    # 2488.10 - 4800 = -2311.90, a refund.
    worksheet = return_ab()

    assert worksheet.get(DISABILITY_DEPENDANTS).value == RecordList(
        DISABILITY_DEPENDANTS.fields,
        [
            {
                DEPENDANT_UNDER_18: 0,
                DEPENDANT_CARE_EXPENSES: D("0"),
                DEPENDANT_CREDIT_AMOUNTS: D("16129"),
                DEPENDANT_TAXABLE_INCOME: D("20000"),
            }
        ],
    )
    assert worksheet.producer_of(DISABILITY_DEPENDANTS) is None
    assert isinstance(
        worksheet.producer_of(DISABILITY_TRANSFERRED_AMOUNT), DisabilityTransferAmount
    )
    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("6267.00")
    assert worksheet.get(CAREGIVER_AMOUNT).value == D("12399.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("39255.95")
    assert worksheet.get(NON_REFUNDABLE_TAX_CREDITS).value == D("5692.11")
    assert worksheet.get(FEDERAL_TAX_AFTER_CREDITS).value == D("1203.37")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("28604.95")
    assert worksheet.get(ONTARIO_TAX).value == D("1284.73")
    assert worksheet.get(TOTAL_PAYABLE).value == D("2488.10")
    assert worksheet.get(CANADA_WORKERS_BENEFIT).value == D("0")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2311.90")


def test_return_abs_trace_names_the_dependant_and_totals_the_credit_amounts() -> None:
    worksheet = return_ab()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, DisabilityTransferLine | ItemsTotalLine)
        and line.output == DISABILITY_TRANSFERRED_AMOUNT
    ]
    assert lines == [
        DisabilityTransferLine(
            output=DISABILITY_TRANSFERRED_AMOUNT,
            position=1,
            base=Amount(D("10138.00")),
            supplement=Amount(D("5914.00")),
            threshold=Amount(D("3464.00")),
            maximum=Amount(D("16052")),
            under_18=0,
            care_expenses=D("0"),
            line_5=D("0"),
            line_6=D("5914.00"),
            line_7=D("0"),
            line_8=D("10138.00"),
            credit_amounts=D("16129"),
            line_10=D("26267.00"),
            taxable_income=D("20000"),
            line_12=D("6267.00"),
            rounding=CENT,
            result=D("6267.00"),
        ),
        ItemsTotalLine(
            output=DISABILITY_TRANSFERRED_AMOUNT,
            items=((1, D("6267.00")),),
            total=D("6267.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "disability_transferred_amount: dependant 1: 18 or older: base 10138 + 0, at most 16052 "
        "= 10138; 10138 + credit amounts 16129 less taxable income 20000 = 6267; "
        "the lesser of 10138 and 6267 = 6267 (half-up to 0.01)"
    )
    assert rendered[first : first + 2] == (
        "disability_transferred_amount: dependant 1: 18 or older: base 10138 + 0, at most 16052 "
        "= 10138; 10138 + credit amounts 16129 less taxable income 20000 = 6267; "
        "the lesser of 10138 and 6267 = 6267 (half-up to 0.01)",
        "disability_transferred_amount: item 1 6267 = 6267",
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
        "+ disability_transferred_amount 6267 + student_loan_interest 0 + federal_tuition_amount "
        "0 + "
        "tuition_transferred_from_child_checked 0 + amounts_transferred_from_spouse 0 + "
        "medical_claim 0 "
        "= 39255.95"
    ) in rendered


def test_a_dependant_under_18_with_care_expenses_transfers_the_reduced_supplement() -> None:
    # Care expenses of 5000: line 5 = 5000 - 3464.00 = 1536.00; line 6 = 5914.00 - 1536.00 =
    # 4378.00; line 7 = line 6; line 8 = 10138.00 + 4378.00 = 14516.00; with no credit amounts
    # and no taxable income line 12 = 14516.00, and line 13 is 14516.00.
    worksheet = compute(
        "48000", (), "0", "0", "8640", "0", "0", disability_dependants=((1, "5000", "0", "0"),)
    )

    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("14516.00")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("35105.95")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "disability_transferred_amount: dependant 1: under 18: care expenses 5000 less threshold "
        "3464 = 1536; supplement 5914 less 1536 = 4378; base 10138 + 4378, at most 16052 = 14516; "
        "14516 + credit amounts 0 less taxable income 0 = 14516; "
        "the lesser of 14516 and 14516 = 14516 (half-up to 0.01)"
    ) in rendered


def test_two_dependants_with_a_disability_are_transferred_one_by_one_on_line_31800() -> None:
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        disability_dependants=((0, "0", "16129", "20000"), (1, "5000", "0", "0")),
    )

    # 6267.00 + 14516.00 = 20783.00.
    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("20783.00")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "disability_transferred_amount: item 1 6267 + item 2 14516 = 20783" in rendered


def test_a_dependants_taxable_income_above_their_credits_transfers_nothing() -> None:
    # Line 10 = 10138.00 + 0; line 12 = 10138.00 - 20000 is negative, "0".
    worksheet = compute(
        "48000", (), "0", "0", "8640", "0", "0", disability_dependants=((0, "0", "0", "20000"),)
    )

    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("20589.95")


def test_no_dependants_with_a_disability_transfer_nothing_on_line_31800() -> None:
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert worksheet.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("20589.95")


def test_return_abs_dependant_with_a_disability_transfers_5298_on_line_58480() -> None:
    # The same dependant, listed for ON428 on its own: not under 18 (worksheet line 6 is "0"), no
    # care expenses, line 28 of their ON428 15000 (a chosen figure) and taxable income 20000.
    # Worksheet ON428 line 58480: line 7 = 10298.00 + 0; line 9 = 10298.00 + 15000 = 25298.00;
    # line 11 = 25298.00 - 20000 = 5298.00; line 12 = lesser(10298.00, 5298.00) = 5298.00, the
    # total of the allowable amounts. ON428 line 58800 is 12747 + 0 + 0 + 0 + 7570.00 + 2202.75 +
    # 787.20 + 5298.00 = 28604.95; 5.05% of it is 1444.549975, rounded half-up to the cent:
    # 1444.55, so the Ontario tax after credits is 2401.53 - 1444.55 = 956.98, with no surtax and
    # no tax reduction (588.00 less 956.98 is negative). After the LIFT credit of 122.25 that is
    # 834.73, with no food donations the food credit is 0.00 and it stays 834.73, and with the
    # health premium of 450 the Ontario tax is 1284.73, where Return W's was 1552.28. The total
    # payable is 1203.37 + 1284.73 = 2488.10 and line 167 is 2488.10 - 4800 = -2311.90, a refund.
    worksheet = return_ab()

    assert worksheet.get(ontario.DISABILITY_DEPENDANTS).value == RecordList(
        ontario.DISABILITY_DEPENDANTS.fields,
        [
            {
                DEPENDANT_UNDER_18: 0,
                DEPENDANT_CARE_EXPENSES: D("0"),
                ontario.DEPENDANT_ON428_LINE_28: D("15000"),
                DEPENDANT_TAXABLE_INCOME: D("20000"),
            }
        ],
    )
    assert worksheet.producer_of(ontario.DISABILITY_DEPENDANTS) is None
    assert isinstance(
        worksheet.producer_of(ontario.DISABILITY_TRANSFERRED_AMOUNT),
        OntarioDisabilityTransferAmount,
    )
    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("5298.00")
    assert worksheet.get(ontario.CAREGIVER_AMOUNT).value == D("7570.00")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("28604.95")
    assert worksheet.get(ontario.NON_REFUNDABLE_TAX_CREDITS).value == D("1444.55")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_CREDITS).value == D("956.98")
    assert worksheet.get(ontario.ONTARIO_SURTAX).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_WITH_SURTAX).value == D("956.98")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_DIVIDEND_CREDIT).value == D("956.98")
    assert worksheet.get(ontario.ONTARIO_TAX_REDUCTION).value == D("0")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_REDUCTION).value == D("956.98")
    assert worksheet.get(ontario.LIFT_CREDIT).value == D("122.25")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_LIFT_CREDIT).value == D("834.73")
    assert worksheet.get(ontario.COMMUNITY_FOOD_PROGRAM_CREDIT).value == D("0.00")
    assert worksheet.get(ontario.ONTARIO_TAX_AFTER_FOOD_CREDIT).value == D("834.73")
    assert worksheet.get(ontario.ONTARIO_HEALTH_PREMIUM).value == D("450")
    assert worksheet.get(ONTARIO_TAX).value == D("1284.73")
    assert worksheet.get(TOTAL_PAYABLE).value == D("2488.10")
    assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-2311.90")
    assert worksheet.get(REFUND).value == D("2311.90")
    assert worksheet.get(ontario.NET_REFUND).value == D("2311.90")


def test_return_abs_ontario_trace_names_the_dependant_and_totals_the_credit_amounts() -> None:
    worksheet = return_ab()

    lines = [
        line
        for line in worksheet.trace
        if isinstance(line, DisabilityTransferLine | ItemsTotalLine)
        and line.output == ontario.DISABILITY_TRANSFERRED_AMOUNT
    ]
    # The T1's trace line is reused: its fields follow the federal worksheet's numbering, so
    # `line_8` is ON428's line 7, `credit_amounts` its line 8 (line 28 of the dependant's ON428),
    # `line_10` its line 9, `taxable_income` its line 10 and `line_12` its line 11.
    assert lines == [
        DisabilityTransferLine(
            output=ontario.DISABILITY_TRANSFERRED_AMOUNT,
            position=1,
            base=Amount(D("10298.00")),
            supplement=Amount(D("6007.00")),
            threshold=Amount(D("3518.00")),
            maximum=Amount(D("16305")),
            under_18=0,
            care_expenses=D("0"),
            line_5=D("0"),
            line_6=D("6007.00"),
            line_7=D("0"),
            line_8=D("10298.00"),
            credit_amounts=D("15000"),
            line_10=D("25298.00"),
            taxable_income=D("20000"),
            line_12=D("5298.00"),
            rounding=CENT,
            result=D("5298.00"),
        ),
        ItemsTotalLine(
            output=ontario.DISABILITY_TRANSFERRED_AMOUNT,
            items=((1, D("5298.00")),),
            total=D("5298.00"),
        ),
    ]
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    first = rendered.index(
        "disability_transferred_amount: dependant 1: 18 or older: base 10298 + 0, at most 16305 "
        "= 10298; 10298 + credit amounts 15000 less taxable income 20000 = 5298; "
        "the lesser of 10298 and 5298 = 5298 (half-up to 0.01)"
    )
    assert rendered[first : first + 2] == (
        "disability_transferred_amount: dependant 1: 18 or older: base 10298 + 0, at most 16305 "
        "= 10298; 10298 + credit amounts 15000 less taxable income 20000 = 5298; "
        "the lesser of 10298 and 5298 = 5298 (half-up to 0.01)",
        "disability_transferred_amount: item 1 5298 = 5298",
    )
    assert (
        "non_refundable_credit_amounts: basic_personal_amount 12747 + age_amount 0 "
        "+ spouse_amount 0 + eligible_dependant_amount 0 + caregiver_amount 7570 "
        "+ cpp_base_contributions_on_return 2202.75 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 787.2 + ei_premiums_on_self_employment 0 "
        "+ adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 5298 + student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 "
        "+ medical_claim 0 = 28604.95"
    ) in rendered
    # The T1's own line is told apart by the amounts it works on.
    assert (
        "disability_transferred_amount: dependant 1: 18 or older: base 10138 + 0, at most 16052 "
        "= 10138; 10138 + credit amounts 16129 less taxable income 20000 = 6267; "
        "the lesser of 10138 and 6267 = 6267 (half-up to 0.01)"
    ) in rendered


def test_the_ontario_dependants_with_a_disability_are_a_list_of_their_own() -> None:
    # The T1 and ON428 each read their own list: with the Ontario one empty the T1 still
    # transfers 6267.00 and ON428 nothing; with the T1's empty ON428 still transfers 5298.00.
    federal_only = return_ab(ontario_disability_dependants=())
    ontario_only = return_ab(disability_dependants=())
    neither = return_w()

    assert federal_only.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("6267.00")
    assert federal_only.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert federal_only.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("23306.95")
    assert federal_only.get(ONTARIO_TAX).value == D("1552.28")
    assert ontario_only.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert ontario_only.get(NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("32988.95")
    assert ontario_only.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("5298.00")
    assert ontario_only.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("28604.95")
    assert neither.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert neither.get(ONTARIO_TAX).value == D("1552.28")


def test_the_ontario_worksheet_reads_line_28_of_the_dependants_on428_not_line_98() -> None:
    # Same dependant, same taxable income: the T1 adds line 98 of their return (16129, giving
    # 6267.00), ON428 adds line 28 of theirs (15000, giving 5298.00).
    worksheet = return_ab()

    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("6267.00")
    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("5298.00")
    # A line 28 of 16129 would give the T1's figure's counterpart: 10298.00 + 16129 - 20000.
    same = return_ab(ontario_disability_dependants=((0, "0", "16129", "20000"),))
    assert same.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("6427.00")


def test_an_ontario_dependant_under_18_with_care_expenses_transfers_the_reduced_amount() -> None:
    # Care expenses of 5000: line 5 = 5000 - 3518.00 = 1482.00; line 6 = 6007.00 - 1482.00 =
    # 4525.00; line 7 = 10298.00 + 4525.00 = 14823.00; with no line 28 amount and no taxable
    # income line 11 = 14823.00, and line 12 is 14823.00.
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        ontario_disability_dependants=((1, "5000", "0", "0"),),
    )

    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("14823.00")
    assert worksheet.get(DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    # 12747 + 2202.75 + 787.20 + 14823.00.
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("30559.95")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert (
        "disability_transferred_amount: dependant 1: under 18: care expenses 5000 less threshold "
        "3518 = 1482; supplement 6007 less 1482 = 4525; base 10298 + 4525, at most 16305 = 14823; "
        "14823 + credit amounts 0 less taxable income 0 = 14823; "
        "the lesser of 14823 and 14823 = 14823 (half-up to 0.01)"
    ) in rendered


def test_two_ontario_dependants_with_a_disability_are_transferred_one_by_one_on_line_58480() -> (
    None
):
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        ontario_disability_dependants=((0, "0", "15000", "20000"), (1, "5000", "0", "0")),
    )

    # 5298.00 + 14823.00 = 20121.00.
    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("20121.00")
    # 12747 + 2202.75 + 787.20 + 20121.00.
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("35857.95")
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)
    assert "disability_transferred_amount: item 1 5298 + item 2 14823 = 20121" in rendered


def test_an_ontario_dependants_taxable_income_above_their_credits_transfers_nothing() -> None:
    # Line 9 = 10298.00 + 0; line 11 = 10298.00 - 20000 is negative, "0".
    worksheet = compute(
        "48000",
        (),
        "0",
        "0",
        "8640",
        "0",
        "0",
        ontario_disability_dependants=((0, "0", "0", "20000"),),
    )

    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")


def test_no_ontario_dependants_with_a_disability_transfer_nothing_on_line_58480() -> None:
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(ontario.DISABILITY_TRANSFERRED_AMOUNT).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")


def test_ontarios_ceiling_is_2885_not_the_federal_2834() -> None:
    # Employment income of 96000 gives a net income of 94926.00, and 3% of it is 2847.78: above
    # the federal ceiling of 2834 and below Ontario's 2885, so line 109 is 2834 and ON428 line
    # 40 is 2847.78.
    worksheet = compute("96000", (), "0", "0", "0", "0", "0", medical_expenses="5000")

    assert worksheet.get(NET_INCOME).value == D("94926.00")
    assert worksheet.get(MEDICAL_THRESHOLD).value == D("2834")
    assert worksheet.get(ontario.MEDICAL_THRESHOLD).value == D("2847.78")
    assert worksheet.get(MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("2166")
    assert worksheet.get(ontario.MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("2152.22")


def test_ontarios_threshold_on_line_40_stops_at_2885() -> None:
    worksheet = compute("115000", (), "0", "0", "0", "0", "0", medical_expenses="5000")

    assert worksheet.get(ontario.MEDICAL_NET_INCOME_SHARE).value > D("2885")
    assert worksheet.get(ontario.MEDICAL_THRESHOLD).value == D("2885")
    assert worksheet.get(ontario.MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("2115")


def test_ontario_caps_each_dependants_claim_at_15551_and_the_t1_does_not() -> None:
    # A dependant with no net income and expenses of 20000: the Federal Worksheet's line 3 is the
    # whole 20000, Worksheet ON428's line 3 is at most 15551.
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0", other_dependants=(("20000", "0"),))

    assert worksheet.get(OTHER_DEPENDANTS_MEDICAL).value == D("20000.00")
    assert worksheet.get(ontario.OTHER_DEPENDANTS_MEDICAL).value == D("15551.00")
    assert worksheet.get(ontario.MEDICAL_CLAIM).value == D("15551.00")
    assert worksheet.get(MEDICAL_CLAIM).value == D("20000.00")


def test_ontario_pooled_dependants_would_give_the_wrong_line_58729() -> None:
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

    assert separate.get(ontario.OTHER_DEPENDANTS_MEDICAL).value == D("2700.00")
    # 4000 - lesser(1500.00, 2885) = 2500.00, not 2700.00.
    assert pooled.get(ontario.OTHER_DEPENDANTS_MEDICAL).value == D("2500.00")


def test_no_medical_expenses_claim_nothing_on_line_58769() -> None:
    worksheet = compute("48000", (), "0", "0", "8640", "0", "0")

    assert worksheet.get(ontario.MEDICAL_EXPENSES_OVER_THRESHOLD).value == D("0")
    assert worksheet.get(ontario.OTHER_DEPENDANTS_MEDICAL).value == D("0")
    assert worksheet.get(ontario.MEDICAL_CLAIM).value == D("0")
    assert worksheet.get(ontario.NON_REFUNDABLE_CREDIT_AMOUNTS).value == D("15736.95")
