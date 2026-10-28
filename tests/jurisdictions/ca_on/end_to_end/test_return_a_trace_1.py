"""CA-ON 2025 end to end, Return A: return a trace 1."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.trace import (
    TimesCountLine,
)
from tax_calculator.jurisdictions.ca.catalog import (
    AGE_AMOUNT_BEFORE_COUNT,
    CAREGIVER_AMOUNT,
    DISABILITY_TRANSFERRED_AMOUNT,
    MEDICAL_CLAIM,
    MEDICAL_NET_INCOME_SHARE,
    OTHER_DEPENDANTS_MEDICAL,
)
from tax_calculator.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import D, run_a


def test_the_trace_explains_the_computation() -> None:
    result = run_a()
    trace = (*result["ca/schedule_8"][0].trace, *result["ca-on/return"][0].trace)
    rendered = EnglishTraceRenderer().render_all(trace)

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
            for i, (text, line) in enumerate(zip(rendered, trace, strict=True))
            if text == expected
            and line.amount == D(amount)
            and (
                claimed is None
                or (isinstance(line, TimesCountLine) and line.amount_kind is claimed)
            )
            and (output is None or getattr(line, "output", None) is output)
        ]
        return found

    included = position(
        "included_capital_gain: 50% of capital_gain 20000 (half-up to 0.01)", "10000"
    )
    taxable_gains = position(
        "taxable_capital_gains: included_capital_gain 10000 + "
        "partnership_gains_at_full_inclusion 0, not below 0 = 10000",
        "10000",
    )
    assert included < taxable_gains
    investment_before = position(
        "investment_income_before_prior_years: t3_investment_income 0 + "
        "t5_investment_income 0 + t5013_investment_income 0 + "
        "investment_income_credited_not_received 0 + tax_refund_interest 0 + "
        "foreign_investment_income 0 + investment_income_without_a_slip 0 + "
        "investment_royalties 0 = 0",
        "0",
    )
    checked = position(
        "investment_income_reported_in_previous_years_applied: "
        "investment_income_reported_in_previous_years 0, "
        "at most investment_income_before_prior_years 0",
        "0",
    )
    interest = position(
        "interest_and_other_investment_income: "
        "investment_income_before_prior_years 0 less "
        "investment_income_reported_in_previous_years_applied 0 = 0",
        "0",
    )
    support = position(
        "income_support_benefits: workers_compensation_benefits 0 + "
        "social_assistance_payments 0 + net_federal_supplements 0 = 0",
        "0",
    )
    total = position(
        "total_income: employment_income 110000 + other_employment_income 0 + "
        "old_age_security 0 + cpp_or_qpp_benefits 0 + "
        "other_pensions_and_superannuation 0 + t2205_on_line_11500 0 + "
        "elected_split_pension_amount 0 + "
        "universal_child_care_benefit 0 + ei_and_other_benefits 0 + taxable_dividends 0 + "
        "interest_and_other_investment_income 0 + net_partnership_income 0 + "
        "rdsp_income 0 + net_rental_income 0 + taxable_capital_gains 10000 "
        "+ taxable_support_payments 0 "
        "+ rrsp_income 0 + t2205_on_line_12900 0 + fhsa_income 0 + other_fhsa_income 0 + "
        "other_income 0 + t2205_on_line_13000 0 + taxable_scholarships 0 "
        "+ net_self_employment_income 0 "
        "+ income_support_benefits 0 = 120000",
        "120000",
    )
    cpp_base = position(
        "cpp_base_contributions: 4.95% of "
        "t4_cpp_pensionable_earnings_outside_quebec between 3500 and 71300 (67800), "
        "at most 3356.1 (half-up to 0.01)",
        "3356.10",
    )
    cpp_first = position(
        "cpp_first_additional_contributions: 1% of "
        "t4_cpp_pensionable_earnings_outside_quebec between 3500 and 71300 "
        "(67800), at most 678 (half-up to 0.01)",
        "678.00",
    )
    cpp_second = position(
        "cpp_second_additional_contributions: 4% of "
        "t4_cpp_pensionable_earnings_outside_quebec between 71300 and 81200 "
        "(9900), at most 396 (half-up to 0.01)",
        "396.00",
    )
    cpp_enhanced = position(
        "cpp_enhanced_contributions: cpp_first_additional_contributions 678 "
        "+ cpp_second_additional_contributions 396 = 1074",
        "1074.00",
    )
    ei = position(
        "ei_premiums: t2204_line_16 1077.48 = 1077.48",
        "1077.48",
    )
    rrsp_available = position(
        "rrsp_contributions_available: unused_rrsp_contributions 0 "
        "+ rrsp_contributions 1926 = 1926",
        "1926",
    )
    rrsp_maximum = position(
        "rrsp_deduction_maximum: lesser of rrsp_contributions_available 1926 "
        "and rrsp_deduction_limit 19800 = 1926",
        "1926",
    )
    rrsp = position(
        "rrsp_deduction: rrsp_amount_deducted 1926, at most rrsp_deduction_maximum 1926",
        "1926",
    )
    rrsp_carried = position(
        "unused_rrsp_contributions_carried_forward: rrsp_contributions_available 1926 "
        "less rrsp_deduction 1926 = 0",
        "0",
    )
    child_care_under_seven = position(
        "child_care_limit_for_children_under_seven: 8000 for each of 0 children_under_seven "
        "= 0 (half-up to 0.01)",
        "0",
    )
    child_care_disability = position(
        "child_care_limit_for_children_with_disability: 11000 for each of 0 "
        "children_with_disability = 0 (half-up to 0.01)",
        "0",
    )
    child_care_seven_to_sixteen = position(
        "child_care_limit_for_children_seven_to_sixteen: 5000 for each of 0 "
        "children_seven_to_sixteen = 0 (half-up to 0.01)",
        "0",
    )
    child_care_basic = position(
        "child_care_basic_limit: child_care_limit_for_children_under_seven 0 "
        "+ child_care_limit_for_children_with_disability 0 "
        "+ child_care_limit_for_children_seven_to_sixteen 0 = 0",
        "0",
    )
    child_care_earned = position(
        "child_care_earned_income: employment_income 110000 = 110000", "110000"
    )
    child_care_earned_limit = position(
        "child_care_earned_income_limit: 2/3 of child_care_earned_income 110000 (half-up to 0.01)",
        "73333.33",
    )
    child_care = position(
        "child_care_expenses: lesser of child_care_basic_limit 0 and child_care_expenses_paid 0 "
        "and child_care_earned_income_limit 73333.33 = 0",
        "0",
    )
    deductions = position(
        "deductions_from_total_income: rpp_deduction 0 + rrsp_deduction 1926 "
        "+ fhsa_deduction 0 "
        "+ elected_split_pension_deduction 0 + union_dues 2000 + uccb_repayment 0 "
        "+ child_care_expenses 0 + disability_supports_deduction 0 "
        "+ allowable_business_investment_loss 0 "
        "+ moving_expenses_deduction 0 "
        "+ support_payments_deduction_checked 0 "
        "+ carrying_charges_interest_expenses_and_other_expenses 0 "
        "+ cpp_deduction_on_self_employment_and_other_earnings 0 "
        "+ cpp_enhanced_contributions_on_return 1074 + exploration_and_development_expenses 0 "
        "+ other_employment_expenses 0 "
        "+ clergy_residence_deduction 0 "
        "+ other_deductions 0 + t746_deduction_on_return 0 "
        "+ t1043_deduction_on_return 0 "
        "+ foreign_property_tax_over_limit 0 + total_split_income 0 = 5000",
        "5000",
    )
    position(
        "net_income_signed: net_income_before_adjustments 115000 less social_benefits_repayment 0 "
        "= 115000",
        "115000",
    )
    net = position(
        "net_income: net_income_before_adjustments 115000 less social_benefits_repayment 0, "
        "not below 0 = 115000",
        "115000",
    )
    position("uccb_and_rdsp_income: universal_child_care_benefit 0 + rdsp_income 0 = 0", "0")
    line_5 = position(
        "net_income_less_uccb_and_rdsp_income: net_income_before_adjustments_not_below_zero "
        "115000 less uccb_and_rdsp_income 0 = 115000",
        "115000",
    )
    position(
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
    other_payments = position(
        "other_payments_deduction: income_support_benefits 0, "
        "chosen as other_payments_worksheet_required is 0",
        "0",
    )
    net_deductions = position(
        "deductions_from_net_income: canadian_armed_forces_and_police_deduction 0 "
        "+ security_options_deductions 0 + other_payments_deduction 0 "
        "+ limited_partnership_losses_of_other_years_checked 0 "
        "+ non_capital_losses_on_line_25200 0 "
        "+ net_capital_losses_of_other_years 0 + qbt_capital_gains_deduction 0 "
        "+ capital_gains_deduction 0 + northern_residents_deductions 0 "
        "+ additional_deductions_total 0 = 0",
        "0",
    )
    # Form T2222 for Return A: no days, so no residency amount, the 20% limit on its net income
    # of 115000 is 23000.00, line 13 is the lesser, 0, no trips and no individuals.
    residency_limit = position(
        "residency_net_income_limit: 20% of net_income 115000 (half-up to 0.01)", "23000"
    )
    residency_deduction = position(
        "residency_deduction: lesser of residency_amount 0 and residency_net_income_limit 23000 "
        "= 0",
        "0",
    )
    zone_a_trips = position("travel_total_zone_a: no items = 0", "0")
    zone_b_trips = position("travel_total_zone_b: no items = 0", "0")
    chart_a = position("standard_amount_allocated: no items = 0", "0")
    travel_b = position(
        "travel_zone_b_deduction: 50% of travel_total_zone_b 0 (half-up to 0.01)", "0"
    )
    travel = position(
        "travel_deduction: travel_total_zone_a 0 + travel_zone_b_deduction 0 = 0", "0"
    )
    northern = position(
        "northern_residents_deductions: residency_deduction 0 + travel_deduction 0 = 0", "0"
    )
    position(
        "taxable_income_signed: net_income_signed 115000 less deductions_from_net_income 0 "
        "= 115000",
        "115000",
    )
    taxable = position(
        "taxable_income: net_income 115000 less deductions_from_net_income 0, not below 0 = 115000",
        "115000",
    )
    position("26% on 250 over 114750 plus 20081.25", "20146.25")
    position("federal_basic_tax on taxable_income 115000 (half-up to 0.01)", "20146.25")
    position(
        "basic_personal_amount: 14538 plus 1591 less 0 for "
        "tosi_adjusted_net_income_not_below_zero 115000 over 177882 "
        "(range 75532), not below 14538 (half-up to 0.01)",
        "16129",
    )
    position(
        "canada_employment_amount_income: employment_income 110000 + "
        "other_employment_income 0 = 110000",
        "110000",
    )
    position(
        "canada_employment_amount: lesser of canada_employment_amount_income 110000 and 1471 "
        "(half-up to 0.01)",
        "1471",
    )
    position(
        "eligible_dependant_amount_basis: basic_personal_amount 16129 "
        "+ dependant_infirmity_supplement 0 = 16129",
        "16129",
    )
    position(
        "eligible_dependant_amount_before_count: eligible_dependant_amount_basis 16129 "
        "less dependant_net_income 0, not below 0 = 16129",
        "16129",
    )
    position(
        "eligible_dependant_amount: eligible_dependant_amount_before_count 16129 "
        "for each of 0 eligible_dependants_checked = 0",
        "0",
    )
    position("caregiver_amount: no items = 0", "0", output=CAREGIVER_AMOUNT)
    position("caregiver_amount: no items = 0", "0", output=ontario.CAREGIVER_AMOUNT)
    # The T1's line 31800 and ON428's line 58480 read alike when both lists are empty, so each
    # total is told apart by the kind it produces.
    position(
        "disability_transferred_amount: no items = 0", "0", output=DISABILITY_TRANSFERRED_AMOUNT
    )
    position(
        "disability_transferred_amount: no items = 0",
        "0",
        output=ontario.DISABILITY_TRANSFERRED_AMOUNT,
    )
    position(
        "infirm_children_amount: 2687 for each of 0 infirm_children = 0 (half-up to 0.01)", "0"
    )
    position(
        "medical_net_income_share: 3% of net_income 115000 (half-up to 0.01)",
        "3450",
        output=MEDICAL_NET_INCOME_SHARE,
    )
    position(
        "medical_threshold: lesser of medical_net_income_share 3450 and 2834 (half-up to 0.01)",
        "2834",
    )
    position(
        "medical_expenses_over_threshold: medical_expenses 0 less medical_threshold 2834, "
        "not below 0 = 0",
        "0",
    )
    position("other_dependants_medical: no items = 0", "0", output=OTHER_DEPENDANTS_MEDICAL)
    position(
        "medical_claim: medical_expenses_over_threshold 0 + other_dependants_medical 0 = 0",
        "0",
        output=MEDICAL_CLAIM,
    )
    position(
        "medical_net_income_share: 3% of net_income 115000 (half-up to 0.01)",
        "3450",
        output=ontario.MEDICAL_NET_INCOME_SHARE,
    )
    position(
        "medical_threshold: lesser of medical_net_income_share 3450 and 2885 (half-up to 0.01)",
        "2885",
    )
    position(
        "medical_expenses_over_threshold: medical_expenses 0 less medical_threshold 2885, "
        "not below 0 = 0",
        "0",
    )
    position("other_dependants_medical: no items = 0", "0", output=ontario.OTHER_DEPENDANTS_MEDICAL)
    position(
        "medical_claim: medical_expenses_over_threshold 0 + other_dependants_medical 0 = 0",
        "0",
        output=ontario.MEDICAL_CLAIM,
    )
    position("age_maximum: credit amount 9028 (half-up to 0.01)", "9028.00")
    position("age_income_threshold: credit amount 45522 (half-up to 0.01)", "45522.00")
    position(
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 115000 "
        "less age_income_threshold 45522, not below 0 = 69478",
        "69478",
    )
    position("age_reduction: 15% of age_income_over_threshold 69478 (half-up to 0.01)", "10421.70")
    position(
        "age_amount_before_count: age_maximum 9028 less age_reduction 10421.7, not below 0 = 0",
        "0",
    )
    position(
        "age_amount: age_amount_before_count 0 for each of 0 born_in_1960_or_earlier_checked = 0",
        "0",
        AGE_AMOUNT_BEFORE_COUNT,
    )
    position(
        "spouse_infirmity_supplement: 2687 for each of 0 spouse_caregiver_eligible_checked = 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "spouse_amount_basis: basic_personal_amount 16129 + spouse_infirmity_supplement 0 = 16129",
        "16129",
    )
    position(
        "spouse_amount_before_count: spouse_amount_basis 16129 "
        "less spouse_net_income 0, not below 0 = 16129",
        "16129",
    )
    position(
        "spouse_amount: spouse_amount_before_count 16129 for each of 0 spouses_claimed_checked = 0",
        "0",
    )
    position("spouse_caregiver_base: credit amount 28798 (half-up to 0.01)", "28798.00")
    position(
        "spouse_caregiver_before_maximum: spouse_caregiver_base 28798 "
        "less spouse_net_income 0, not below 0 = 28798",
        "28798",
    )
    position(
        "spouse_caregiver_limit: lesser of spouse_caregiver_before_maximum 28798 and 8601 "
        "(half-up to 0.01)",
        "8601",
    )
    position(
        "spouse_caregiver_amount_before_count: spouse_caregiver_limit 8601 "
        "less spouse_amount 0, not below 0 = 8601",
        "8601",
    )
    position(
        "spouse_caregiver_amount: spouse_caregiver_amount_before_count 8601 "
        "for each of 0 spouse_caregiver_eligible_checked = 0",
        "0",
    )
    position(
        "dependant_infirmity_supplement: 2687 for each of 0 dependant_caregiver_eligible_checked = "
        "0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "dependant_caregiver_before_maximum: spouse_caregiver_base 28798 "
        "less dependant_net_income 0, not below 0 = 28798",
        "28798",
    )
    position(
        "dependant_caregiver_limit: lesser of dependant_caregiver_before_maximum 28798 "
        "and 8601 (half-up to 0.01)",
        "8601",
    )
    position(
        "dependant_caregiver_amount_before_count: dependant_caregiver_limit 8601 "
        "less eligible_dependant_amount 0, not below 0 = 8601",
        "8601",
    )
    position(
        "dependant_caregiver_amount_before_age_count: dependant_caregiver_amount_before_count 8601 "
        "for each of 0 dependant_caregiver_eligible_checked = 0",
        "0",
    )
    position(
        "dependant_caregiver_amount: dependant_caregiver_amount_before_age_count 0 "
        "for each of 0 dependant_caregiver_aged_18_or_older_checked = 0",
        "0",
    )
    position(
        "caregiver_amount_for_spouse_or_dependant: spouse_caregiver_amount 0 "
        "+ dependant_caregiver_amount 0 = 0",
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
    position(
        "credit_amounts_at_credit_rate: 14.5% of non_refundable_credit_amounts 22033.58 "
        "(half-up to 0.01)",
        "3194.87",
    )
    position(
        "federal_tax_after_credits: federal_tax_with_split_income 20146.25 "
        "less credits_against_basic_federal_tax 3194.87, not below 0 = 16951.38",
        "16951.38",
    )
    position("11.16% on 9225 over 105775 plus 7510.09", "8539.60")
    position("ontario_basic_tax on taxable_income 115000 (half-up to 0.01)", "8539.60")
    position("basic_personal_amount: credit amount 12747 (half-up to 0.01)", "12747")
    position("eligible_dependant_base: credit amount 11905 (half-up to 0.01)", "11905")
    position(
        "eligible_dependant_amount_before_maximum: eligible_dependant_base 11905 "
        "less dependant_net_income 0, not below 0 = 11905",
        "11905",
    )
    position(
        "eligible_dependant_amount_before_count: lesser of "
        "eligible_dependant_amount_before_maximum 11905 and 10823 (half-up to 0.01)",
        "10823",
    )
    position(
        "eligible_dependant_amount: eligible_dependant_amount_before_count 10823 "
        "for each of 0 eligible_dependants_checked = 0",
        "0",
    )
    position("age_maximum: credit amount 6223 (half-up to 0.01)", "6223.00")
    position("age_income_threshold: credit amount 46330 (half-up to 0.01)", "46330.00")
    position(
        "age_income_over_threshold: tosi_adjusted_net_income_not_below_zero 115000 "
        "less age_income_threshold 46330, not below 0 = 68670",
        "68670",
    )
    position("age_reduction: 15% of age_income_over_threshold 68670 (half-up to 0.01)", "10300.50")
    position(
        "age_amount_before_count: age_maximum 6223 less age_reduction 10300.5, not below 0 = 0",
        "0",
    )
    position(
        "age_amount: age_amount_before_count 0 for each of 0 born_in_1960_or_earlier_checked = 0",
        "0",
        ontario.AGE_AMOUNT_BEFORE_COUNT,
    )
    position("spouse_base: credit amount 11905 (half-up to 0.01)", "11905")
    position(
        "spouse_amount_before_maximum: spouse_base 11905 "
        "less spouse_net_income 0, not below 0 = 11905",
        "11905",
    )
    position(
        "spouse_amount_before_count: lesser of spouse_amount_before_maximum 11905 and 10823 "
        "(half-up to 0.01)",
        "10823",
    )
    position(
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
    position(
        "credit_amounts_at_credit_rate: 5.05% of non_refundable_credit_amounts 17180.58 "
        "(half-up to 0.01)",
        "867.62",
    )
    position("donations_first_tier_credit: 5.05% of donations_first_tier 0 (half-up to 0.01)", "0")
    position(
        "donations_over_first_tier_credit: 11.16% of donations_over_first_tier 0 (half-up to 0.01)",
        "0",
    )
    position(
        "donations_and_gifts_credit: donations_first_tier_credit 0 "
        "+ donations_over_first_tier_credit 0 = 0",
        "0",
    )
    position(
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 867.62 "
        "+ donations_and_gifts_credit 0 = 867.62",
        "867.62",
    )
    position(
        "ontario_tax_after_credits: ontario_basic_tax 8539.6 "
        "less non_refundable_tax_credits 867.62, not below 0 = 7671.98",
        "7671.98",
    )
    position(
        "ontario_tax_with_split_income: ontario_tax_after_credits 7671.98 "
        "+ ontario_tax_on_split_income 0 = 7671.98",
        "7671.98",
    )
    position(
        "minimum_tax_carryover_credit: 24.63% of amt_minimum_tax_carryover_applied 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "ontario_minimum_tax_carryover_applied: lesser of ontario_tax_less_dividend_credit "
        "7671.98 and minimum_tax_carryover_credit 0 = 0",
        "0",
    )
    position(
        "ontario_tax_after_minimum_tax_carryover: ontario_tax_with_split_income 7671.98 "
        "less ontario_minimum_tax_carryover_applied 0, not below 0 = 7671.98",
        "7671.98",
    )
    position(
        "ontario_surtax_base: ontario_tax_after_minimum_tax_carryover 7671.98 "
        "less ontario_tax_on_split_income_for_surtax 0, not below 0 = 7671.98",
        "7671.98",
    )
    position(
        "ontario_surtax: 20% of ontario_surtax_base 7671.98 over 5710 (half-up to 0.01)",
        "392.40",
    )
    position(
        "ontario_surtax: 36% of ontario_surtax_base 7671.98 over 7307 (half-up to 0.01)",
        "131.39",
    )
    position(
        "ontario_tax_with_surtax: ontario_tax_after_minimum_tax_carryover 7671.98 "
        "+ ontario_surtax 523.79 = 8195.77",
        "8195.77",
    )
    position(
        "worksheet_on428_line_1: 24.63% of amt_alternative_minimum_tax_payable 0 (half-up to 0.01)",
        "0",
    )
    position("worksheet_on428_line_2: ontario_surtax_base 7671.98 = 7671.98", "7671.98")
    position(
        "worksheet_on428_line_3: worksheet_on428_line_1 0 + worksheet_on428_line_2 7671.98 "
        "= 7671.98",
        "7671.98",
    )
    position(
        "worksheet_on428_line_6: 20% of worksheet_on428_line_3 7671.98 over 5710 (half-up to 0.01)",
        "392.40",
    )
    position(
        "worksheet_on428_line_6: 36% of worksheet_on428_line_3 7671.98 over 7307 (half-up to 0.01)",
        "131.39",
    )
    position("worksheet_on428_line_7: ontario_surtax 523.79 = 523.79", "523.79")
    position(
        "worksheet_on428_line_8: worksheet_on428_line_6 523.79 less worksheet_on428_line_7 "
        "523.79 = 0",
        "0",
    )
    position("ontario_minimum_tax: worksheet_on428_line_1 0 + worksheet_on428_line_8 0 = 0", "0")
    position("dividends_amount_a: taxable_dividends 0 = 0", "0")
    position("dividends_amount_b: taxable_dividends_other_than_eligible 0 = 0", "0")
    position("other_dividends_credit: 2.9863% of dividends_amount_b 0 (half-up to 0.01)", "0")
    position("eligible_dividends_credit: 10% of dividends_amount_a_less_b 0 (half-up to 0.01)", "0")
    position("dividend_tax_credit: other_dividends_credit 0 + eligible_dividends_credit 0 = 0", "0")
    position(
        "ontario_tax_before_dividend_credit: ontario_tax_after_credits 7671.98 = 7671.98",
        "7671.98",
    )
    position(
        "ontario_tax_less_dividend_credit: ontario_tax_before_dividend_credit 7671.98 "
        "less dividend_tax_credit 0, not below 0 = 7671.98",
        "7671.98",
    )
    position("dividend_credit_from_line_57: dividend_tax_credit 0 = 0", "0")
    position(
        "ontario_tax_after_dividend_credit: ontario_tax_with_surtax 8195.77 "
        "less dividend_credit_from_line_57 0, not below 0 = 8195.77",
        "8195.77",
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
    ):
        position(
            f'tax_reduction_claimable: condition {number} "{text}": {kind} 0, does not apply', "0"
        )
    position("tax_reduction_claimable: no condition applies, so 1", "1")
    position(
        "tax_reduction_basic: credit amount 294 (half-up to 0.01)",
        "294.00",
    )
    position(
        "tax_reduction_for_children_before_spouse_rule: 544 for each of 0 dependent_children = 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "tax_reduction_for_dependants_before_spouse_rule: 544 for each of 0 dependants = 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        'tax_reduction_amounts_claimable: condition 1 "If you had a spouse or common-law partner '
        "on December 31, 2025, only the individual with the higher net income can claim the "
        'amounts on lines 75 and 76.": spouse_or_common_law_partner_on_december_31_total 0, '
        "net_income 115000, spouse_net_income 0, net_income 115000, spouse_net_income 0, "
        "spouse_or_common_law_partner_on_december_31_total 0, net_income 115000, "
        "spouse_net_income 0, "
        "claims_tax_reduction_amounts_at_equal_net_income_checked 0, applies",
        "1",
    )
    position("tax_reduction_amounts_claimable: condition 1 applies, so 1", "1")
    position(
        "ontario_tax_before_reduction: ontario_tax_after_dividend_credit 8195.77 "
        "+ ontario_minimum_tax 0 = 8195.77",
        "8195.77",
    )
    position(
        "tax_reduction_for_children: tax_reduction_for_children_before_spouse_rule 0 "
        "for each of 1 tax_reduction_amounts_claimable = 0",
        "0",
    )
    position(
        "tax_reduction_for_dependants: tax_reduction_for_dependants_before_spouse_rule 0 "
        "for each of 1 tax_reduction_amounts_claimable = 0",
        "0",
    )
    position(
        "tax_reduction_amounts: tax_reduction_basic 294 + tax_reduction_for_children 0 "
        "+ tax_reduction_for_dependants 0 = 294",
        "294.00",
    )
    position(
        "ontario_tax_reduction_before_conditions: 2 × tax_reduction_amounts 294 "
        "over ontario_tax_before_reduction 8195.77, not below 0 (half-up to 0.01)",
        "0",
    )
    position(
        "ontario_tax_reduction: ontario_tax_reduction_before_conditions 0 "
        "for each of 1 tax_reduction_claimable = 0",
        "0",
    )
    position(
        "ontario_tax_after_reduction: ontario_tax_before_reduction 8195.77 "
        "less ontario_tax_reduction 0, not below 0 = 8195.77",
        "8195.77",
    )
    position(
        "lift_employment_income: employment_income 110000 + other_employment_income 0 = 110000",
        "110000",
    )
    position(
        "lift_credit_before_maximum: 5.05% of lift_employment_income 110000 (half-up to 0.01)",
        "5555",
    )
    position(
        "lift_maximum_credit: lesser of lift_credit_before_maximum 5555 and 875 (half-up to 0.01)",
        "875",
    )
    position(
        "lift_net_income_and_repayments: tosi_adjusted_net_income 115000 "
        "+ uccb_repayment 0 + rdsp_income_repayment_checked 0 = 115000",
        "115000",
    )
    position("lift_uccb_and_rdsp_income: universal_child_care_benefit 0 + rdsp_income 0 = 0", "0")
    position(
        "lift_adjusted_net_income: lift_net_income_and_repayments 115000 "
        "less lift_uccb_and_rdsp_income 0, not below 0 = 115000",
        "115000",
    )
    position(
        "lift_reduction: 5% of lift_adjusted_net_income 115000 over 32500 (half-up to 0.01)",
        "4125",
    )
    position(
        "lift_credit_single: lift_maximum_credit 875 less lift_reduction 4125, not below 0 = 0",
        "0",
    )
    position(
        "lift_spouse_net_income_and_repayments: spouse_net_income_before_adjustments 0 "
        "+ spouse_uccb_repayment 0 + spouse_rdsp_income_repayment 0 = 0",
        "0",
    )
    position(
        "lift_spouse_uccb_and_rdsp_income: spouse_universal_child_care_benefit 0 "
        "+ spouse_rdsp_income 0 = 0",
        "0",
    )
    position(
        "lift_spouse_adjusted_net_income: lift_spouse_net_income_and_repayments 0 "
        "less lift_spouse_uccb_and_rdsp_income 0, not below 0 = 0",
        "0",
    )
    position("lift_individual_income_threshold: credit amount 32500 (half-up to 0.01)", "32500.00")
    position(
        "lift_excess_over_individual_threshold: lift_adjusted_net_income 115000 "
        "less lift_individual_income_threshold 32500, not below 0 = 82500",
        "82500",
    )
    position(
        "lift_family_net_income: lift_adjusted_net_income 115000 "
        "+ lift_spouse_adjusted_net_income 0 = 115000",
        "115000",
    )
    position("lift_family_income_threshold: credit amount 65000 (half-up to 0.01)", "65000.00")
    position(
        "lift_excess_over_family_threshold: lift_family_net_income 115000 "
        "less lift_family_income_threshold 65000, not below 0 = 50000",
        "50000",
    )
    position(
        "lift_greater_excess: greater of lift_excess_over_individual_threshold 82500 "
        "and lift_excess_over_family_threshold 50000 = 82500",
        "82500",
    )
    position("lift_family_reduction: 5% of lift_greater_excess 82500 (half-up to 0.01)", "4125")
    position(
        "lift_credit_with_spouse: lift_maximum_credit 875 less lift_family_reduction 4125, "
        "not below 0 = 0",
        "0",
    )
    position(
        "lift_credit: lift_credit_single 0, chosen as "
        "spouse_or_common_law_partner_on_december_31_total is 0",
        "0",
    )
    position(
        "ontario_tax_after_lift_credit: ontario_tax_after_foreign_tax_credit 8195.77 "
        "less lift_credit 0, not below 0 = 8195.77",
        "8195.77",
    )
    position(
        "community_food_program_donations_applied: community_food_program_donations 0, "
        "at most donations_and_gifts_total 0",
        "0",
    )
    position(
        "community_food_program_credit: 25% of community_food_program_donations_applied 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "ontario_tax_after_food_credit: ontario_tax_after_lift_credit 8195.77 "
        "less community_food_program_credit 0, not below 0 = 8195.77",
        "8195.77",
    )
    position(
        "health_premium_income: taxable_income 115000 + total_split_income 0 = 115000",
        "115000",
    )
    position(
        "ontario_health_premium: 6% of health_premium_income 115000 over 20000, at most 300 "
        "(half-up to 0.01)",
        "300",
    )
    position(
        "ontario_health_premium: 6% of health_premium_income 115000 over 36000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 48000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 72000, at most 150 "
        "(half-up to 0.01)",
        "150",
    )
    position(
        "ontario_health_premium: 25% of health_premium_income 115000 over 200000, at most 150 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "split_income_line_52: greater of split_income_line_50 0 "
        "and ontario_tax_after_food_credit 8195.77 = 8195.77",
        "8195.77",
    )
    position(
        "ontario_tax: split_income_line_52 8195.77 + ontario_health_premium 750 = 8945.77",
        "8945.77",
    )
    position(
        "itc_recapture_at_15_percent: 15% of itc_recapture_expenditure_at_15_percent 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "itc_recapture_at_20_percent: 20% of itc_recapture_expenditure_at_20_percent 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "itc_recapture: itc_recapture_at_15_percent 0 + itc_recapture_at_20_percent 0 = 0", "0"
    )
    position(
        "federal_tax_with_itc_recapture: federal_tax_less_foreign_tax_credit 16951.38 "
        "+ itc_recapture 0 = 16951.38",
        "16951.38",
    )
    position(
        "labour_sponsored_funds_credit_before_maximum: 15% of labour_sponsored_funds_net_cost 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
        "labour_sponsored_funds_credit: lesser of labour_sponsored_funds_credit_before_maximum 0 "
        "and 750 (half-up to 0.01)",
        "0",
    )
    position(
        "credits_against_federal_tax: political_credit 0 + investment_tax_credit 0 "
        "+ labour_sponsored_funds_credit 0 = 0",
        "0",
    )
    position(
        "federal_tax: federal_tax_with_itc_recapture 16951.38 "
        "less federal_logging_tax_credit 0, not below 0 = 16951.38",
        "16951.38",
    )
    position(
        "federal_tax_less_credits: federal_tax 16951.38 "
        "less credits_against_federal_tax 0, not below 0 = 16951.38",
        "16951.38",
    )
    position(
        "resp_aips_contributions_counted: lesser of resp_aips_received_part_a 0 "
        "and resp_aips_rrsp_contributions 0 = 0",
        "0",
    )
    position("resp_aips_lifetime_limit: credit amount 50000 (half-up to 0.01)", "50000")
    position(
        "resp_aips_limit_remaining: resp_aips_lifetime_limit 50000 "
        "less resp_aips_reduction_used_in_previous_years 0 = 50000",
        "50000",
    )
    position(
        "resp_aips_reduction: lesser of resp_aips_contributions_counted 0 "
        "and resp_aips_limit_remaining 50000 = 0",
        "0",
    )
    position(
        "resp_aips_subject_to_tax: resp_aips_received_part_a 0 less resp_aips_reduction 0 = 0", "0"
    )
    position("resp_aips_part_a_tax: 20% of resp_aips_subject_to_tax 0 (half-up to 0.01)", "0")
    position("resp_aips_part_b_tax: 20% of resp_aips_received_part_b 0 (half-up to 0.01)", "0")
    position(
        "resp_aips_additional_tax: resp_aips_part_b_tax 0, chosen as "
        "resp_aips_part_a_applies_checked is 0",
        "0",
    )
    position(
        "special_taxes: resp_aips_additional_tax 0 + rl_10_labour_sponsored_fund_amount 0 "
        "+ rc359_tax_total 0 = 0",
        "0",
    )
    position(
        "net_federal_tax: split_income_line_30 16951.38 + special_taxes 0 = 16951.38",
        "16951.38",
    )
    position(
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
    position(
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
    position(
        "adjusted_family_net_income: cwb_family_net_income_line_13 115000 less "
        "cwb_secondary_earner_exemption 0 = 115000",
        "115000",
    )
    position(
        "cwb_before_reduction_without_dependant: 27% of cwb_family_working_income 110000 "
        "over 3000, "
        "at most 1633 (half-up to 0.01)",
        "1633",
    )
    position(
        "cwb_reduction_without_dependant: 15% of adjusted_family_net_income 115000 over 26855 "
        "(half-up to 0.01)",
        "13221.75",
    )
    position(
        "canada_workers_benefit_without_dependant: cwb_before_reduction_without_dependant 1633 "
        "less cwb_reduction_without_dependant 13221.75, not below 0 = 0",
        "0",
    )
    position(
        "cwb_before_reduction_with_dependant: 27% of cwb_family_working_income 110000 "
        "over 3000, "
        "at most 2813 (half-up to 0.01)",
        "2813",
    )
    position(
        "cwb_reduction_with_dependant: 15% of adjusted_family_net_income 115000 over 30639 "
        "(half-up to 0.01)",
        "12654.15",
    )
    position(
        "canada_workers_benefit_with_dependant: cwb_before_reduction_with_dependant 2813 "
        "less cwb_reduction_with_dependant 12654.15, not below 0 = 0",
        "0",
    )
    position(
        "canada_workers_benefit_line_28: cwb_line_28_by_spouse 0, "
        "chosen as cwb_eligible_dependants_checked is 0",
        "0",
    )
    position("fertility_credit_before_maximum: 25% of fertility_expenses 0 (half-up to 0.01)", "0")
    position(
        "fertility_credit: lesser of fertility_credit_before_maximum 0 and 5000 (half-up to 0.01)",
        "0",
    )
    position(
        "care_adjusted_income: tosi_adjusted_net_income 115000 + child_care_expenses 0 "
        "+ social_benefits_repayment 0, not below 0 = 115000",
        "115000",
    )
    position(
        "care_family_adjusted_income: care_adjusted_income 115000 "
        "+ care_supporting_persons_adjusted_income 0 = 115000",
        "115000",
    )
    position(
        "care_credit_percentage: care_family_adjusted_income 115000, "
        "more than 114000 but not more than 117600: 19%",
        "0.19",
    )
    position(
        "care_credit: care_credit_percentage 19% of child_care_expenses 0 (half-up to 0.01)", "0"
    )
    position("seniors_care_before_maximum: 25% of medical_claim 0 (half-up to 0.01)", "0")
    position(
        "seniors_care_amount: lesser of seniors_care_before_maximum 0 and 1500 (half-up to 0.01)",
        "0",
    )
    position(
        "seniors_care_family_net_income: tosi_adjusted_net_income_not_below_zero 115000 "
        "+ spouse_net_income 0 = 115000",
        "115000",
    )
    position("seniors_care_base_amount: credit amount 35000 (half-up to 0.01)", "35000")
    position(
        "seniors_care_income_over_base: seniors_care_family_net_income 115000 "
        "less seniors_care_base_amount 35000, not below 0 = 80000",
        "80000",
    )
    position(
        "seniors_care_reduction: 5% of seniors_care_income_over_base 80000 (half-up to 0.01)",
        "4000",
    )
    position(
        "seniors_care_before_claim: seniors_care_amount 0 "
        "less seniors_care_reduction 4000, not below 0 = 0",
        "0",
    )
    position(
        "seniors_care_credit: seniors_care_before_claim 0 "
        "for each of 0 claims_seniors_care_credit_checked = 0",
        "0",
    )
    position("seniors_transit_maximum: credit amount 3000 (half-up to 0.01)", "3000.00")
    position(
        "seniors_transit_amount_paid_checked: seniors_transit_paid 0, at most "
        "seniors_transit_maximum 3000",
        "0",
    )
    position(
        "seniors_transit_credit: 15% of seniors_transit_amount_paid_checked 0 (half-up to 0.01)",
        "0",
    )
    position("flow_through_share_expenses: no items = 0", "0")
    position(
        'flow_through_share_claimable: condition 1 "You were not a resident of Ontario on the '
        'last day of the tax year": not_resident_of_ontario_at_year_end_checked 0, does not apply',
        "0",
    )
    position("flow_through_share_claimable: no condition applies, so 1", "1")
    position(
        "flow_through_share_credit: 5% of flow_through_share_expenses_claimed 0 (half-up to 0.01)",
        "0",
    )
    position(
        "ontario_credits_subtotal: fertility_credit 0 + care_credit 0 + seniors_care_credit 0 "
        "+ seniors_transit_credit 0 + political_credit 0 + flow_through_share_credit 0 = 0",
        "0",
    )
    position("coop_education_payroll_threshold: credit amount 400000 (half-up to 0.01)", "400000")
    position(
        "coop_education_payroll_over_threshold: coop_education_payroll 0 "
        "less coop_education_payroll_threshold 400000, not below 0 = 0",
        "0",
    )
    position("coop_education_payroll_range: credit amount 200000 (half-up to 0.01)", "200000")
    position(
        "coop_education_phase_out_share: coop_education_payroll_over_threshold 0 "
        "divided by coop_education_payroll_range 200000 = 0",
        "0",
    )
    position("coop_education_full_share: credit amount 1 (half-up to 0.01)", "1")
    position(
        "coop_education_remaining_share: coop_education_full_share 1 "
        "less coop_education_phase_out_share 0, not below 0 = 1",
        "1",
    )
    position("coop_education_credit: no items = 0", "0")
    position("coop_education_placement_count: no items in coop_education_placements = 0", "0")
    position("ontario_credits: ontario_credits_subtotal 0 + coop_education_credit 0 = 0", "0")
    position("provincial_credits: ontario_credits 0 = 0", "0")
    position(
        "educator_supplies_expenses_at_most_maximum: lesser of educator_supplies_expenses 0 "
        "and 1000 (half-up to 0.01)",
        "0",
    )
    position(
        "educator_school_supply_credit: 25% of educator_supplies_expenses_at_most_maximum 0 "
        "(half-up to 0.01)",
        "0",
    )
    position(
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
    position(
        "refund_or_balance_owing: total_payable 25897.15 less total_credits 25000 = 897.15",
        "897.15",
    )
    position("refund: total_credits 25000 less total_payable 25897.15, not below 0 = 0", "0")
    position("refund_before_donation: refund 0 = 0", "0")
    position(
        "opportunities_fund_donation_checked: opportunities_fund_donation 0, "
        "at most refund_before_donation 0",
        "0",
    )
    position(
        "net_refund: refund_before_donation 0 less opportunities_fund_donation_checked 0 = 0",
        "0",
    )
    position(
        "depreciable_gift_proceeds_or_cost: lesser of depreciable_gift_net_proceeds 0 "
        "and depreciable_gift_capital_cost 0 = 0",
        "0",
    )
    position(
        "depreciable_gifts: lesser of depreciable_gift_recaptured_depreciation 0 "
        "and depreciable_gift_proceeds_or_cost 0 = 0",
        "0",
    )
    position(
        "capital_property_gifts: capital_gift_taxable_gains 0 "
        "less capital_gift_gains_deduction_checked 0 = 0",
        "0",
    )
    position(
        "total_charitable_donations: charitable_donations 0 + government_donations 0 "
        "+ university_donations_outside_canada 0 + foreign_charity_donations 0 = 0",
        "0",
    )
    position("donation_limit_on_net_income: 75% of net_income 115000 (half-up to 0.01)", "86250")
    position("capital_gifts_total: depreciable_gifts 0 + capital_property_gifts 0 = 0", "0")
    position("capital_gifts_limit_addition: 25% of capital_gifts_total 0 (half-up to 0.01)", "0")
    position(
        "donation_limit_with_capital_gifts: donation_limit_on_net_income 86250 "
        "+ capital_gifts_limit_addition 0 = 86250",
        "86250",
    )
    position(
        "charitable_donations_limit: lesser of net_income 115000 "
        "and donation_limit_with_capital_gifts 86250 = 86250",
        "86250",
    )
    position(
        "charitable_donations_claimed: lesser of total_charitable_donations 0 "
        "and charitable_donations_limit 86250 = 0",
        "0",
    )
    position(
        "donations_and_gifts_total: charitable_donations_claimed 0 "
        "+ ecological_and_cultural_gifts 0 = 0",
        "0",
    )
    position("donation_first_tier_maximum: credit amount 200 (half-up to 0.01)", "200")
    position(
        "donations_first_tier: lesser of donations_and_gifts_total 0 "
        "and donation_first_tier_maximum 200 = 0",
        "0",
    )
    position(
        "donations_over_first_tier: donations_and_gifts_total 0 less donations_first_tier 0 = 0",
        "0",
    )
    position(
        "donations_over_first_tier_after_2016_gifts: donations_over_first_tier 0 "
        "less ecological_gifts_before_2016 0, not below 0 = 0",
        "0",
    )
    position("donation_high_income_threshold: credit amount 253414 (half-up to 0.01)", "253414")
    position(
        "taxable_income_over_donation_threshold: taxable_income 115000 "
        "less donation_high_income_threshold 253414, not below 0 = 0",
        "0",
    )
    position(
        "high_income_donations: lesser of donations_over_first_tier_after_2016_gifts 0 "
        "and taxable_income_over_donation_threshold 0 = 0",
        "0",
    )
    position("high_income_donation_credit: 33% of high_income_donations 0 (half-up to 0.01)", "0")
    position(
        "regular_rate_donations: donations_over_first_tier 0 less high_income_donations 0 = 0",
        "0",
    )
    position("regular_rate_donation_credit: 29% of regular_rate_donations 0 (half-up to 0.01)", "0")
    position("first_tier_donation_credit: 14.5% of donations_first_tier 0 (half-up to 0.01)", "0")
    position(
        "donations_and_gifts_credit: high_income_donation_credit 0 "
        "+ regular_rate_donation_credit 0 + first_tier_donation_credit 0 = 0",
        "0",
    )
    position(
        "top_up_credits_base: credit_amounts_at_credit_rate 3194.87 "
        "+ first_tier_donation_credit 0 = 3194.87",
        "3194.87",
    )
    position("top_up_threshold: credit amount 8319.38 (half-up to 0.01)", "8319.38")
    position(
        "top_up_excess: top_up_credits_base 3194.87 less top_up_threshold 8319.38, not below 0 = 0",
        "0",
    )
    position("top_up_tax_credit: 3.45% of top_up_excess 0 (half-up to 0.01)", "0")
    position(
        "non_refundable_tax_credits: credit_amounts_at_credit_rate 3194.87 "
        "+ donations_and_gifts_credit 0 + top_up_tax_credit 0 = 3194.87",
        "3194.87",
    )
    assert taxable_gains < total < net
    assert investment_before < checked < interest < total
    assert support < total
    assert cpp_first < cpp_enhanced < deductions < net
    assert rrsp_available < rrsp_maximum < rrsp < deductions
    assert rrsp < rrsp_carried
    assert child_care_under_seven < child_care_basic
    assert child_care_disability < child_care_basic
    assert child_care_seven_to_sixteen < child_care_basic < child_care
    assert child_care_earned < child_care_earned_limit < child_care < deductions
    assert cpp_second < cpp_enhanced
    assert cpp_base < federal_amounts
    assert cpp_base < ontario_amounts
    assert ei < federal_amounts
    assert ei < ontario_amounts
    assert net < taxable
    assert line_5 < line_9
    assert support < after_limit < other_payments < net_deductions < taxable
    assert net < residency_limit < residency_deduction < northern < net_deductions
    assert zone_a_trips < travel < northern
    assert zone_b_trips < travel_b < travel
    assert chart_a < taxable
