"""CA-ON 2025 end to end, Return A: return a trace 2."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import ArtifactKind
from tax_engine.domain.trace import (
    TimesCountLine,
)
from tax_engine.jurisdictions.ca.catalog import (
    AGE_AMOUNT_BEFORE_COUNT,
    CAREGIVER_AMOUNT,
    DISABILITY_TRANSFERRED_AMOUNT,
    MEDICAL_CLAIM,
    MEDICAL_NET_INCOME_SHARE,
    OTHER_DEPENDANTS_MEDICAL,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, return_a


def test_the_trace_explains_the_computation() -> None:
    worksheet = return_a()
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    def position(
        expected: str,
        amount: str,
        claimed: ArtifactKind[Decimal] | None = None,
        output: ArtifactKind[Decimal] | None = None,
    ) -> int:
        """The index of the one rendered line reading `expected` whose line has `amount`.

        A claimed line (an amount times a count) reads the same federally and for Ontario when the
        amounts are alike, so it is told apart by the kind of the amount it claims. Any other line
        that reads the same federally and for Ontario, such as the medical lines and the totals of
        items, is told apart by the kind it produces, `output`.
        """
        (found,) = [
            i
            for i, (text, line) in enumerate(zip(rendered, worksheet.trace, strict=True))
            if text == expected
            and line.amount == D(amount)
            and (
                claimed is None
                or (isinstance(line, TimesCountLine) and line.amount_kind is claimed)
            )
            and (output is None or getattr(line, "output", None) is output)
        ]
        return found

    support = position(
        "income_support_benefits: workers_compensation_benefits 0 + "
        "social_assistance_payments 0 + net_federal_supplements 0 = 0",
        "0",
    )
    net_signed = position(
        "net_income_signed: net_income_before_adjustments 115000 less social_benefits_repayment 0 "
        "= 115000",
        "115000",
    )
    net = position(
        "net_income: net_income_before_adjustments 115000 less social_benefits_repayment 0, "
        "not below 0 = 115000",
        "115000",
    )
    uccb_and_rdsp = position(
        "uccb_and_rdsp_income: universal_child_care_benefit 0 + rdsp_income 0 = 0", "0"
    )
    line_5 = position(
        "net_income_less_uccb_and_rdsp_income: net_income_before_adjustments_not_below_zero "
        "115000 less uccb_and_rdsp_income 0 = 115000",
        "115000",
    )
    repayments = position(
        "uccb_and_rdsp_income_repayments: uccb_repayment 0 + rdsp_income_repayment_checked 0 = 0",
        "0",
    )
    line_9 = position(
        "other_payments_limit_income: net_income_less_uccb_and_rdsp_income 115000 "
        "+ uccb_and_rdsp_income_repayments 0 = 115000",
        "115000",
    )
    after_limit = position(
        "other_payments_deduction_after_limit: other_payments_deduction_above_limit_checked 0, "
        "chosen as other_payments_worksheet_line_9_over_limit is 1",
        "0",
    )
    taxable_signed = position(
        "taxable_income_signed: net_income_signed 115000 less deductions_from_net_income 0 "
        "= 115000",
        "115000",
    )
    taxable = position(
        "taxable_income: net_income 115000 less deductions_from_net_income 0, not below 0 = 115000",
        "115000",
    )
    federal_column = position("26% on 250 over 114750 plus 20081.25", "20146.25")
    federal_basic = position(
        "federal_basic_tax on taxable_income 115000 (half-up to 0.01)", "20146.25"
    )
    federal_amount = position(
        "basic_personal_amount: 14538 plus 1591 less 0 for "
        "tosi_adjusted_net_income_not_below_zero 115000 over 177882 "
        "(range 75532), not below 14538 (half-up to 0.01)",
        "16129",
    )
    employment_sum = position(
        "canada_employment_amount_income: employment_income 110000 + "
        "other_employment_income 0 = 110000",
        "110000",
    )
    employment_amount = position(
        "canada_employment_amount: lesser of canada_employment_amount_income 110000 and 1471 "
        "(half-up to 0.01)",
        "1471",
    )
    position(
        "eligible_dependant_amount_basis: basic_personal_amount 16129 "
        "+ dependant_infirmity_supplement 0 = 16129",
        "16129",
    )
    federal_dependant = position(
        "eligible_dependant_amount_before_count: eligible_dependant_amount_basis 16129 "
        "less dependant_net_income 0, not below 0 = 16129",
        "16129",
    )
    federal_dependant_claimed = position(
        "eligible_dependant_amount: eligible_dependant_amount_before_count 16129 "
        "for each of 0 eligible_dependants_checked = 0",
        "0",
    )
    federal_caregiver = position("caregiver_amount: no items = 0", "0", output=CAREGIVER_AMOUNT)
    ontario_caregiver = position(
        "caregiver_amount: no items = 0", "0", output=ontario.CAREGIVER_AMOUNT
    )
    # The T1's line 31800 and ON428's line 58480 read alike when both lists are empty, so each
    # total is told apart by the kind it produces.
    disability_transfer = position(
        "disability_transferred_amount: no items = 0", "0", output=DISABILITY_TRANSFERRED_AMOUNT
    )
    ontario_disability_transfer = position(
        "disability_transferred_amount: no items = 0",
        "0",
        output=ontario.DISABILITY_TRANSFERRED_AMOUNT,
    )
    infirm_children = position(
        "infirm_children_amount: 2687 for each of 0 infirm_children = 0 (half-up to 0.01)", "0"
    )
    medical_share = position(
        "medical_net_income_share: 3% of net_income 115000 (half-up to 0.01)",
        "3450",
        output=MEDICAL_NET_INCOME_SHARE,
    )
    medical_threshold = position(
        "medical_threshold: lesser of medical_net_income_share 3450 and 2834 (half-up to 0.01)",
        "2834",
    )
    medical_over = position(
        "medical_expenses_over_threshold: medical_expenses 0 less medical_threshold 2834, "
        "not below 0 = 0",
        "0",
    )
    other_medical = position(
        "other_dependants_medical: no items = 0", "0", output=OTHER_DEPENDANTS_MEDICAL
    )
    medical_claim = position(
        "medical_claim: medical_expenses_over_threshold 0 + other_dependants_medical 0 = 0",
        "0",
        output=MEDICAL_CLAIM,
    )
    ontario_medical_share = position(
        "medical_net_income_share: 3% of net_income 115000 (half-up to 0.01)",
        "3450",
        output=ontario.MEDICAL_NET_INCOME_SHARE,
    )
    ontario_medical_threshold = position(
        "medical_threshold: lesser of medical_net_income_share 3450 and 2885 (half-up to 0.01)",
        "2885",
    )
    ontario_medical_over = position(
        "medical_expenses_over_threshold: medical_expenses 0 less medical_threshold 2885, "
        "not below 0 = 0",
        "0",
    )
    ontario_other_medical = position(
        "other_dependants_medical: no items = 0", "0", output=ontario.OTHER_DEPENDANTS_MEDICAL
    )
    ontario_medical_claim = position(
        "medical_claim: medical_expenses_over_threshold 0 + other_dependants_medical 0 = 0",
        "0",
        output=ontario.MEDICAL_CLAIM,
    )
    age_maximum = position("age_maximum: credit amount 9028 (half-up to 0.01)", "9028.00")
    age_threshold = position(
        "age_income_threshold: credit amount 45522 (half-up to 0.01)", "45522.00"
    )
    age_over_threshold = position(
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 115000 "
        "less age_income_threshold 45522, not below 0 = 69478",
        "69478",
    )
    age_reduction = position(
        "age_reduction: 15% of age_income_over_threshold 69478 (half-up to 0.01)", "10421.70"
    )
    age_before_count = position(
        "age_amount_before_count: age_maximum 9028 less age_reduction 10421.7, not below 0 = 0",
        "0",
    )
    age = position(
        "age_amount: age_amount_before_count 0 for each of 0 born_in_1960_or_earlier_checked = 0",
        "0",
        AGE_AMOUNT_BEFORE_COUNT,
    )
    spouse_supplement = position(
        "spouse_infirmity_supplement: 2687 for each of 0 spouse_caregiver_eligible_checked = 0 "
        "(half-up to 0.01)",
        "0",
    )
    spouse_basis = position(
        "spouse_amount_basis: basic_personal_amount 16129 + spouse_infirmity_supplement 0 = 16129",
        "16129",
    )
    spouse_before_count = position(
        "spouse_amount_before_count: spouse_amount_basis 16129 "
        "less spouse_net_income 0, not below 0 = 16129",
        "16129",
    )
    spouse = position(
        "spouse_amount: spouse_amount_before_count 16129 for each of 0 spouses_claimed_checked = 0",
        "0",
    )
    caregiver_base = position(
        "spouse_caregiver_base: credit amount 28798 (half-up to 0.01)", "28798.00"
    )
    caregiver_before_maximum = position(
        "spouse_caregiver_before_maximum: spouse_caregiver_base 28798 "
        "less spouse_net_income 0, not below 0 = 28798",
        "28798",
    )
    caregiver_limit = position(
        "spouse_caregiver_limit: lesser of spouse_caregiver_before_maximum 28798 and 8601 "
        "(half-up to 0.01)",
        "8601",
    )
    caregiver_before_count = position(
        "spouse_caregiver_amount_before_count: spouse_caregiver_limit 8601 "
        "less spouse_amount 0, not below 0 = 8601",
        "8601",
    )
    caregiver = position(
        "spouse_caregiver_amount: spouse_caregiver_amount_before_count 8601 "
        "for each of 0 spouse_caregiver_eligible_checked = 0",
        "0",
    )
    federal_amounts = position(
        "non_refundable_credit_amounts: basic_personal_amount 16129 "
        "+ age_amount 0 + spouse_amount 0 "
        "+ eligible_dependant_amount 0 + caregiver_amount_for_spouse_or_dependant 0 "
        "+ caregiver_amount 0 "
        "+ infirm_children_amount 0 "
        "+ cpp_base_contributions_on_return 3356.1 + "
        "cpp_base_contributions_on_self_employment_and_other_earnings 0 "
        "+ ei_premiums 1077.48 + ei_premiums_on_self_employment 0 "
        "+ volunteer_firefighters_credit 0 + search_and_rescue_credit 0 + "
        "canada_employment_amount 1471 + home_buyers_credit 0 + home_accessibility_credit 0 + "
        "adoption_credit 0 + pension_income_credit 0 + disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 "
        "+ student_loan_interest 0 + federal_tuition_amount 0 + "
        "tuition_transferred_from_child_checked 0 + "
        "amounts_transferred_from_spouse 0 + medical_claim 0 = 22033.58",
        "22033.58",
    )
    federal_credit = position(
        "credit_amounts_at_credit_rate: 14.5% of non_refundable_credit_amounts 22033.58 "
        "(half-up to 0.01)",
        "3194.87",
    )
    federal_after = position(
        "federal_tax_after_credits: federal_tax_with_split_income 20146.25 "
        "less credits_against_basic_federal_tax 3194.87, not below 0 = 16951.38",
        "16951.38",
    )
    ontario_column = position("11.16% on 9225 over 105775 plus 7510.09", "8539.60")
    ontario_basic = position(
        "ontario_basic_tax on taxable_income 115000 (half-up to 0.01)", "8539.60"
    )
    ontario_amount = position(
        "basic_personal_amount: credit amount 12747 (half-up to 0.01)", "12747"
    )
    ontario_base = position(
        "eligible_dependant_base: credit amount 11905 (half-up to 0.01)", "11905"
    )
    ontario_before_maximum = position(
        "eligible_dependant_amount_before_maximum: eligible_dependant_base 11905 "
        "less dependant_net_income 0, not below 0 = 11905",
        "11905",
    )
    ontario_dependant = position(
        "eligible_dependant_amount_before_count: lesser of "
        "eligible_dependant_amount_before_maximum 11905 and 10823 (half-up to 0.01)",
        "10823",
    )
    ontario_dependant_claimed = position(
        "eligible_dependant_amount: eligible_dependant_amount_before_count 10823 "
        "for each of 0 eligible_dependants_checked = 0",
        "0",
    )
    ontario_age_maximum = position("age_maximum: credit amount 6223 (half-up to 0.01)", "6223.00")
    ontario_age_threshold = position(
        "age_income_threshold: credit amount 46330 (half-up to 0.01)", "46330.00"
    )
    ontario_age_over_threshold = position(
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 115000 "
        "less age_income_threshold 46330, not below 0 = 68670",
        "68670",
    )
    ontario_age_reduction = position(
        "age_reduction: 15% of age_income_over_threshold 68670 (half-up to 0.01)", "10300.50"
    )
    ontario_age_before_count = position(
        "age_amount_before_count: age_maximum 6223 less age_reduction 10300.5, not below 0 = 0",
        "0",
    )
    ontario_age = position(
        "age_amount: age_amount_before_count 0 for each of 0 born_in_1960_or_earlier_checked = 0",
        "0",
        ontario.AGE_AMOUNT_BEFORE_COUNT,
    )
    ontario_spouse_base = position("spouse_base: credit amount 11905 (half-up to 0.01)", "11905")
    ontario_spouse_before_maximum = position(
        "spouse_amount_before_maximum: spouse_base 11905 "
        "less spouse_net_income 0, not below 0 = 11905",
        "11905",
    )
    ontario_spouse_before_count = position(
        "spouse_amount_before_count: lesser of spouse_amount_before_maximum 11905 and 10823 "
        "(half-up to 0.01)",
        "10823",
    )
    ontario_spouse = position(
        "spouse_amount: spouse_amount_before_count 10823 for each of 0 spouses_claimed_checked = 0",
        "0",
    )
    ontario_amounts = position(
        "non_refundable_credit_amounts: basic_personal_amount 12747 "
        "+ age_amount 0 + spouse_amount 0 + eligible_dependant_amount 0 "
        "+ caregiver_amount 0 + cpp_base_contributions_on_return 3356.1 "
        "+ cpp_base_contributions_on_self_employment_and_other_earnings 0 + ei_premiums 1077.48 "
        "+ ei_premiums_on_self_employment 0 + adoption_credit 0 + pension_income_credit 0 "
        "+ disability_amount_for_self 0 "
        "+ disability_transferred_amount 0 "
        "+ student_loan_interest 0 + unused_tuition_claimed 0 "
        "+ amounts_transferred_from_spouse 0 "
        "+ medical_claim 0 = 17180.58",
        "17180.58",
    )
    ontario_credit = position(
        "credit_amounts_at_credit_rate: 5.05% of non_refundable_credit_amounts 17180.58 "
        "(half-up to 0.01)",
        "867.62",
    )
    ontario_first_tier_credit = position(
        "donations_first_tier_credit: 5.05% of donations_first_tier 0 (half-up to 0.01)", "0"
    )
    ontario_over_first_tier_credit = position(
        "donations_over_first_tier_credit: 11.16% of donations_over_first_tier 0 (half-up to 0.01)",
        "0",
    )
    ontario_donations_credit = position(
        "donations_and_gifts_credit: donations_first_tier_credit 0 "
        "+ donations_over_first_tier_credit 0 = 0",
        "0",
    )
    ontario_line_50 = position(
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 867.62 "
        "+ donations_and_gifts_credit 0 = 867.62",
        "867.62",
    )
    ontario_after = position(
        "ontario_tax_after_credits: ontario_basic_tax 8539.6 "
        "less non_refundable_tax_credits 867.62, not below 0 = 7671.98",
        "7671.98",
    )
    with_split_income = position(
        "ontario_tax_with_split_income: ontario_tax_after_credits 7671.98 "
        "+ ontario_tax_on_split_income 0 = 7671.98",
        "7671.98",
    )
    carryover_credit = position(
        "minimum_tax_carryover_credit: 24.63% of amt_minimum_tax_carryover_applied 0 "
        "(half-up to 0.01)",
        "0",
    )
    carryover_applied = position(
        "ontario_minimum_tax_carryover_applied: lesser of ontario_tax_less_dividend_credit "
        "7671.98 and minimum_tax_carryover_credit 0 = 0",
        "0",
    )
    after_carryover = position(
        "ontario_tax_after_minimum_tax_carryover: ontario_tax_with_split_income 7671.98 "
        "less ontario_minimum_tax_carryover_applied 0, not below 0 = 7671.98",
        "7671.98",
    )
    surtax_base = position(
        "ontario_surtax_base: ontario_tax_after_minimum_tax_carryover 7671.98 "
        "less ontario_tax_on_split_income_for_surtax 0, not below 0 = 7671.98",
        "7671.98",
    )
    surtax_first = position(
        "ontario_surtax: 20% of ontario_surtax_base 7671.98 over 5710 (half-up to 0.01)",
        "392.40",
    )
    surtax_second = position(
        "ontario_surtax: 36% of ontario_surtax_base 7671.98 over 7307 (half-up to 0.01)",
        "131.39",
    )
    with_surtax = position(
        "ontario_tax_with_surtax: ontario_tax_after_minimum_tax_carryover 7671.98 "
        "+ ontario_surtax 523.79 = 8195.77",
        "8195.77",
    )
    worksheet_line_1 = position(
        "worksheet_on428_line_1: 24.63% of amt_alternative_minimum_tax_payable 0 (half-up to 0.01)",
        "0",
    )
    worksheet_line_2 = position(
        "worksheet_on428_line_2: ontario_surtax_base 7671.98 = 7671.98", "7671.98"
    )
    worksheet_line_3 = position(
        "worksheet_on428_line_3: worksheet_on428_line_1 0 + worksheet_on428_line_2 7671.98 "
        "= 7671.98",
        "7671.98",
    )
    worksheet_line_6_first = position(
        "worksheet_on428_line_6: 20% of worksheet_on428_line_3 7671.98 over 5710 (half-up to 0.01)",
        "392.40",
    )
    worksheet_line_6_second = position(
        "worksheet_on428_line_6: 36% of worksheet_on428_line_3 7671.98 over 7307 (half-up to 0.01)",
        "131.39",
    )
    worksheet_line_7 = position("worksheet_on428_line_7: ontario_surtax 523.79 = 523.79", "523.79")
    worksheet_line_8 = position(
        "worksheet_on428_line_8: worksheet_on428_line_6 523.79 less worksheet_on428_line_7 "
        "523.79 = 0",
        "0",
    )
    line_72 = position(
        "ontario_minimum_tax: worksheet_on428_line_1 0 + worksheet_on428_line_8 0 = 0", "0"
    )
    dividend_a = position("dividends_amount_a: taxable_dividends 0 = 0", "0")
    dividend_b = position("dividends_amount_b: taxable_dividends_other_than_eligible 0 = 0", "0")
    dividend_other = position(
        "other_dividends_credit: 2.9863% of dividends_amount_b 0 (half-up to 0.01)", "0"
    )
    dividend_eligible = position(
        "eligible_dividends_credit: 10% of dividends_amount_a_less_b 0 (half-up to 0.01)", "0"
    )
    dividend_credit = position(
        "dividend_tax_credit: other_dividends_credit 0 + eligible_dividends_credit 0 = 0", "0"
    )
    line_56 = position(
        "ontario_tax_before_dividend_credit: ontario_tax_after_credits 7671.98 = 7671.98",
        "7671.98",
    )
    line_58 = position(
        "ontario_tax_less_dividend_credit: ontario_tax_before_dividend_credit 7671.98 "
        "less dividend_tax_credit 0, not below 0 = 7671.98",
        "7671.98",
    )
    line_70 = position("dividend_credit_from_line_57: dividend_tax_credit 0 = 0", "0")
    line_71 = position(
        "ontario_tax_after_dividend_credit: ontario_tax_with_surtax 8195.77 "
        "less dividend_credit_from_line_57 0, not below 0 = 8195.77",
        "8195.77",
    )
    gate_conditions = [
        position(
            f'tax_reduction_claimable: condition {number} "{text}": {kind} 0, does not apply', "0"
        )
        for number, text, kind in (
            (
                1,
                "You were not a resident of Canada at the beginning of the year",
                "not_resident_of_canada_at_start_of_year_checked",
            ),
            (
                2,
                "You were not a resident of Ontario on December 31, 2025",
                "not_resident_of_ontario_at_year_end_checked",
            ),
            (3, "There is an amount on line 72", "ontario_minimum_tax"),
            (4, "You were bankrupt at any time in 2025", "bankrupt_in_year_checked"),
            (
                5,
                "Your return is filed for you by a trustee in bankruptcy",
                "return_filed_by_trustee_in_bankruptcy_checked",
            ),
            (
                6,
                "You are choosing not to claim an Ontario tax reduction",
                "not_claiming_ontario_tax_reduction_checked",
            ),
        )
    ]
    gate = position("tax_reduction_claimable: no condition applies, so 1", "1")
    reduction_basic = position(
        "tax_reduction_basic: credit amount 294 (half-up to 0.01)",
        "294.00",
    )
    children_before_rule = position(
        "tax_reduction_for_children_before_spouse_rule: 544 for each of 0 dependent_children = 0 "
        "(half-up to 0.01)",
        "0",
    )
    dependants_before_rule = position(
        "tax_reduction_for_dependants_before_spouse_rule: 544 for each of 0 dependants = 0 "
        "(half-up to 0.01)",
        "0",
    )
    spouse_rule_condition = position(
        'tax_reduction_amounts_claimable: condition 1 "If you had a spouse or common-law partner '
        "on December 31, 2025, only the individual with the higher net income can claim the "
        'amounts on lines 75 and 76.": spouse_or_common_law_partner_on_december_31_total 0, '
        "net_income 115000, spouse_net_income 0, net_income 115000, spouse_net_income 0, "
        "spouse_or_common_law_partner_on_december_31_total 0, net_income 115000, "
        "spouse_net_income 0, "
        "claims_tax_reduction_amounts_at_equal_net_income_checked 0, applies",
        "1",
    )
    spouse_rule = position("tax_reduction_amounts_claimable: condition 1 applies, so 1", "1")
    line_73 = position(
        "ontario_tax_before_reduction: ontario_tax_after_dividend_credit 8195.77 "
        "+ ontario_minimum_tax 0 = 8195.77",
        "8195.77",
    )
    reduction_children = position(
        "tax_reduction_for_children: tax_reduction_for_children_before_spouse_rule 0 "
        "for each of 1 tax_reduction_amounts_claimable = 0",
        "0",
    )
    reduction_dependants = position(
        "tax_reduction_for_dependants: tax_reduction_for_dependants_before_spouse_rule 0 "
        "for each of 1 tax_reduction_amounts_claimable = 0",
        "0",
    )
    reduction_amounts = position(
        "tax_reduction_amounts: tax_reduction_basic 294 + tax_reduction_for_children 0 "
        "+ tax_reduction_for_dependants 0 = 294",
        "294.00",
    )
    reduction_before_conditions = position(
        "ontario_tax_reduction_before_conditions: 2 × tax_reduction_amounts 294 "
        "over ontario_tax_before_reduction 8195.77, not below 0 (half-up to 0.01)",
        "0",
    )
    reduction = position(
        "ontario_tax_reduction: ontario_tax_reduction_before_conditions 0 "
        "for each of 1 tax_reduction_claimable = 0",
        "0",
    )
    after_reduction = position(
        "ontario_tax_after_reduction: ontario_tax_before_reduction 8195.77 "
        "less ontario_tax_reduction 0, not below 0 = 8195.77",
        "8195.77",
    )
    lift_sum = position(
        "lift_employment_income: employment_income 110000 + other_employment_income 0 = 110000",
        "110000",
    )
    lift_before_maximum = position(
        "lift_credit_before_maximum: 5.05% of lift_employment_income 110000 (half-up to 0.01)",
        "5555",
    )
    lift_maximum = position(
        "lift_maximum_credit: lesser of lift_credit_before_maximum 5555 and 875 (half-up to 0.01)",
        "875",
    )
    lift_net = position(
        "lift_net_income_and_repayments: tosi_adjusted_net_income 115000 "
        "+ uccb_repayment 0 + rdsp_income_repayment_checked 0 = 115000",
        "115000",
    )
    lift_uccb_and_rdsp = position(
        "lift_uccb_and_rdsp_income: universal_child_care_benefit 0 + rdsp_income 0 = 0", "0"
    )
    lift_adjusted = position(
        "lift_adjusted_net_income: lift_net_income_and_repayments 115000 "
        "less lift_uccb_and_rdsp_income 0, not below 0 = 115000",
        "115000",
    )
    lift_reduction = position(
        "lift_reduction: 5% of lift_adjusted_net_income 115000 over 32500 (half-up to 0.01)",
        "4125",
    )
    lift_single = position(
        "lift_credit_single: lift_maximum_credit 875 less lift_reduction 4125, not below 0 = 0",
        "0",
    )
    lift_spouse_net = position(
        "lift_spouse_net_income_and_repayments: spouse_net_income_before_adjustments 0 "
        "+ spouse_uccb_repayment 0 + spouse_rdsp_income_repayment 0 = 0",
        "0",
    )
    lift_spouse_uccb_and_rdsp = position(
        "lift_spouse_uccb_and_rdsp_income: spouse_universal_child_care_benefit 0 "
        "+ spouse_rdsp_income 0 = 0",
        "0",
    )
    lift_spouse_adjusted = position(
        "lift_spouse_adjusted_net_income: lift_spouse_net_income_and_repayments 0 "
        "less lift_spouse_uccb_and_rdsp_income 0, not below 0 = 0",
        "0",
    )
    lift_individual_threshold = position(
        "lift_individual_income_threshold: credit amount 32500 (half-up to 0.01)", "32500.00"
    )
    lift_excess_individual = position(
        "lift_excess_over_individual_threshold: lift_adjusted_net_income 115000 "
        "less lift_individual_income_threshold 32500, not below 0 = 82500",
        "82500",
    )
    lift_family_net = position(
        "lift_family_net_income: lift_adjusted_net_income 115000 "
        "+ lift_spouse_adjusted_net_income 0 = 115000",
        "115000",
    )
    lift_family_threshold = position(
        "lift_family_income_threshold: credit amount 65000 (half-up to 0.01)", "65000.00"
    )
    lift_excess_family = position(
        "lift_excess_over_family_threshold: lift_family_net_income 115000 "
        "less lift_family_income_threshold 65000, not below 0 = 50000",
        "50000",
    )
    lift_greater = position(
        "lift_greater_excess: greater of lift_excess_over_individual_threshold 82500 "
        "and lift_excess_over_family_threshold 50000 = 82500",
        "82500",
    )
    lift_family_reduction = position(
        "lift_family_reduction: 5% of lift_greater_excess 82500 (half-up to 0.01)", "4125"
    )
    lift_with_spouse = position(
        "lift_credit_with_spouse: lift_maximum_credit 875 less lift_family_reduction 4125, "
        "not below 0 = 0",
        "0",
    )
    lift = position(
        "lift_credit: lift_credit_single 0, chosen as "
        "spouse_or_common_law_partner_on_december_31_total is 0",
        "0",
    )
    after_lift = position(
        "ontario_tax_after_lift_credit: ontario_tax_after_foreign_tax_credit 8195.77 "
        "less lift_credit 0, not below 0 = 8195.77",
        "8195.77",
    )
    food_applied = position(
        "community_food_program_donations_applied: community_food_program_donations 0, "
        "at most donations_and_gifts_total 0",
        "0",
    )
    food_credit = position(
        "community_food_program_credit: 25% of community_food_program_donations_applied 0 "
        "(half-up to 0.01)",
        "0",
    )
    after_food = position(
        "ontario_tax_after_food_credit: ontario_tax_after_lift_credit 8195.77 "
        "less community_food_program_credit 0, not below 0 = 8195.77",
        "8195.77",
    )
    health_income = position(
        "health_premium_income: taxable_income 115000 + total_split_income 0 = 115000",
        "115000",
    )
    premium_first = position(
        "ontario_health_premium: 6% of health_premium_income 115000 over 20000, at most 300 "
        "(half-up to 0.01)",
        "300",
    )
    premium_second = position(
        "ontario_health_premium: 6% of health_premium_income 115000 over 36000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    premium_third = position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 48000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    premium_fourth = position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 72000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    premium_fifth = position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 200000, at most 150 "
        "(half-up to 0.01)",
        "0",
    )
    line_52 = position(
        "split_income_line_52: greater of split_income_line_50 0 "
        "and ontario_tax_after_food_credit 8195.77 = 8195.77",
        "8195.77",
    )
    ontario_tax = position(
        "ontario_tax: split_income_line_52 8195.77 + ontario_health_premium 750 = 8945.77",
        "8945.77",
    )
    recapture_at_15 = position(
        "itc_recapture_at_15_percent: 15% of itc_recapture_expenditure_at_15_percent 0 "
        "(half-up to 0.01)",
        "0",
    )
    recapture_at_20 = position(
        "itc_recapture_at_20_percent: 20% of itc_recapture_expenditure_at_20_percent 0 "
        "(half-up to 0.01)",
        "0",
    )
    recapture = position(
        "itc_recapture: itc_recapture_at_15_percent 0 + itc_recapture_at_20_percent 0 = 0", "0"
    )
    with_recapture = position(
        "federal_tax_with_itc_recapture: federal_tax_less_foreign_tax_credit 16951.38 "
        "+ itc_recapture 0 = 16951.38",
        "16951.38",
    )
    labour_before_maximum = position(
        "labour_sponsored_funds_credit_before_maximum: 15% of labour_sponsored_funds_net_cost 0 "
        "(half-up to 0.01)",
        "0",
    )
    labour_credit = position(
        "labour_sponsored_funds_credit: lesser of labour_sponsored_funds_credit_before_maximum 0 "
        "and 750 (half-up to 0.01)",
        "0",
    )
    position(
        "federal_tax: federal_tax_with_itc_recapture 16951.38 "
        "less federal_logging_tax_credit 0, not below 0 = 16951.38",
        "16951.38",
    )
    less_credits = position(
        "federal_tax_less_credits: federal_tax 16951.38 "
        "less credits_against_federal_tax 0, not below 0 = 16951.38",
        "16951.38",
    )
    aips_counted = position(
        "resp_aips_contributions_counted: lesser of resp_aips_received_part_a 0 "
        "and resp_aips_rrsp_contributions 0 = 0",
        "0",
    )
    aips_limit = position(
        "resp_aips_lifetime_limit: credit amount 50000 (half-up to 0.01)", "50000"
    )
    aips_remaining = position(
        "resp_aips_limit_remaining: resp_aips_lifetime_limit 50000 "
        "less resp_aips_reduction_used_in_previous_years 0 = 50000",
        "50000",
    )
    aips_reduction = position(
        "resp_aips_reduction: lesser of resp_aips_contributions_counted 0 "
        "and resp_aips_limit_remaining 50000 = 0",
        "0",
    )
    aips_subject = position(
        "resp_aips_subject_to_tax: resp_aips_received_part_a 0 less resp_aips_reduction 0 = 0", "0"
    )
    aips_part_a = position(
        "resp_aips_part_a_tax: 20% of resp_aips_subject_to_tax 0 (half-up to 0.01)", "0"
    )
    aips_part_b = position(
        "resp_aips_part_b_tax: 20% of resp_aips_received_part_b 0 (half-up to 0.01)", "0"
    )
    aips_tax = position(
        "resp_aips_additional_tax: resp_aips_part_b_tax 0, chosen as "
        "resp_aips_part_a_applies_checked is 0",
        "0",
    )
    special = position(
        "special_taxes: resp_aips_additional_tax 0 + rl_10_labour_sponsored_fund_amount 0 "
        "+ rc359_tax_total 0 = 0",
        "0",
    )
    net_federal = position(
        "net_federal_tax: split_income_line_30 16951.38 + special_taxes 0 = 16951.38",
        "16951.38",
    )
    payable = position(
        "total_payable: net_federal_tax 16951.38 + "
        "cpp_payable_on_self_employment_and_other_earnings 0 "
        "+ ei_payable_on_self_employment 0 + social_benefits_repayment_payable 0 "
        "+ ontario_tax 8945.77 = 25897.15",
        "25897.15",
    )
    position(
        "cwb_employment_income: employment_income 110000 + other_employment_income 0 = 110000",
        "110000",
    )
    working = position(
        "working_income: cwb_employment_income 110000 + taxable_scholarships 0 + "
        "medical_supplement_self_employment_income 0 + cwb_tax_exempt_working_income 0 = 110000",
        "110000",
    )
    position(
        "cwb_family_net_income_line_10: tosi_adjusted_net_income 115000 + "
        "uccb_and_rdsp_income_repayments 0 + cwb_tax_exempt_net_income 0 = 115000",
        "115000",
    )
    position(
        "cwb_family_net_income_line_12: cwb_family_net_income_line_10 115000 "
        "less uccb_and_rdsp_income 0, not below 0 = 115000",
        "115000",
    )
    family_net = position(
        "adjusted_family_net_income: cwb_family_net_income_line_13 115000 less "
        "cwb_secondary_earner_exemption 0 = 115000",
        "115000",
    )
    cwb_before_reduction = position(
        "cwb_before_reduction_without_dependant: 27% of cwb_family_working_income 110000 "
        "over 3000, "
        "at most 1633 (half-up to 0.01)",
        "1633",
    )
    cwb_reduction = position(
        "cwb_reduction_without_dependant: 15% of adjusted_family_net_income 115000 over 26855 "
        "(half-up to 0.01)",
        "13221.75",
    )
    cwb_without = position(
        "canada_workers_benefit_without_dependant: cwb_before_reduction_without_dependant 1633 "
        "less cwb_reduction_without_dependant 13221.75, not below 0 = 0",
        "0",
    )
    cwb_before_reduction_dependant = position(
        "cwb_before_reduction_with_dependant: 27% of cwb_family_working_income 110000 "
        "over 3000, "
        "at most 2813 (half-up to 0.01)",
        "2813",
    )
    cwb_reduction_dependant = position(
        "cwb_reduction_with_dependant: 15% of adjusted_family_net_income 115000 over 30639 "
        "(half-up to 0.01)",
        "12654.15",
    )
    cwb_with = position(
        "canada_workers_benefit_with_dependant: cwb_before_reduction_with_dependant 2813 "
        "less cwb_reduction_with_dependant 12654.15, not below 0 = 0",
        "0",
    )
    cwb = position(
        "canada_workers_benefit_line_28: cwb_line_28_by_spouse 0, "
        "chosen as cwb_eligible_dependants_checked is 0",
        "0",
    )
    fertility_before_maximum = position(
        "fertility_credit_before_maximum: 25% of fertility_expenses 0 (half-up to 0.01)", "0"
    )
    fertility = position(
        "fertility_credit: lesser of fertility_credit_before_maximum 0 and 5000 (half-up to 0.01)",
        "0",
    )
    child_care_adjusted = position(
        "care_adjusted_income: tosi_adjusted_net_income 115000 + child_care_expenses 0 "
        "+ social_benefits_repayment 0, not below 0 = 115000",
        "115000",
    )
    child_care_family = position(
        "care_family_adjusted_income: care_adjusted_income 115000 "
        "+ care_supporting_persons_adjusted_income 0 = 115000",
        "115000",
    )
    child_care_rate = position(
        "care_credit_percentage: care_family_adjusted_income 115000, "
        "more than 114000 but not more than 117600: 19%",
        "0.19",
    )
    child_care_credit = position(
        "care_credit: care_credit_percentage 19% of child_care_expenses 0 (half-up to 0.01)", "0"
    )
    care_before_maximum = position(
        "seniors_care_before_maximum: 25% of medical_claim 0 (half-up to 0.01)", "0"
    )
    care_amount = position(
        "seniors_care_amount: lesser of seniors_care_before_maximum 0 and 1500 (half-up to 0.01)",
        "0",
    )
    care_family_net_income = position(
        "seniors_care_family_net_income: tosi_adjusted_net_income_not_below_zero 115000 "
        "+ spouse_net_income 0 = 115000",
        "115000",
    )
    care_base = position("seniors_care_base_amount: credit amount 35000 (half-up to 0.01)", "35000")
    care_over_base = position(
        "seniors_care_income_over_base: seniors_care_family_net_income 115000 "
        "less seniors_care_base_amount 35000, not below 0 = 80000",
        "80000",
    )
    care_reduction = position(
        "seniors_care_reduction: 5% of seniors_care_income_over_base 80000 (half-up to 0.01)",
        "4000",
    )
    care_before_claim = position(
        "seniors_care_before_claim: seniors_care_amount 0 "
        "less seniors_care_reduction 4000, not below 0 = 0",
        "0",
    )
    care_credit = position(
        "seniors_care_credit: seniors_care_before_claim 0 "
        "for each of 0 claims_seniors_care_credit_checked = 0",
        "0",
    )
    transit_paid = position(
        "seniors_transit_amount_paid_checked: seniors_transit_paid 0, at most "
        "seniors_transit_maximum 3000",
        "0",
    )
    transit = position(
        "seniors_transit_credit: 15% of seniors_transit_amount_paid_checked 0 (half-up to 0.01)",
        "0",
    )
    flow_through_expenses = position("flow_through_share_expenses: no items = 0", "0")
    position(
        'flow_through_share_claimable: condition 1 "You were not a resident of Ontario on the '
        'last day of the tax year": not_resident_of_ontario_at_year_end_checked 0, does not apply',
        "0",
    )
    position("flow_through_share_claimable: no condition applies, so 1", "1")
    flow_through = position(
        "flow_through_share_credit: 5% of flow_through_share_expenses_claimed 0 (half-up to 0.01)",
        "0",
    )
    ontario_credits_subtotal = position(
        "ontario_credits_subtotal: fertility_credit 0 + care_credit 0 + seniors_care_credit 0 "
        "+ seniors_transit_credit 0 + political_credit 0 + flow_through_share_credit 0 = 0",
        "0",
    )
    coop_threshold = position(
        "coop_education_payroll_threshold: credit amount 400000 (half-up to 0.01)", "400000"
    )
    coop_over_threshold = position(
        "coop_education_payroll_over_threshold: coop_education_payroll 0 "
        "less coop_education_payroll_threshold 400000, not below 0 = 0",
        "0",
    )
    coop_range = position(
        "coop_education_payroll_range: credit amount 200000 (half-up to 0.01)", "200000"
    )
    coop_phase_out = position(
        "coop_education_phase_out_share: coop_education_payroll_over_threshold 0 "
        "divided by coop_education_payroll_range 200000 = 0",
        "0",
    )
    coop_full_share = position("coop_education_full_share: credit amount 1 (half-up to 0.01)", "1")
    coop_remaining = position(
        "coop_education_remaining_share: coop_education_full_share 1 "
        "less coop_education_phase_out_share 0, not below 0 = 1",
        "1",
    )
    coop_credit = position("coop_education_credit: no items = 0", "0")
    coop_count = position(
        "coop_education_placement_count: no items in coop_education_placements = 0", "0"
    )
    ontario_credits = position(
        "ontario_credits: ontario_credits_subtotal 0 + coop_education_credit 0 = 0", "0"
    )
    provincial = position("provincial_credits: ontario_credits 0 = 0", "0")
    educator_expenses = position(
        "educator_supplies_expenses_at_most_maximum: lesser of educator_supplies_expenses 0 "
        "and 1000 (half-up to 0.01)",
        "0",
    )
    educator_credit = position(
        "educator_school_supply_credit: 25% of educator_supplies_expenses_at_most_maximum 0 "
        "(half-up to 0.01)",
        "0",
    )
    credits = position(
        "total_credits: income_tax_deducted_after_election 25000 + cpp_overpayment 0 "
        "+ ei_overpayment 0 "
        "+ refundable_medical_expense_supplement 0 "
        "+ canada_workers_benefit 0 "
        "+ canada_training_credit 0 + multigenerational_home_renovation_credit 0 "
        "+ investment_tax_credit_refund 0 + part_xii_2_tax_credit 0 + "
        "employee_and_partner_gst_hst_rebate 0 "
        "+ educator_school_supply_credit 0 + journalism_labour_tax_credit 0 "
        "+ fuel_charge_credit_farmers_total 0 "
        "+ tax_paid_by_instalments 0 + provincial_credits 0 = 25000",
        "25000",
    )
    balance = position(
        "refund_or_balance_owing: total_payable 25897.15 less total_credits 25000 = 897.15",
        "897.15",
    )
    refund = position(
        "refund: total_credits 25000 less total_payable 25897.15, not below 0 = 0", "0"
    )
    refund_before_donation = position("refund_before_donation: refund 0 = 0", "0")
    donation_checked = position(
        "opportunities_fund_donation_checked: opportunities_fund_donation 0, "
        "at most refund_before_donation 0",
        "0",
    )
    net_refund = position(
        "net_refund: refund_before_donation 0 less opportunities_fund_donation_checked 0 = 0", "0"
    )
    depreciable_proceeds_or_cost = position(
        "depreciable_gift_proceeds_or_cost: lesser of depreciable_gift_net_proceeds 0 "
        "and depreciable_gift_capital_cost 0 = 0",
        "0",
    )
    depreciable_gifts = position(
        "depreciable_gifts: lesser of depreciable_gift_recaptured_depreciation 0 "
        "and depreciable_gift_proceeds_or_cost 0 = 0",
        "0",
    )
    capital_gifts = position(
        "capital_property_gifts: capital_gift_taxable_gains 0 "
        "less capital_gift_gains_deduction_checked 0 = 0",
        "0",
    )
    donations_total = position(
        "total_charitable_donations: charitable_donations 0 + government_donations 0 "
        "+ university_donations_outside_canada 0 + foreign_charity_donations 0 = 0",
        "0",
    )
    limit_on_net_income = position(
        "donation_limit_on_net_income: 75% of net_income 115000 (half-up to 0.01)", "86250"
    )
    capital_gifts_total = position(
        "capital_gifts_total: depreciable_gifts 0 + capital_property_gifts 0 = 0", "0"
    )
    capital_gifts_addition = position(
        "capital_gifts_limit_addition: 25% of capital_gifts_total 0 (half-up to 0.01)", "0"
    )
    limit_with_gifts = position(
        "donation_limit_with_capital_gifts: donation_limit_on_net_income 86250 "
        "+ capital_gifts_limit_addition 0 = 86250",
        "86250",
    )
    donations_limit = position(
        "charitable_donations_limit: lesser of net_income 115000 "
        "and donation_limit_with_capital_gifts 86250 = 86250",
        "86250",
    )
    donations_claimed = position(
        "charitable_donations_claimed: lesser of total_charitable_donations 0 "
        "and charitable_donations_limit 86250 = 0",
        "0",
    )
    donations_and_gifts = position(
        "donations_and_gifts_total: charitable_donations_claimed 0 "
        "+ ecological_and_cultural_gifts 0 = 0",
        "0",
    )
    first_tier_maximum = position(
        "donation_first_tier_maximum: credit amount 200 (half-up to 0.01)", "200"
    )
    first_tier = position(
        "donations_first_tier: lesser of donations_and_gifts_total 0 "
        "and donation_first_tier_maximum 200 = 0",
        "0",
    )
    over_first_tier = position(
        "donations_over_first_tier: donations_and_gifts_total 0 less donations_first_tier 0 = 0",
        "0",
    )
    over_first_tier_after_2016 = position(
        "donations_over_first_tier_after_2016_gifts: donations_over_first_tier 0 "
        "less ecological_gifts_before_2016 0, not below 0 = 0",
        "0",
    )
    high_income_threshold = position(
        "donation_high_income_threshold: credit amount 253414 (half-up to 0.01)", "253414"
    )
    taxable_over_threshold = position(
        "taxable_income_over_donation_threshold: taxable_income 115000 "
        "less donation_high_income_threshold 253414, not below 0 = 0",
        "0",
    )
    high_income_donations = position(
        "high_income_donations: lesser of donations_over_first_tier_after_2016_gifts 0 "
        "and taxable_income_over_donation_threshold 0 = 0",
        "0",
    )
    high_income_credit = position(
        "high_income_donation_credit: 33% of high_income_donations 0 (half-up to 0.01)", "0"
    )
    regular_donations = position(
        "regular_rate_donations: donations_over_first_tier 0 less high_income_donations 0 = 0",
        "0",
    )
    regular_credit = position(
        "regular_rate_donation_credit: 29% of regular_rate_donations 0 (half-up to 0.01)", "0"
    )
    first_tier_credit = position(
        "first_tier_donation_credit: 14.5% of donations_first_tier 0 (half-up to 0.01)", "0"
    )
    donations_credit = position(
        "donations_and_gifts_credit: high_income_donation_credit 0 "
        "+ regular_rate_donation_credit 0 + first_tier_donation_credit 0 = 0",
        "0",
    )
    top_up_base = position(
        "top_up_credits_base: credit_amounts_at_credit_rate 3194.87 "
        "+ first_tier_donation_credit 0 = 3194.87",
        "3194.87",
    )
    top_up_threshold = position(
        "top_up_threshold: credit amount 8319.38 (half-up to 0.01)", "8319.38"
    )
    top_up_excess = position(
        "top_up_excess: top_up_credits_base 3194.87 less top_up_threshold 8319.38, not below 0 = 0",
        "0",
    )
    top_up_credit = position("top_up_tax_credit: 3.45% of top_up_excess 0 (half-up to 0.01)", "0")
    federal_credits = position(
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 3194.87 "
        "+ donations_and_gifts_credit 0 + top_up_tax_credit 0 = 3194.87",
        "3194.87",
    )
    assert uccb_and_rdsp < line_5
    assert repayments < line_9
    assert support < after_limit
    assert taxable < federal_column < federal_basic < federal_after
    assert taxable < ontario_column < ontario_basic
    assert ontario_basic < ontario_after
    assert federal_amount < federal_amounts < federal_credit < federal_after
    assert depreciable_proceeds_or_cost < depreciable_gifts < capital_gifts_total
    assert capital_gifts < capital_gifts_total < capital_gifts_addition < limit_with_gifts
    assert net < limit_on_net_income < limit_with_gifts < donations_limit < donations_claimed
    assert donations_total < donations_claimed < donations_and_gifts
    assert first_tier_maximum < first_tier < over_first_tier < over_first_tier_after_2016
    assert donations_and_gifts < first_tier
    assert taxable < taxable_over_threshold
    assert high_income_threshold < taxable_over_threshold < high_income_donations
    assert over_first_tier_after_2016 < high_income_donations < high_income_credit
    assert high_income_donations < regular_donations < regular_credit
    assert first_tier < first_tier_credit
    assert high_income_credit < donations_credit
    assert regular_credit < donations_credit
    assert first_tier_credit < donations_credit < federal_credits
    assert federal_credit < top_up_base < top_up_excess < top_up_credit < federal_credits
    assert first_tier_credit < top_up_base
    assert top_up_threshold < top_up_excess
    assert federal_credit < federal_credits < federal_after
    assert employment_sum < employment_amount < federal_amounts
    assert federal_amount < federal_dependant < federal_dependant_claimed < federal_amounts
    assert federal_caregiver < federal_amounts
    assert disability_transfer < federal_amounts
    assert infirm_children < federal_amounts
    assert net < medical_share < medical_threshold < medical_over < medical_claim < federal_amounts
    assert other_medical < medical_claim
    assert net < ontario_medical_share < ontario_medical_threshold < ontario_medical_over
    assert ontario_medical_over < ontario_medical_claim < ontario_amounts
    assert ontario_other_medical < ontario_medical_claim
    assert age_over_threshold < age_reduction < age_before_count < age < federal_amounts
    assert age_threshold < age_over_threshold
    assert age_maximum < age_before_count
    assert federal_amount < spouse_basis < spouse_before_count < spouse < federal_amounts
    assert spouse_supplement < spouse_basis
    assert caregiver_base < caregiver_before_maximum < caregiver_limit < caregiver_before_count
    assert spouse < caregiver_before_count < caregiver < federal_amounts
    assert ontario_base < ontario_before_maximum < ontario_dependant
    assert ontario_dependant < ontario_dependant_claimed < ontario_caregiver < ontario_amounts
    assert ontario_disability_transfer < ontario_amounts
    assert ontario_age_over_threshold < ontario_age_reduction < ontario_age_before_count
    assert ontario_age_before_count < ontario_age < ontario_amounts
    assert ontario_age_threshold < ontario_age_over_threshold
    assert ontario_age_maximum < ontario_age_before_count
    assert ontario_spouse_base < ontario_spouse_before_maximum < ontario_spouse_before_count
    assert ontario_spouse_before_count < ontario_spouse < ontario_amounts
    assert ontario_amount < ontario_amounts < ontario_credit < ontario_line_50 < ontario_after
    assert first_tier < ontario_first_tier_credit < ontario_donations_credit < ontario_line_50
    assert over_first_tier < ontario_over_first_tier_credit < ontario_donations_credit
    assert ontario_after < with_split_income < after_carryover < surtax_base < surtax_first
    assert surtax_first < surtax_second < with_surtax
    assert line_58 < carryover_applied < after_carryover
    assert carryover_credit < carryover_applied
    assert surtax_base < worksheet_line_2 < worksheet_line_3 < worksheet_line_6_first
    assert worksheet_line_1 < worksheet_line_3
    assert worksheet_line_6_first < worksheet_line_6_second < worksheet_line_8
    assert surtax_second < worksheet_line_7 < worksheet_line_8 < line_72 < line_73
    assert worksheet_line_1 < line_72
    assert reduction_basic < reduction_amounts
    assert children_before_rule < reduction_children < reduction_amounts
    assert dependants_before_rule < reduction_dependants < reduction_amounts
    assert spouse_rule_condition < spouse_rule < reduction_children
    assert spouse_rule < reduction_dependants
    assert gate_conditions == sorted(gate_conditions)
    assert gate_conditions[-1] < gate < reduction
    assert dividend_a < dividend_eligible < dividend_credit < line_70
    assert dividend_b < dividend_other < dividend_credit
    assert ontario_after < line_56 < line_58
    assert with_surtax < line_71 < line_73 < reduction_before_conditions < reduction
    assert reduction < after_reduction
    assert line_73 < after_reduction
    assert reduction_amounts < reduction_before_conditions
    assert taxable < health_income < premium_first < premium_second < premium_third < premium_fourth
    assert premium_fourth < premium_fifth < ontario_tax
    assert after_food < line_52 < ontario_tax
    assert (
        lift_sum < lift_before_maximum < lift_maximum < lift < after_lift < after_food < ontario_tax
    )
    assert lift_net < lift_adjusted < lift_reduction < lift_single < lift
    assert lift_uccb_and_rdsp < lift_adjusted
    assert lift_spouse_net < lift_spouse_adjusted < lift_family_net < lift_excess_family
    assert lift_spouse_uccb_and_rdsp < lift_spouse_adjusted
    assert lift_individual_threshold < lift_excess_individual < lift_greater
    assert lift_family_threshold < lift_excess_family < lift_greater
    assert lift_greater < lift_family_reduction < lift_with_spouse < lift
    assert food_applied < food_credit < after_food
    assert lift_net < lift_reduction < lift
    assert after_reduction < after_lift
    assert federal_after < with_recapture < less_credits < net_federal < payable
    assert recapture_at_15 < recapture < with_recapture
    assert recapture_at_20 < recapture
    assert labour_before_maximum < labour_credit < federal_credits < less_credits
    assert aips_counted < aips_reduction < aips_subject < aips_part_a < aips_tax < special
    assert aips_limit < aips_remaining < aips_reduction
    assert aips_part_b < aips_tax
    assert special < net_federal
    assert ontario_tax < payable < balance
    assert working < cwb_before_reduction < cwb_without < cwb
    assert family_net < cwb_reduction < cwb_without
    assert working < cwb_before_reduction_dependant < cwb_with < cwb
    assert family_net < cwb_reduction_dependant < cwb_with
    assert fertility_before_maximum < fertility < ontario_credits_subtotal
    assert net_signed < net
    assert net_signed < taxable_signed < taxable
    assert net_signed < child_care_adjusted
    assert (
        child_care_adjusted
        < child_care_family
        < child_care_rate
        < child_care_credit
        < ontario_credits_subtotal
    )
    assert care_before_maximum < care_amount < care_before_claim < care_credit
    assert care_family_net_income < care_over_base < care_reduction < care_before_claim
    assert care_base < care_over_base
    assert care_credit < ontario_credits_subtotal
    assert transit_paid < transit < ontario_credits_subtotal
    assert flow_through_expenses < flow_through < ontario_credits_subtotal
    assert coop_threshold < coop_over_threshold < coop_phase_out < coop_remaining < coop_credit
    assert coop_range < coop_phase_out
    assert coop_full_share < coop_remaining
    assert coop_credit < ontario_credits
    assert coop_count != coop_credit
    assert ontario_credits_subtotal < ontario_credits < provincial < credits
    assert cwb < credits
    assert credits < balance
    assert educator_expenses < educator_credit < credits
    assert credits < refund < refund_before_donation < donation_checked < net_refund
    assert payable < refund
