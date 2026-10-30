"""The CA-ON manifest entries of Form T929, the disability supports deduction (T1 line 21500), and
the return's line 21500 (see `test_manifest.py` and `test_manifest_t929.py`). Form `ca/t929` is
run once for the one copy of the form the return carries (`ca/t929_instances`, a record list of no
fields with `min_instances` 0 and `max_instances` 1). Its figures are manifest inputs: lines 1 and
2 (`T929_EXPENSES_PAID`, `T929_EXPENSES_REIMBURSED`), line 8 (`T929_WEEKS_ATTENDED`), and the six
earned-income items of line 4. Its selections are `FORM_STEPS`: the 13 of its own (`OWN_STEPS`)
and 141 copies of the return's steps that compute the net income of line 23600, the figure line 5
reads (`COPIED_STEPS`; the return keeps the originals, except the line 23300 sum, which the copies
leave without line 21500). The form exports its computed lines 3, 4, 7, 9, 10 and 11 and line 12,
which is the disability supports deduction (`FORM_EXPORTS`); the return re-produces the deduction
with `core/record_total` over the form's derived kind `ca/t929.disability_supports_deduction`
(`STEPS`), before the line 23300 sum, which adds it (`deductions.py`). `IMPORTS` are the other
forms' exports and the return's record lists the copies read. The two datasets, the weekly amount
of $375 and the maximum of $15,000, are `ca/t929_weekly_amount` and `ca/t929_maximum`.
"""

from __future__ import annotations

from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.per_unit_amount import PerUnitAmount
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.manifest import CapabilitySelection
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.capabilities.lesser_of_with_maximum import LesserOfWithMaximum
from tax_engine.jurisdictions.ca.capabilities.yes_or_no_count import YesOrNoCount
from tax_engine.jurisdictions.ca.catalog import (
    DISABILITY_SUPPORTS_DEDUCTION,
    EMPLOYMENT_INCOME,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED,
    MOVING_EXPENSES_CLAIM,
    NET_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    T929_COVID_19_PAYMENTS,
    T929_EARNINGS_SUPPLEMENTS,
    T929_EMPLOYMENT_INSURANCE_PART_2_SUPPORT,
    T929_EXPENSES_PAID,
    T929_EXPENSES_REIMBURSED,
    T929_INCOME_REPLACEMENT_SUPPORT,
    T929_LINE_3,
    T929_LINE_4,
    T929_LINE_7,
    T929_LINE_9,
    T929_LINE_10,
    T929_LINE_11,
    T929_NET_BUSINESS_INCOME,
    T929_NET_COMMISSION_INCOME,
    T929_NET_FARMING_INCOME,
    T929_NET_FISHING_INCOME,
    T929_NET_PROFESSIONAL_INCOME,
    T929_NET_RESEARCH_GRANTS,
    T929_WAGE_EARNER_PROTECTION_AMOUNTS,
    T929_WEEKS_ATTENDED,
    TAXABLE_SCHOLARSHIPS,
)
from tests.jurisdictions.ca_on.manifest_families.t1139 import (
    BUSINESS_PROFIT_ON_RETURN_LINES,
    COMMISSION_PROFIT_ON_RETURN_LINES,
    FARMING_PROFIT_ON_RETURN_LINES,
    FISHING_PROFIT_ON_RETURN_LINES,
    PROFESSIONAL_PROFIT_ON_RETURN_LINES,
)

MOVING_EXPENSES_CLAIM_PER_MOVE = RecordListKind(
    "ca/t1_m.moving_expenses_claim", fields=(MOVING_EXPENSES_CLAIM,)
)

# The manifest inputs of the form: its instances and every figure it takes as entered.
INPUTS = frozenset(
    {
        "ca/t929_instances",
        "ca/t929_expenses_paid",
        "ca/t929_expenses_reimbursed",
        "ca/t929_weeks_attended",
        "ca/t929_net_research_grants",
        "ca/t929_earnings_supplements",
        "ca/t929_employment_insurance_part_2_support",
        "ca/t929_income_replacement_support",
        "ca/t929_wage_earner_protection_amounts",
        "ca/t929_covid_19_payments",
    }
)

# The return's own artifacts the form's copies read, and the other forms' exports they read.
IMPORTS = frozenset(
    {
        "ca/t1139_return.t1139_business_income_on_return",
        "ca/t1139_return.t1139_professional_income_on_return",
        "ca/t1139_return.t1139_commission_income_on_return",
        "ca/t1139_return.t1139_farming_income_on_return",
        "ca/t1139_return.t1139_fishing_income_on_return",
        "ca/t1139_return.t1139_business_profit_on_return",
        "ca/t1139_return.t1139_professional_profit_on_return",
        "ca/t1139_return.t1139_commission_profit_on_return",
        "ca/t1139_return.t1139_farming_profit_on_return",
        "ca/t1139_return.t1139_fishing_profit_on_return",
        "ca/t2017.t2017_line_31",
        "ca/t746.t746_deduction",
        "ca/t1043.t1043_deduction",
        "ca/t1_m.moving_expenses_claim",
        "ca/t776.net_rental_income",
        "ca/t1206_share_dispositions.t1206_under_18_dividend_amount",
        "ca/t1206_share_dispositions.t1206_part_1_line_3_amount",
        "ca/schedule_8.cpp_part_5_line_88",
        "ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return",
        "ca/rc381.rc381_cpp_deduction_on_self_employment_and_other_earnings",
        "ca/rc381.rc381_cpp_enhanced_contributions_on_return",
        "ca/t1032.t1032_line_22_checked",
        "ca/t1032.t1032_filer_is_transferring_spouse_checked",
        "ca/t2205.t2205_line_11_rrsp_part",
        "ca/t2205.t2205_line_11_spp_part_checked",
        "ca/t2205.t2205_line_22",
    }
)

# The form exports its computed lines 3, 4, 7, 9, 10 and 11 and line 12 (the deduction).
FORM_EXPORTS = (
    "ca/t929_line_3",
    "ca/t929_line_4",
    "ca/t929_line_7",
    "ca/t929_line_9",
    "ca/t929_line_10",
    "ca/t929_line_11",
    "ca/disability_supports_deduction",
)

# The return's outputs: none, the deduction is read by the steps that follow it on the return.
OUTPUTS = frozenset[str]()

# The derived record lists of the form's exports, one record for each instance of the form.
T929_LINE_3_PER_INSTANCE = RecordListKind("ca/t929.t929_line_3", fields=(T929_LINE_3,))
T929_LINE_4_PER_INSTANCE = RecordListKind("ca/t929.t929_line_4", fields=(T929_LINE_4,))
T929_LINE_7_PER_INSTANCE = RecordListKind("ca/t929.t929_line_7", fields=(T929_LINE_7,))
T929_LINE_9_PER_INSTANCE = RecordListKind("ca/t929.t929_line_9", fields=(T929_LINE_9,))
T929_LINE_10_PER_INSTANCE = RecordListKind("ca/t929.t929_line_10", fields=(T929_LINE_10,))
T929_LINE_11_PER_INSTANCE = RecordListKind("ca/t929.t929_line_11", fields=(T929_LINE_11,))
DISABILITY_SUPPORTS_DEDUCTION_PER_INSTANCE = RecordListKind(
    "ca/t929.disability_supports_deduction", fields=(DISABILITY_SUPPORTS_DEDUCTION,)
)

# The form's own steps: lines 3, 4 (with its five net self-employment and professional items and
# its six inputs), 7, 9, 10, 11 and 12 (the deduction), in the form's order.
OWN_STEPS = {
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/t929_expenses_paid", "less": "ca/t929_expenses_reimbursed"},
        produces={"output": "ca/t929_line_3"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_profit_on_return"},
        produces={"output": "ca/t929_net_business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_profit_on_return"},
        produces={"output": "ca/t929_net_farming_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_profit_on_return"},
        produces={"output": "ca/t929_net_fishing_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_profit_on_return"},
        produces={"output": "ca/t929_net_professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_profit_on_return"},
        produces={"output": "ca/t929_net_commission_income"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/employment_income",
                "ca/other_employment_income",
                "ca/taxable_scholarships",
                "ca/t929_net_business_income",
                "ca/t929_net_farming_income",
                "ca/t929_net_fishing_income",
                "ca/t929_net_professional_income",
                "ca/t929_net_commission_income",
                "ca/t929_net_research_grants",
                "ca/t929_earnings_supplements",
                "ca/t929_employment_insurance_part_2_support",
                "ca/t929_income_replacement_support",
                "ca/t929_wage_earner_protection_amounts",
                "ca/t929_covid_19_payments",
            )
        },
        produces={"output": "ca/t929_line_4"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/net_income", "less": "ca/t929_line_4"},
        produces={"output": "ca/t929_line_7"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/t929_weekly_amount"},
        consumes={"count": "ca/t929_weeks_attended"},
        produces={"output": "ca/t929_line_9"},
    ),
    CapabilitySelection(
        name="ca/lesser_of_with_maximum",
        params={"maximum": "ca/t929_maximum"},
        consumes={"amounts": ("ca/t929_line_7", "ca/t929_line_9")},
        produces={"output": "ca/t929_line_10"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/t929_line_4", "ca/t929_line_10")},
        produces={"output": "ca/t929_line_11"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/t929_line_3", "ca/t929_line_11")},
        produces={"output": "ca/disability_supports_deduction"},
    ),
    # Schedule 15 Step 2 flag, checked in the form that reads it
    # (`05t_t929_yes_or_no_flag_check.yaml`), as a count of 1 or 0, before the copied FHSA steps
    # read the checked count.
    CapabilitySelection(
        name="ca/yes_or_no_count",
        params={},
        consumes={"count": "ca/fhsa_maximum_participation_period_ended"},
        produces={"output": "ca/fhsa_maximum_participation_period_ended_checked"},
    ),
}

# The copies of the return's steps that compute the net income of line 23600 (line 5), with the
# comments of their originals, from the return's manifest parts `05l_t929_copies_1.yaml`,
# `05m_t929_copies_2.yaml` and `05x_t929_copies_3.yaml`.
COPIED_STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1206_share_dispositions.t1206_under_18_dividend_amount"},
        produces={"output": "ca/t1206_under_18_dividend_amount"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1206_share_dispositions.t1206_part_1_line_3_amount"},
        produces={"output": "ca/t1206_part_1_line_3_amount"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/split_income_dividends", "ca/t1206_under_18_dividend_amount")},
        produces={"output": "ca/split_income_dividends_total"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/other_split_income", "ca/t1206_part_1_line_3_amount")},
        produces={"output": "ca/other_split_income_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t746.t746_deduction"},
        produces={"output": "ca/t746_deduction_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1043.t1043_deduction"},
        produces={"output": "ca/t1043_deduction_on_return"},
    ),
    CapabilitySelection(
        name="ca/foreign_property_tax_over_limit",
        params={"limit_rate": "ca/foreign_property_income_credit_limit_rate"},
        consumes={"countries": "ca/foreign_tax_countries"},
        produces={"output": "ca/foreign_property_tax_over_limit"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/qsbcs_dispositions"},
        produces={"output": "ca/qsbcs_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/qffp_dispositions"},
        produces={"output": "ca/qffp_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/qffp_foreclosure_dispositions"},
        produces={"output": "ca/qffp_foreclosure_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/share_dispositions"},
        produces={"output": "ca/share_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/depreciable_property_gains",
        params={},
        consumes={"dispositions": "ca/real_estate_dispositions"},
        produces={"output": "ca/real_estate_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/bond_dispositions"},
        produces={"output": "ca/bond_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/crypto_asset_dispositions"},
        produces={"output": "ca/crypto_asset_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/qffp_gains",
        params={},
        consumes={"dispositions": "ca/other_foreclosure_dispositions"},
        produces={"output": "ca/other_foreclosure_gain_or_loss"},
    ),
    CapabilitySelection(
        name="ca/personal_use_property_gains",
        params={"minimum": "ca/personal_use_property_minimum"},
        consumes={"dispositions": "ca/personal_use_property_dispositions"},
        produces={"output": "ca/personal_use_property_gain_rows"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/personal_use_property_gain_rows", "ca/principal_residence_line_57")
        },
        produces={"output": "ca/personal_use_property_gain"},
    ),
    CapabilitySelection(
        name="ca/disposition_gains",
        params={},
        consumes={"dispositions": "ca/listed_personal_property_dispositions"},
        produces={"output": "ca/listed_personal_property_gain_or_loss"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/listed_personal_property_gain_or_loss",
            "less": "ca/unapplied_listed_personal_property_losses",
        },
        produces={"output": "ca/listed_personal_property_net_gain"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/qsbcs_gain_or_loss",
                "ca/qffp_gain_or_loss",
                "ca/qffp_foreclosure_gain_or_loss",
                "ca/share_gain_or_loss",
                "ca/real_estate_gain_or_loss",
                "ca/bond_gain_or_loss",
                "ca/crypto_asset_gain_or_loss",
                "ca/other_foreclosure_gain_or_loss",
                "ca/personal_use_property_gain",
                "ca/listed_personal_property_net_gain",
            )
        },
        produces={"output": "ca/capital_gains_of_qualified_and_other_properties"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_of_qualified_and_other_properties",
            "less": "ca/capital_gains_deferral_checked",
        },
        produces={"output": "ca/capital_gains_after_deferral"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/capital_gains_after_deferral",
                "ca/slip_capital_gains_or_losses",
                "ca/t3_capital_gains_or_losses",
            )
        },
        produces={"output": "ca/capital_gains_before_investment_loss_reduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_before_investment_loss_reduction",
            "less": "ca/business_investment_loss_reduction",
        },
        produces={"output": "ca/capital_gains_before_reserves"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2017.t2017_line_31"},
        produces={"output": "ca/schedule_3_line_19200"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/capital_gains_before_reserves", "ca/schedule_3_line_19200")},
        produces={"output": "ca/capital_gain"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/capital_gains_inclusion_rate"},
        consumes={"base": "ca/capital_gain"},
        produces={"output": "ca/included_capital_gain"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/included_capital_gain", "ca/partnership_gains_at_full_inclusion")},
        produces={"output": "ca/taxable_capital_gains"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_taxable_dividends",
                "ca/t4ps_taxable_dividends",
                "ca/t5_taxable_dividends",
                "ca/t5013_taxable_dividends",
            )
        },
        produces={"output": "ca/slip_taxable_dividends"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/eligible_dividend_gross_up"},
        consumes={"base": "ca/eligible_dividends_received_without_a_slip"},
        produces={"output": "ca/eligible_dividends_grossed_up"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/other_dividend_gross_up"},
        consumes={"base": "ca/other_dividends_received_without_a_slip"},
        produces={"output": "ca/other_dividends_grossed_up"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/eligible_dividends_grossed_up", "ca/other_dividends_grossed_up")},
        produces={"output": "ca/dividends_without_a_slip_grossed_up"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/slip_taxable_dividends",
                "ca/dividends_without_a_slip_grossed_up",
                "ca/t1206_under_18_dividend_amount",
            )
        },
        produces={"output": "ca/taxable_dividends"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_investment_income",
                "ca/t5_investment_income",
                "ca/t5013_investment_income",
                "ca/investment_income_credited_not_received",
                "ca/tax_refund_interest",
                "ca/foreign_investment_income",
                "ca/investment_income_without_a_slip",
                "ca/investment_royalties",
            )
        },
        produces={"output": "ca/investment_income_before_prior_years"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/investment_income_reported_in_previous_years",
            "bound": "ca/investment_income_before_prior_years",
        },
        produces={"output": "ca/investment_income_reported_in_previous_years_applied"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/investment_income_before_prior_years",
            "less": "ca/investment_income_reported_in_previous_years_applied",
        },
        produces={"output": "ca/interest_and_other_investment_income"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/workers_compensation_benefits",
                "ca/social_assistance_payments",
                "ca/net_federal_supplements",
            )
        },
        produces={"output": "ca/income_support_benefits"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.net_rental_income"},
        produces={"output": "ca/net_rental_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_business_income_on_return"},
        produces={"output": "ca/business_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_professional_income_on_return"},
        produces={"output": "ca/professional_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_commission_income_on_return"},
        produces={"output": "ca/commission_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_farming_income_on_return"},
        produces={"output": "ca/farming_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1139_return.t1139_fishing_income_on_return"},
        produces={"output": "ca/fishing_income"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1_m.moving_expenses_claim"},
        produces={"output": "ca/moving_expenses_deduction"},
    ),
    # Form T2205's routing (`03v_t2205_routing.yaml`), copied: the copy counts "65 or older at the
    # end of the year" from the input (born in 1960 or earlier), as the form cannot read the
    # return's checked count.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2205.t2205_line_11_rrsp_part"},
        produces={"output": "ca/t2205_on_line_12900"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2205.t2205_line_11_spp_part_checked"},
        produces={"output": "ca/t2205_spp_part_total"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2205.t2205_line_22"},
        produces={"output": "ca/t2205_line_22_total"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t2205_spp_part_total", "count": "ca/born_in_1960_or_earlier"},
        produces={"output": "ca/t2205_spp_part_on_line_11500"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t2205_spp_part_total",
            "less": "ca/t2205_spp_part_on_line_11500",
        },
        produces={"output": "ca/t2205_spp_part_on_line_13000"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/t2205_line_22_total", "count": "ca/born_in_1960_or_earlier"},
        produces={"output": "ca/t2205_line_22_on_line_11500"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t2205_line_22_total",
            "less": "ca/t2205_line_22_on_line_11500",
        },
        produces={"output": "ca/t2205_line_22_on_line_13000"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t2205_spp_part_on_line_11500",
                "ca/t2205_line_22_on_line_11500",
            )
        },
        produces={"output": "ca/t2205_on_line_11500"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t2205_spp_part_on_line_13000",
                "ca/t2205_line_22_on_line_13000",
            )
        },
        produces={"output": "ca/t2205_on_line_13000"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/employment_income",
                "ca/other_employment_income",
                "ca/old_age_security",
                "ca/cpp_or_qpp_benefits",
                "ca/other_pensions_and_superannuation",
                "ca/t2205_on_line_11500",
                "ca/elected_split_pension_amount",
                "ca/universal_child_care_benefit",
                "ca/ei_and_other_benefits",
                "ca/taxable_dividends",
                "ca/interest_and_other_investment_income",
                "ca/net_partnership_income",
                "ca/rdsp_income",
                "ca/net_rental_income",
                "ca/taxable_capital_gains",
                "ca/taxable_support_payments",
                "ca/rrsp_income",
                "ca/t2205_on_line_12900",
                "ca/fhsa_income",
                "ca/other_fhsa_income",
                "ca/other_income",
                "ca/t2205_on_line_13000",
                "ca/taxable_scholarships",
                "ca/net_self_employment_income",
                "ca/income_support_benefits",
            )
        },
        produces={"output": "ca/total_income"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/business_income",
                "ca/professional_income",
                "ca/commission_income",
                "ca/farming_income",
                "ca/fishing_income",
            )
        },
        produces={"output": "ca/net_self_employment_income"},
    ),
    CapabilitySelection(
        name="ca/principal_residence_line_57",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_57"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/unused_rrsp_contributions", "ca/rrsp_contributions")},
        produces={"output": "ca/rrsp_contributions_available"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/rrsp_contributions_available", "ca/rrsp_deduction_limit")},
        produces={"output": "ca/rrsp_deduction_maximum"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/rrsp_amount_deducted", "bound": "ca/rrsp_deduction_maximum"},
        produces={"output": "ca/rrsp_deduction"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal",
            "bound": "ca/fhsa_contributions_in_2025",
        },
        produces={
            "output": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked"
        },
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2025",
            "less": "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked",
        },
        produces={"output": "ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_contributions_in_2025_before_first_qualifying_withdrawal",
                "ca/fhsa_variable_b_amount",
            )
        },
        produces={"output": "ca/fhsa_contributions_plus_variable_b_amount"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal",
            "bound": "ca/fhsa_contributions_in_2024",
        },
        produces={
            "output": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked"
        },
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_in_2024",
            "less": "ca/fhsa_contributions_in_2024_before_first_qualifying_withdrawal_checked",
        },
        produces={"output": "ca/fhsa_contributions_in_2024_after_first_qualifying_withdrawal"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_contributions_in_2024_after_first_qualifying_withdrawal",
                "ca/fhsa_contributions_in_2025_after_first_qualifying_withdrawal_checked",
            )
        },
        produces={"output": "ca/fhsa_contributions_after_first_qualifying_withdrawal"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_designated_withdrawals_in_2025",
            "less": "ca/fhsa_contributions_after_first_qualifying_withdrawal",
        },
        produces={"output": "ca/fhsa_excess_designated_withdrawals"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_contributions_plus_variable_b_amount",
            "less": "ca/fhsa_excess_designated_withdrawals",
        },
        produces={"output": "ca/fhsa_contributions_limit"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_amount"},
        consumes={},
        produces={"output": "ca/fhsa_annual_amount"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_annual_amount", "ca/fhsa_carryforward_for_2025")},
        produces={"output": "ca/fhsa_annual_amount_with_carryforward"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_rrsp_transfers_in_2024_and_prior_years",
                "ca/fhsa_rrsp_transfers_in_2025",
            )
        },
        produces={"output": "ca/fhsa_total_rrsp_transfers"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/fhsa_designated_transfers_in_2024_and_prior_years",
                "ca/fhsa_designated_transfers_in_2025",
            )
        },
        produces={"output": "ca/fhsa_total_designated_transfers"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_total_rrsp_transfers",
            "less": "ca/fhsa_total_designated_transfers",
        },
        produces={"output": "ca/fhsa_net_rrsp_transfer_amount"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_rrsp_transfers_in_2024_and_prior_years",
            "less": "ca/fhsa_designated_transfers_in_2024_and_prior_years",
        },
        produces={"output": "ca/fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_net_rrsp_transfer_amount_for_2024_and_prior_years",
            "less": "ca/fhsa_variable_h_amount",
        },
        produces={"output": "ca/fhsa_net_transfer_amount_less_variable_h_amount"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_amount"},
        consumes={},
        produces={"output": "ca/fhsa_annual_amount_for_2024"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_annual_amount_for_2024", "ca/fhsa_carryforward_for_2024")},
        produces={"output": "ca/fhsa_annual_amount_for_2024_with_carryforward"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/fhsa_net_transfer_amount_less_variable_h_amount",
                "ca/fhsa_annual_amount_for_2024_with_carryforward",
            )
        },
        produces={"output": "ca/fhsa_transfer_amount_at_most_limit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/fhsa_transfer_amount_at_most_limit", "ca/fhsa_variable_f_amount")},
        produces={"output": "ca/fhsa_transfer_amount_plus_variable_f_amount"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_net_rrsp_transfer_amount",
            "less": "ca/fhsa_transfer_amount_plus_variable_f_amount",
        },
        produces={"output": "ca/fhsa_net_transfer_amount_after_prior_years"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_annual_amount_with_carryforward",
            "less": "ca/fhsa_net_transfer_amount_after_prior_years",
        },
        produces={"output": "ca/fhsa_annual_amount_after_transfers"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/fhsa_contributions_limit", "ca/fhsa_annual_amount_after_transfers")
        },
        produces={"output": "ca/fhsa_annual_limit_from_step_2"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_annual_limit_after_maximum_participation_period"},
        consumes={},
        produces={"output": "ca/fhsa_annual_limit_after_maximum_participation_period"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/fhsa_maximum_participation_period_ended_checked",
            "when_none": "ca/fhsa_annual_limit_from_step_2",
            "when_any": "ca/fhsa_annual_limit_after_maximum_participation_period",
        },
        produces={"output": "ca/fhsa_annual_limit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/fhsa_annual_limit", "ca/fhsa_annual_limits_for_2024_and_prior_years")
        },
        produces={"output": "ca/fhsa_total_annual_limits"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/fhsa_deductions_for_2024_and_prior_years",
            "bound": "ca/fhsa_annual_limits_for_2024_and_prior_years",
        },
        produces={"output": "ca/fhsa_deductions_for_2024_and_prior_years_checked"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_total_annual_limits",
            "less": "ca/fhsa_deductions_for_2024_and_prior_years_checked",
        },
        produces={"output": "ca/fhsa_annual_limits_less_deductions"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/fhsa_lifetime_limit"},
        consumes={},
        produces={"output": "ca/fhsa_lifetime_limit"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/fhsa_lifetime_limit",
            "less": "ca/fhsa_deductions_for_2024_and_prior_years_checked",
        },
        produces={"output": "ca/fhsa_lifetime_limit_less_deductions"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/fhsa_lifetime_limit_less_deductions",
            "less": "ca/fhsa_net_rrsp_transfer_amount",
        },
        produces={"output": "ca/fhsa_lifetime_limit_less_deductions_and_transfers"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/fhsa_annual_limits_less_deductions",
                "ca/fhsa_lifetime_limit_less_deductions_and_transfers",
            )
        },
        produces={"output": "ca/fhsa_maximum_deduction"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/fhsa_contributions_deducted", "bound": "ca/fhsa_maximum_deduction"},
        produces={"output": "ca/fhsa_deduction"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_maximum_pensionable_earnings"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_maximum_pensionable_earnings"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_additional_maximum_pensionable_earnings"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_additional_maximum_pensionable_earnings"},
    ),
    CapabilitySelection(
        name="core/amount_by_count",
        params={"table": "ca/cpp_basic_exemption"},
        consumes={"count": "ca/cpp_months"},
        produces={"output": "ca/cpp_basic_exemption"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/net_partnership_income", "ca/net_self_employment_income")},
        produces={"output": "ca/pensionable_net_self_employment_earnings"},
    ),
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/pensionable_net_self_employment_earnings", "ca/cpt20_earnings")},
        produces={"output": "ca/cpp_pensionable_earnings"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/cpp_additional_maximum_pensionable_earnings",
                "ca/cpp_pensionable_earnings",
            )
        },
        produces={"output": "ca/cpp_pensionable_earnings_up_to_additional_maximum"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_pensionable_earnings_up_to_additional_maximum",
            "less": "ca/cpp_maximum_pensionable_earnings",
        },
        produces={"output": "ca/cpp_earnings_subject_to_second_additional"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/cpp_pensionable_earnings_up_to_additional_maximum",
            "less": "ca/cpp_earnings_subject_to_second_additional",
        },
        produces={"output": "ca/cpp_earnings_up_to_maximum"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/cpp_earnings_up_to_maximum", "less": "ca/cpp_basic_exemption"},
        produces={"output": "ca/cpp_earnings_subject_to_base_and_first_additional"},
    ),
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_base_contribution"},
        consumes={"earnings": "ca/cpp_earnings_subject_to_base_and_first_additional"},
        produces={"output": "ca/self_employed_cpp_base_contributions"},
    ),
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_first_additional_contribution"},
        consumes={"earnings": "ca/cpp_earnings_subject_to_base_and_first_additional"},
        produces={"output": "ca/self_employed_cpp_first_additional_contributions"},
    ),
    CapabilitySelection(
        name="core/contribution_tier",
        params={"tier": "ca/cpp_self_employed_second_additional_contribution"},
        consumes={"earnings": "ca/cpp_earnings_subject_to_second_additional"},
        produces={"output": "ca/self_employed_cpp_second_additional_contributions"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/self_employed_cpp_first_additional_contributions",
                "ca/self_employed_cpp_second_additional_contributions",
            )
        },
        produces={"output": "ca/self_employed_cpp_enhanced_contributions"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/cpp_self_employed_base_credit_rate"},
        consumes={"base": "ca/self_employed_cpp_base_contributions"},
        produces={"output": "ca/self_employed_cpp_base_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/self_employed_cpp_base_credit",
                "ca/self_employed_cpp_enhanced_contributions",
            )
        },
        produces={"output": "ca/self_employed_cpp_deduction"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/self_employed_cpp_deduction", "count": "ca/cpp_part_4_completed"},
        produces={"output": "ca/cpp_deduction_on_self_employment"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={"amount": "ca/cpp_part_5_line_88", "count": "ca/cpp_part_5_completed"},
        produces={"output": "ca/cpp_part_5_deduction_on_self_employment"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/cpp_deduction_on_self_employment",
                "ca/cpp_part_5_deduction_on_self_employment",
                "ca/rc381_cpp_deduction_on_self_employment_and_other_earnings",
            )
        },
        produces={"output": "ca/cpp_deduction_on_self_employment_and_other_earnings"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/child_care_limit_under_seven"},
        consumes={"count": "ca/children_under_seven"},
        produces={"output": "ca/child_care_limit_for_children_under_seven"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/child_care_limit_disability"},
        consumes={"count": "ca/children_with_disability"},
        produces={"output": "ca/child_care_limit_for_children_with_disability"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/child_care_limit_seven_to_sixteen"},
        consumes={"count": "ca/children_seven_to_sixteen"},
        produces={"output": "ca/child_care_limit_for_children_seven_to_sixteen"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/child_care_limit_for_children_under_seven",
                "ca/child_care_limit_for_children_with_disability",
                "ca/child_care_limit_for_children_seven_to_sixteen",
            )
        },
        produces={"output": "ca/child_care_basic_limit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/employment_income",)},
        produces={"output": "ca/child_care_earned_income"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/child_care_earned_income_fraction"},
        consumes={"base": "ca/child_care_earned_income"},
        produces={"output": "ca/child_care_earned_income_limit"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/child_care_basic_limit",
                "ca/child_care_expenses_paid",
                "ca/child_care_earned_income_limit",
            )
        },
        produces={"output": "ca/child_care_expenses"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/total_carrying_charges",
                "ca/total_interest_expenses",
                "ca/total_other_expenses",
            )
        },
        produces={"output": "ca/carrying_charges_interest_expenses_and_other_expenses"},
    ),
    # Chart A row "In 2000", column (B) "1/(IR × 2)": the printed 1 of the factor, as an artifact;
    # line 5 of T1436 reads it, as the return's copy of the step does.
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/net_capital_loss_numerator_one_2000"},
        consumes={},
        produces={"output": "ca/net_capital_loss_numerator_one_2000"},
    ),
    # Schedule 3 lines 543 and 544, summed (lines 2 and 3 of T1436).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/schedule_3_line_543", "ca/schedule_3_line_544")},
        produces={"output": "ca/schedule_3_lines_543_and_544_total"},
    ),
    # Line 2 (a): the amount entered less the Schedule 3 sum, not below 0.
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": (
                "ca/capital_gains_deductions_1988_and_1989_other_than_eligible_capital_property"
            ),
            "less": "ca/schedule_3_lines_543_and_544_total",
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_amount_a"},
    ),
    # Line 1, x 2.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_1_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1985_to_1987"},
        produces={"output": "ca/capital_gains_deductions_line_1"},
    ),
    # Line 2, x 1.5.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_2_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1988_and_1989_amount_a"},
        produces={"output": "ca/capital_gains_deductions_line_2"},
    ),
    # Line 3, the amount entered less amount (a), signed.
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_deductions_1988_and_1989_eligible_capital_property",
            "less": "ca/capital_gains_deductions_1988_and_1989_amount_a",
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_after_amount_a"},
    ),
    # Line 3, the lesser of that difference and the Schedule 3 sum.
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/capital_gains_deductions_1988_and_1989_after_amount_a",
                "ca/schedule_3_lines_543_and_544_total",
            )
        },
        produces={"output": "ca/capital_gains_deductions_1988_and_1989_limited"},
    ),
    # Line 3, x 1.3333.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_3_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1988_and_1989_limited"},
        produces={"output": "ca/capital_gains_deductions_line_3"},
    ),
    # Line 4, x 1.3333.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_4_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_1990_to_1999"},
        produces={"output": "ca/capital_gains_deductions_line_4"},
    ),
    # Line 5, x 1/IR, rounded half-up to the cent; 0 when IR is 0.
    CapabilitySelection(
        name="ca/apply_ratio_or_zero",
        params={"rounding": "ca/t1436_line_5_rounding"},
        consumes={
            "amount": "ca/capital_gains_deductions_2000",
            "numerator": "ca/net_capital_loss_numerator_one_2000",
            "denominator": "ca/t657_inclusion_rate_2000",
        },
        produces={"output": "ca/capital_gains_deductions_line_5"},
    ),
    # Line 6, x 2.
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/t1436_line_6_multiplier"},
        consumes={"base": "ca/capital_gains_deductions_2001_to_2024"},
        produces={"output": "ca/capital_gains_deductions_line_6"},
    ),
    # Line 7, "Add lines 1 to 6.": the six lines after their multipliers.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/capital_gains_deductions_line_1",
                "ca/capital_gains_deductions_line_2",
                "ca/capital_gains_deductions_line_3",
                "ca/capital_gains_deductions_line_4",
                "ca/capital_gains_deductions_line_5",
                "ca/capital_gains_deductions_line_6",
            )
        },
        produces={"output": "ca/capital_gains_deductions_claimed_1985_to_2024"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/other_business_investment_loss_reductions_1986_to_1994",
                "ca/other_business_investment_loss_reductions_1994_to_1996",
                "ca/other_business_investment_loss_reductions_1997_to_1999",
                "ca/other_business_investment_loss_reductions_2000",
                "ca/other_business_investment_loss_reductions_2001_to_2023",
                "ca/other_business_investment_loss_reductions_2024",
            )
        },
        produces={"output": "ca/other_business_investment_loss_reductions_1986_to_2024"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_deductions_claimed_1985_to_2024",
            "less": "ca/other_business_investment_loss_reductions_1986_to_2024",
        },
        produces={"output": "ca/business_investment_loss_reduction_available"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": (
                "ca/business_investment_loss_reduction_available",
                "ca/business_investment_loss",
            )
        },
        produces={"output": "ca/business_investment_loss_reduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/business_investment_loss",
            "less": "ca/business_investment_loss_reduction",
        },
        produces={"output": "ca/business_investment_loss_after_reduction"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/business_investment_loss_inclusion_rate"},
        consumes={"base": "ca/business_investment_loss_after_reduction"},
        produces={"output": "ca/allowable_business_investment_loss"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/rpp_deduction",
                "ca/rrsp_deduction",
                "ca/fhsa_deduction",
                "ca/elected_split_pension_deduction",
                "ca/union_dues",
                "ca/uccb_repayment",
                "ca/child_care_expenses",
                "ca/allowable_business_investment_loss",
                "ca/moving_expenses_deduction",
                "ca/support_payments_deduction",
                "ca/carrying_charges_interest_expenses_and_other_expenses",
                "ca/cpp_deduction_on_self_employment_and_other_earnings",
                "ca/cpp_enhanced_contributions_on_return",
                "ca/exploration_and_development_expenses",
                "ca/clergy_residence_deduction",
                "ca/other_deductions",
                "ca/t746_deduction_on_return",
                "ca/t1043_deduction_on_return",
                "ca/foreign_property_tax_over_limit",
                "ca/total_split_income",
            )
        },
        produces={"output": "ca/deductions_from_total_income"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/total_income", "less": "ca/deductions_from_total_income"},
        produces={"output": "ca/net_income_before_adjustments"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/net_income_before_adjustments",
            "less": "ca/social_benefits_repayment",
        },
        produces={"output": "ca/net_income"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/split_income_dividends_total", "bound": "ca/taxable_dividends"},
        produces={"output": "ca/split_income_dividends_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/split_income_dividends_checked", "ca/other_split_income_total")},
        produces={"output": "ca/total_split_income"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/social_benefits_repayment_conditions"},
        consumes={
            "counts": (),
            "amounts": (
                "ca/ei_and_other_benefits",
                "ca/net_income_before_adjustments",
                "ca/old_age_security",
                "ca/net_federal_supplements",
            ),
        },
        produces={"output": "ca/social_benefits_repayment_applies"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/old_age_security", "ca/net_federal_supplements")},
        produces={"output": "ca/oas_and_federal_supplements"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={
            "amount": "ca/oas_and_federal_supplements",
            "less": "ca/oas_overpayment_recovered",
        },
        produces={"output": "ca/social_benefits_line_5"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/net_income_before_adjustments", "ca/total_split_income")},
        produces={"output": "ca/social_benefits_line_6"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/ei_benefits_repayment", "bound": "ca/ei_and_other_benefits"},
        produces={"output": "ca/ei_benefits_repayment_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/ei_benefits_repayment_checked",
                "ca/universal_child_care_benefit",
                "ca/rdsp_income",
            )
        },
        produces={"output": "ca/social_benefits_line_10"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/social_benefits_line_6", "less": "ca/social_benefits_line_10"},
        produces={"output": "ca/social_benefits_line_11"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={"amount": "ca/rdsp_income_repayment", "bound": "ca/other_deductions"},
        produces={"output": "ca/rdsp_income_repayment_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/uccb_repayment", "ca/rdsp_income_repayment_checked")},
        produces={"output": "ca/social_benefits_line_14"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/social_benefits_line_11", "ca/social_benefits_line_14")},
        produces={"output": "ca/social_benefits_line_15"},
    ),
    CapabilitySelection(
        name="core/credit_amount",
        params={"amount": "ca/oas_benefits_base_amount"},
        consumes={},
        produces={"output": "ca/oas_benefits_base_amount"},
    ),
    CapabilitySelection(
        name="core/subtract_not_below_zero",
        params={},
        consumes={"amount": "ca/social_benefits_line_15", "less": "ca/oas_benefits_base_amount"},
        produces={"output": "ca/social_benefits_line_17"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/social_benefits_repayment_rate"},
        consumes={"base": "ca/social_benefits_line_17"},
        produces={"output": "ca/social_benefits_line_18"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/social_benefits_line_5", "ca/social_benefits_line_18")},
        produces={"output": "ca/social_benefits_line_19"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/social_benefits_line_19", "ca/ei_benefits_repayment_checked")},
        produces={"output": "ca/social_benefits_line_21"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/social_benefits_line_21",
            "count": "ca/social_benefits_repayment_applies",
        },
        produces={"output": "ca/social_benefits_repayment"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.schedule_8_cpp_enhanced_contributions_on_return"},
        produces={"output": "ca/schedule_8_cpp_enhanced_contributions_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/schedule_8.cpp_part_5_line_88"},
        produces={"output": "ca/cpp_part_5_line_88"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
                "ca/rc381_cpp_enhanced_contributions_on_return",
            )
        },
        produces={"output": "ca/cpp_enhanced_contributions_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/rc381.rc381_cpp_enhanced_contributions_on_return"},
        produces={"output": "ca/rc381_cpp_enhanced_contributions_on_return"},
    ),
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/rc381.rc381_cpp_deduction_on_self_employment_and_other_earnings"},
        produces={"output": "ca/rc381_cpp_deduction_on_self_employment_and_other_earnings"},
    ),
    CapabilitySelection(
        name="core/apply_fraction",
        params={"fraction": "ca/clergy_residence_fraction"},
        consumes={"base": "ca/clergy_qualifying_employment_income"},
        produces={"output": "ca/clergy_residence_line_2"},
    ),
    CapabilitySelection(
        name="core/per_unit_amount",
        params={"amount": "ca/clergy_residence_per_month"},
        consumes={"count": "ca/clergy_months_in_qualifying_employment"},
        produces={"output": "ca/clergy_residence_months_amount"},
    ),
    CapabilitySelection(
        name="core/capped_amount",
        params={"cap": "ca/clergy_residence_months_maximum"},
        consumes={"base": "ca/clergy_residence_months_amount"},
        produces={"output": "ca/clergy_residence_line_4"},
    ),
    CapabilitySelection(
        name="core/greater_of",
        params={},
        consumes={"amounts": ("ca/clergy_residence_line_2", "ca/clergy_residence_line_4")},
        produces={"output": "ca/clergy_residence_line_5"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/clergy_other_accommodation_claims",
            "bound": "ca/clergy_accommodation_cost",
        },
        produces={"output": "ca/clergy_other_accommodation_claims_checked"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/clergy_accommodation_cost",
            "less": "ca/clergy_other_accommodation_claims_checked",
        },
        produces={"output": "ca/clergy_residence_line_8"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={"amounts": ("ca/clergy_residence_line_5", "ca/clergy_residence_line_8")},
        produces={"output": "ca/clergy_residence_line_9"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/clergy_qualifying_employment_income", "ca/clergy_residence_line_9")
        },
        produces={"output": "ca/clergy_residence_line_10"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/clergy_employer_residence_benefit",
            "bound": "ca/other_employment_income",
        },
        produces={"output": "ca/clergy_employer_residence_benefit_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/clergy_employer_residence_benefit_checked",
                "ca/clergy_residence_line_10",
            )
        },
        produces={"output": "ca/clergy_residence_total"},
    ),
    CapabilitySelection(
        name="core/lesser_of",
        params={},
        consumes={
            "amounts": ("ca/clergy_residence_total", "ca/clergy_qualifying_employment_income")
        },
        produces={"output": "ca/clergy_residence_total_limited"},
    ),
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/clergy_residence_part_b_conditions"},
        consumes={
            "counts": ("ca/clergy_months_in_qualifying_employment",),
            "amounts": ("ca/clergy_accommodation_cost", "ca/clergy_other_accommodation_claims"),
        },
        produces={"output": "ca/clergy_residence_part_b_completed"},
    ),
    CapabilitySelection(
        name="core/choose_by_count",
        params={},
        consumes={
            "count": "ca/clergy_residence_part_b_completed",
            "when_none": "ca/clergy_residence_total",
            "when_any": "ca/clergy_residence_total_limited",
        },
        produces={"output": "ca/clergy_residence_deduction"},
    ),
    # Schedule 3 line 4 and line 13200 "Total gain or loss (add all the amounts under column 5)",
    # floored at 0: a share loss leaves no share gain for the deferral, so the bound is 0 then.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/share_gain_or_loss",)},
        produces={"output": "ca/share_gain_not_below_zero"},
    ),
    # Schedule 3 line 13 and line 16100 "Capital gains deferral from qualifying dispositions of
    # eligible small business corporation shares included on line 4" is at most line 4, the share
    # gain floored at 0. It is refused above it, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/capital_gains_deferral",
            "bound": "ca/share_gain_not_below_zero",
        },
        produces={"output": "ca/capital_gains_deferral_checked"},
    ),
    # Form T1032 line 22 on T1 line 21000 or line 11600 (copies of 22c_t1032_...).
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t1032.t1032_line_22_checked"},
        produces={"output": "ca/t1032_line_22_total"},
    ),
    CapabilitySelection(
        name="core/first_record_count",
        params={},
        consumes={"records": "ca/t1032.t1032_filer_is_transferring_spouse_checked"},
        produces={"output": "ca/t1032_filer_is_transferring_spouse_total"},
    ),
    CapabilitySelection(
        name="core/times_count",
        params={},
        consumes={
            "amount": "ca/t1032_line_22_total",
            "count": "ca/t1032_filer_is_transferring_spouse_total",
        },
        produces={"output": "ca/elected_split_pension_deduction"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/t1032_line_22_total",
            "less": "ca/elected_split_pension_deduction",
        },
        produces={"output": "ca/elected_split_pension_amount"},
    ),
}

FORM_STEPS = OWN_STEPS | COPIED_STEPS

# The return totals the form's deduction over the one instance (`core/record_total`), before the
# line 23300 sum (`deductions.py`), which adds it.
STEPS = {
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t929.disability_supports_deduction"},
        produces={"output": "ca/disability_supports_deduction"},
    ),
}

# The form's own selections, wired as the composition derives them (the copies are wired as their
# originals on the return, see `test_manifest_t929.py`).
FORM_WIRING = {
    (Subtract, frozenset({T929_EXPENSES_PAID, T929_EXPENSES_REIMBURSED}), frozenset({T929_LINE_3})),
    (
        RecordTotal,
        frozenset({BUSINESS_PROFIT_ON_RETURN_LINES}),
        frozenset({T929_NET_BUSINESS_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FARMING_PROFIT_ON_RETURN_LINES}),
        frozenset({T929_NET_FARMING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({FISHING_PROFIT_ON_RETURN_LINES}),
        frozenset({T929_NET_FISHING_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({PROFESSIONAL_PROFIT_ON_RETURN_LINES}),
        frozenset({T929_NET_PROFESSIONAL_INCOME}),
    ),
    (
        RecordTotal,
        frozenset({COMMISSION_PROFIT_ON_RETURN_LINES}),
        frozenset({T929_NET_COMMISSION_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                EMPLOYMENT_INCOME,
                OTHER_EMPLOYMENT_INCOME,
                TAXABLE_SCHOLARSHIPS,
                T929_NET_BUSINESS_INCOME,
                T929_NET_FARMING_INCOME,
                T929_NET_FISHING_INCOME,
                T929_NET_PROFESSIONAL_INCOME,
                T929_NET_COMMISSION_INCOME,
                T929_NET_RESEARCH_GRANTS,
                T929_EARNINGS_SUPPLEMENTS,
                T929_EMPLOYMENT_INSURANCE_PART_2_SUPPORT,
                T929_INCOME_REPLACEMENT_SUPPORT,
                T929_WAGE_EARNER_PROTECTION_AMOUNTS,
                T929_COVID_19_PAYMENTS,
            }
        ),
        frozenset({T929_LINE_4}),
    ),
    (
        SubtractNotBelowZero,
        frozenset({NET_INCOME, T929_LINE_4}),
        frozenset({T929_LINE_7}),
    ),
    (PerUnitAmount, frozenset({T929_WEEKS_ATTENDED}), frozenset({T929_LINE_9})),
    (
        LesserOfWithMaximum,
        frozenset({T929_LINE_7, T929_LINE_9}),
        frozenset({T929_LINE_10}),
    ),
    (Sum, frozenset({T929_LINE_4, T929_LINE_10}), frozenset({T929_LINE_11})),
    (LesserOf, frozenset({T929_LINE_3, T929_LINE_11}), frozenset({DISABILITY_SUPPORTS_DEDUCTION})),
    (
        YesOrNoCount,
        frozenset({FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED}),
        frozenset({FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED_CHECKED}),
    ),
}

# The return's wiring of the deduction: the record total over the form's derived kind.
WIRING = {
    (
        RecordTotal,
        frozenset({DISABILITY_SUPPORTS_DEDUCTION_PER_INSTANCE}),
        frozenset({DISABILITY_SUPPORTS_DEDUCTION}),
    ),
}
