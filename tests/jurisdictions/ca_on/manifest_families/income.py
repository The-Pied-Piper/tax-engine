"""The CA-ON manifest entries of one family of lines (see `test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_fraction import ApplyFraction
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.subtract import Subtract
from tax_calculator.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.domain.record_list import RecordListKind
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions
from tax_calculator.jurisdictions.ca.capabilities.count_refused_by_conditions import (
    CountRefusedByConditions,
)
from tax_calculator.jurisdictions.ca.capabilities.depreciable_property_gains import (
    DepreciablePropertyGains,
)
from tax_calculator.jurisdictions.ca.capabilities.disposition_gains import DispositionGains
from tax_calculator.jurisdictions.ca.capabilities.disposition_proceeds import DispositionProceeds
from tax_calculator.jurisdictions.ca.capabilities.personal_use_property_gains import (
    PersonalUsePropertyGains,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_gain import (
    PrincipalResidenceGain,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_27 import (
    PrincipalResidencePart2Line27,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_29 import (
    PrincipalResidencePart2Line29,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_30 import (
    PrincipalResidencePart2Line30,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_32 import (
    PrincipalResidencePart2Line32,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_33 import (
    PrincipalResidencePart2Line33,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_38 import (
    PrincipalResidencePart2Line38,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_39 import (
    PrincipalResidencePart2Line39,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_42 import (
    PrincipalResidencePart2Line42,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_44 import (
    PrincipalResidencePart2Line44,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_45 import (
    PrincipalResidencePart2Line45,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_48 import (
    PrincipalResidencePart2Line48,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_51 import (
    PrincipalResidencePart2Line51,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_53 import (
    PrincipalResidencePart2Line53,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_56 import (
    PrincipalResidencePart4Line56,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_line_57 import (
    PrincipalResidencePart4Line57,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_3 import (
    PrincipalResidenceWorksheetLine3Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_6 import (
    PrincipalResidenceWorksheetLine6Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_16 import (
    PrincipalResidenceWorksheetLine16Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_17 import (
    PrincipalResidenceWorksheetLine17Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_18 import (
    PrincipalResidenceWorksheetLine18Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_19 import (
    PrincipalResidenceWorksheetLine19Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_21 import (
    PrincipalResidenceWorksheetLine21Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_23 import (
    PrincipalResidenceWorksheetLine23Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_24 import (
    PrincipalResidenceWorksheetLine24Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_26 import (
    PrincipalResidenceWorksheetLine26Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_27 import (
    PrincipalResidenceWorksheetLine27Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_30 import (
    PrincipalResidenceWorksheetLine30Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_32 import (
    PrincipalResidenceWorksheetLine32Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_33 import (
    PrincipalResidenceWorksheetLine33Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_35 import (
    PrincipalResidenceWorksheetLine35Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_36 import (
    PrincipalResidenceWorksheetLine36Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_40 import (
    PrincipalResidenceWorksheetLine40Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_41 import (
    PrincipalResidenceWorksheetLine41Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_44 import (
    PrincipalResidenceWorksheetLine44Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_46 import (
    PrincipalResidenceWorksheetLine46Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_47 import (
    PrincipalResidenceWorksheetLine47Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_50 import (
    PrincipalResidenceWorksheetLine50Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_53 import (
    PrincipalResidenceWorksheetLine53Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_55 import (
    PrincipalResidenceWorksheetLine55Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_58 import (
    PrincipalResidenceWorksheetLine58Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_59 import (
    PrincipalResidenceWorksheetLine59Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_61 import (
    PrincipalResidenceWorksheetLine61Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_63 import (
    PrincipalResidenceWorksheetLine63Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_64 import (
    PrincipalResidenceWorksheetLine64Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_worksheet_line_66 import (
    PrincipalResidenceWorksheetLine66Capability,
)
from tax_calculator.jurisdictions.ca.capabilities.qffp_gains import QffpGains
from tax_calculator.jurisdictions.ca.catalog import (
    AMT_MINIMUM_TAX_CARRYOVER_APPLIED,
    BOND_DISPOSITIONS,
    BOND_GAIN_OR_LOSS,
    BOND_PROCEEDS,
    BUSINESS_INCOME,
    BUSINESS_INVESTMENT_LOSS_REDUCTION,
    CAPITAL_GAIN,
    CAPITAL_GAINS_AFTER_DEFERRAL,
    CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION,
    CAPITAL_GAINS_BEFORE_RESERVES,
    CAPITAL_GAINS_DEFERRAL,
    CAPITAL_GAINS_DEFERRAL_CHECKED,
    CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES,
    COMMISSION_INCOME,
    CPP_OR_QPP_BENEFITS,
    CREDITS_AGAINST_BASIC_FEDERAL_TAX,
    CRYPTO_ASSET_DISPOSITIONS,
    CRYPTO_ASSET_GAIN_OR_LOSS,
    CRYPTO_ASSET_PROCEEDS,
    DIVIDEND_TAX_CREDIT,
    DIVIDENDS_AMOUNT_A,
    DIVIDENDS_AMOUNT_A_LESS_B,
    DIVIDENDS_AMOUNT_B,
    DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP,
    EI_AND_OTHER_BENEFITS,
    ELECTED_SPLIT_PENSION_AMOUNT,
    ELIGIBLE_DIVIDENDS_CREDIT,
    ELIGIBLE_DIVIDENDS_GROSSED_UP,
    ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
    EMERGENCY_SERVICES_VOLUNTEER_CONFLICT,
    EMERGENCY_SERVICES_VOLUNTEER_CONFLICT_CHECKED,
    EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
    EMPLOYMENT_INCOME,
    FARMING_INCOME,
    FHSA_INCOME,
    FISHING_INCOME,
    FOREIGN_INVESTMENT_INCOME,
    INCLUDED_CAPITAL_GAIN,
    INCOME_SUPPORT_BENEFITS,
    INTEREST_AND_OTHER_INVESTMENT_INCOME,
    INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
    INVESTMENT_INCOME_CREDITED_NOT_RECEIVED,
    INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS,
    INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED,
    INVESTMENT_INCOME_WITHOUT_A_SLIP,
    INVESTMENT_ROYALTIES,
    LISTED_PERSONAL_PROPERTY_DISPOSITIONS,
    LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS,
    LISTED_PERSONAL_PROPERTY_NET_GAIN,
    NET_FEDERAL_SUPPLEMENTS,
    NET_PARTNERSHIP_INCOME,
    NET_RENTAL_INCOME,
    NET_SELF_EMPLOYMENT_INCOME,
    NO_SLIP_DIVIDEND_TAX_CREDIT,
    NON_REFUNDABLE_TAX_CREDITS,
    OLD_AGE_SECURITY,
    OTHER_DIVIDENDS_CREDIT,
    OTHER_DIVIDENDS_GROSSED_UP,
    OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_FHSA_INCOME,
    OTHER_FORECLOSURE_DISPOSITIONS,
    OTHER_FORECLOSURE_GAIN_OR_LOSS,
    OTHER_FORECLOSURE_PROCEEDS,
    OTHER_INCOME,
    OTHER_PENSIONS_AND_SUPERANNUATION,
    PARTNERSHIP_GAINS_AT_FULL_INCLUSION,
    PERSONAL_USE_PROPERTY_DISPOSITIONS,
    PERSONAL_USE_PROPERTY_GAIN,
    PERSONAL_USE_PROPERTY_GAIN_ROWS,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_LINE_27,
    PRINCIPAL_RESIDENCE_LINE_29,
    PRINCIPAL_RESIDENCE_LINE_30,
    PRINCIPAL_RESIDENCE_LINE_32,
    PRINCIPAL_RESIDENCE_LINE_33,
    PRINCIPAL_RESIDENCE_LINE_38,
    PRINCIPAL_RESIDENCE_LINE_39,
    PRINCIPAL_RESIDENCE_LINE_42,
    PRINCIPAL_RESIDENCE_LINE_44,
    PRINCIPAL_RESIDENCE_LINE_45,
    PRINCIPAL_RESIDENCE_LINE_48,
    PRINCIPAL_RESIDENCE_LINE_51,
    PRINCIPAL_RESIDENCE_LINE_53,
    PRINCIPAL_RESIDENCE_LINE_56,
    PRINCIPAL_RESIDENCE_LINE_57,
    PRINCIPAL_RESIDENCE_PROPERTIES,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64,
    PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66,
    PROFESSIONAL_INCOME,
    QFFP_DISPOSITIONS,
    QFFP_FORECLOSURE_DISPOSITIONS,
    QFFP_FORECLOSURE_GAIN_OR_LOSS,
    QFFP_FORECLOSURE_PROCEEDS,
    QFFP_GAIN_OR_LOSS,
    QFFP_PROCEEDS,
    QSBCS_DISPOSITIONS,
    QSBCS_GAIN_OR_LOSS,
    QSBCS_PROCEEDS,
    RDSP_INCOME,
    REAL_ESTATE_DISPOSITIONS,
    REAL_ESTATE_GAIN_OR_LOSS,
    REAL_ESTATE_PROCEEDS,
    RRSP_INCOME,
    SCHEDULE_3_LINE_19200,
    SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
    SHARE_DISPOSITIONS,
    SHARE_GAIN_NOT_BELOW_ZERO,
    SHARE_GAIN_OR_LOSS,
    SHARE_PROCEEDS,
    SLIP_CAPITAL_GAINS_OR_LOSSES,
    SLIP_DIVIDEND_TAX_CREDIT,
    SLIP_TAXABLE_DIVIDENDS,
    SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    SOCIAL_ASSISTANCE_PAYMENTS,
    T3_CAPITAL_GAINS_OR_LOSSES,
    T3_DIVIDEND_TAX_CREDIT,
    T3_INVESTMENT_INCOME,
    T3_TAXABLE_DIVIDENDS,
    T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T4PS_DIVIDEND_TAX_CREDIT,
    T4PS_TAXABLE_DIVIDENDS,
    T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T5_DIVIDEND_TAX_CREDIT,
    T5_INVESTMENT_INCOME,
    T5_TAXABLE_DIVIDENDS,
    T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    T1206_PART_1_LINE_3_AMOUNT,
    T1206_UNDER_18_DIVIDEND_AMOUNT,
    T2205_ON_LINE_11500,
    T2205_ON_LINE_12900,
    T2205_ON_LINE_13000,
    T5013_DIVIDEND_TAX_CREDIT,
    T5013_INVESTMENT_INCOME,
    T5013_TAXABLE_DIVIDENDS,
    T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    TAX_REFUND_INTEREST,
    TAXABLE_CAPITAL_GAINS,
    TAXABLE_DIVIDENDS,
    TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    TAXABLE_SCHOLARSHIPS,
    TAXABLE_SUPPORT_PAYMENTS,
    TOTAL_INCOME,
    UNAPPLIED_LISTED_PERSONAL_PROPERTY_LOSSES,
    UNIVERSAL_CHILD_CARE_BENEFIT,
    VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
    WORKERS_COMPENSATION_BENEFITS,
)
from tests.jurisdictions.ca_on.manifest_families.t2017_reserve import T2017_LINE_31_EXPORT

# The exports of the form ca/t1206_share_dispositions that the return adds: the under-18 dividend
# amount and the Part 1 line 3 amount, one record each.
T1206_UNDER_18_DIVIDEND_AMOUNT_EXPORT = RecordListKind(
    "ca/t1206_share_dispositions.t1206_under_18_dividend_amount",
    fields=(T1206_UNDER_18_DIVIDEND_AMOUNT,),
)
T1206_PART_1_LINE_3_AMOUNT_EXPORT = RecordListKind(
    "ca/t1206_share_dispositions.t1206_part_1_line_3_amount",
    fields=(T1206_PART_1_LINE_3_AMOUNT,),
)

INPUTS = frozenset(
    {
        "ca/employment_income",
        # Schedule 3 Part 3 and Part 4: the ten property lists (lines 1 to 10), the unapplied
        # listed personal property losses, the properties sold (Form T2091(IND)), line 13
        # (16100), line 15 (17400), line 16 (17600) and line 20 (19200); line 21 (19700) is
        # computed.
        "ca/qsbcs_dispositions",
        "ca/qffp_dispositions",
        "ca/qffp_foreclosure_dispositions",
        "ca/share_dispositions",
        "ca/real_estate_dispositions",
        "ca/bond_dispositions",
        "ca/crypto_asset_dispositions",
        "ca/other_foreclosure_dispositions",
        "ca/personal_use_property_dispositions",
        "ca/listed_personal_property_dispositions",
        "ca/unapplied_listed_personal_property_losses",
        "ca/principal_residence_properties",
        "ca/capital_gains_deferral",
        "ca/slip_capital_gains_or_losses",
        "ca/t3_capital_gains_or_losses",
        # Schedule 3 Part 5 line 25 and line 19890: "Capital gains from certain dispositions of an
        # interest in a partnership subject to 100% inclusion rate (if negative, enter "0")", a
        # starting amount.
        "ca/partnership_gains_at_full_inclusion",
        "ca/other_employment_income",
        "ca/old_age_security",
        "ca/cpp_or_qpp_benefits",
        "ca/other_pensions_and_superannuation",
        "ca/universal_child_care_benefit",
        "ca/ei_and_other_benefits",
        "ca/t3_taxable_dividends_other_than_eligible",
        "ca/t4ps_taxable_dividends_other_than_eligible",
        "ca/t5_taxable_dividends_other_than_eligible",
        "ca/t5013_taxable_dividends_other_than_eligible",
        "ca/t3_taxable_dividends",
        "ca/t4ps_taxable_dividends",
        "ca/t5_taxable_dividends",
        "ca/t5013_taxable_dividends",
        "ca/eligible_dividends_received_without_a_slip",
        "ca/other_dividends_received_without_a_slip",
        "ca/t3_dividend_tax_credit",
        "ca/t4ps_dividend_tax_credit",
        "ca/t5_dividend_tax_credit",
        "ca/t5013_dividend_tax_credit",
        "ca/t3_investment_income",
        "ca/t5_investment_income",
        "ca/t5013_investment_income",
        "ca/investment_income_credited_not_received",
        "ca/tax_refund_interest",
        "ca/foreign_investment_income",
        "ca/investment_income_without_a_slip",
        "ca/investment_royalties",
        "ca/investment_income_reported_in_previous_years",
        "ca/net_partnership_income",
        "ca/rdsp_income",
        "ca/taxable_support_payments",
        "ca/rrsp_income",
        "ca/fhsa_income",
        "ca/other_fhsa_income",
        "ca/other_income",
        "ca/taxable_scholarships",
        "ca/workers_compensation_benefits",
        "ca/social_assistance_payments",
        "ca/net_federal_supplements",
        # T1 lines 10105, 10120, 10130, 11410, 11701, 11905 and 12799 "Line 10105: Tax-exempt income
        # for emergency services volunteers", "Line 10120: Commissions included on line 10100 (box
        # 42 of all T4 slips)", "Line 10130: Wage-loss replacement contributions", "Line 11410:
        # Disability benefits included on line 11400 (box 16 of the T4A(P) slip)", "Line 11701: UCCB
        # amount designated to a dependant", "Line 11905: EI maternity and parental benefits, and
        # provincial parental insurance plan (PPIP) benefits" and "Line 12799: Total" (under "Line
        # 15: Support payments received (go to canada.ca/taxes-support-payments)"): the form
        # computes nothing from them, so each is also an output; the General Guide says lines 10120,
        # 11410 and 11905 are already included in lines 10100, 11400 and 11900, so they are not
        # added to total income.
        "ca/emergency_services_volunteer_exempt_income",
        "ca/t4_commissions",
        "ca/wage_loss_replacement_contributions",
        "ca/t4ap_disability_benefits",
        "ca/uccb_designated_to_dependant",
        "ca/ei_maternity_parental_benefits",
        "ca/support_payments_received_total",
    }
)

OUTPUTS = frozenset(
    {
        # Schedule 3 line 26 (box 19900): a net capital loss is negative here, not on line 12700.
        "ca/schedule_3_line_19900",
        "ca/taxable_dividends_other_than_eligible",
        # Schedule 3 Part 3: the eight "Total proceeds of disposition" lines feed no later line.
        "ca/qsbcs_proceeds",
        "ca/qffp_proceeds",
        "ca/qffp_foreclosure_proceeds",
        "ca/share_proceeds",
        "ca/real_estate_proceeds",
        "ca/bond_proceeds",
        "ca/crypto_asset_proceeds",
        "ca/other_foreclosure_proceeds",
        # Form T2091(IND) Part 2 lines 27 to 53 (the total over the properties of each line): no
        # step reads them, so each is declared as an unread printed line.
        "ca/principal_residence_line_27",
        "ca/principal_residence_line_29",
        "ca/principal_residence_line_30",
        "ca/principal_residence_line_32",
        "ca/principal_residence_line_33",
        "ca/principal_residence_line_38",
        "ca/principal_residence_line_39",
        "ca/principal_residence_line_42",
        "ca/principal_residence_line_44",
        "ca/principal_residence_line_45",
        "ca/principal_residence_line_48",
        "ca/principal_residence_line_51",
        "ca/principal_residence_line_53",
        # Form T2091(IND)-WS Chart 1 and Parts 1 and 3, and Form T2091(IND) Part 4 line 56:
        # the total over the properties of each line; no step reads them, so each is declared
        # as an unread printed line.
        "ca/principal_residence_worksheet_line_3",
        "ca/principal_residence_worksheet_line_6",
        "ca/principal_residence_worksheet_line_16",
        "ca/principal_residence_worksheet_line_17",
        "ca/principal_residence_worksheet_line_18",
        "ca/principal_residence_worksheet_line_19",
        "ca/principal_residence_worksheet_line_21",
        "ca/principal_residence_worksheet_line_23",
        "ca/principal_residence_worksheet_line_24",
        "ca/principal_residence_worksheet_line_26",
        "ca/principal_residence_worksheet_line_27",
        "ca/principal_residence_worksheet_line_59",
        "ca/principal_residence_worksheet_line_61",
        "ca/principal_residence_worksheet_line_63",
        "ca/principal_residence_worksheet_line_64",
        "ca/principal_residence_worksheet_line_66",
        # Form T2091(IND)-WS Part 2 lines 30 to 58 that are calculated: the total over the
        # properties of each line; no step reads them, so each is an unread printed line.
        "ca/principal_residence_worksheet_line_30",
        "ca/principal_residence_worksheet_line_32",
        "ca/principal_residence_worksheet_line_33",
        "ca/principal_residence_worksheet_line_35",
        "ca/principal_residence_worksheet_line_36",
        "ca/principal_residence_worksheet_line_40",
        "ca/principal_residence_worksheet_line_41",
        "ca/principal_residence_worksheet_line_44",
        "ca/principal_residence_worksheet_line_46",
        "ca/principal_residence_worksheet_line_47",
        "ca/principal_residence_worksheet_line_50",
        "ca/principal_residence_worksheet_line_53",
        "ca/principal_residence_worksheet_line_55",
        "ca/principal_residence_worksheet_line_58",
        "ca/principal_residence_line_56",
        # Form T2091(IND) Part 3 line 54 "Total capital gain": line 57 is entered on line
        # 15800 of Schedule 3 instead, so no step reads it and it is a declared unread printed
        # line.
        "ca/principal_residence_gain",
        "ca/emergency_services_volunteer_exempt_income",
        "ca/t4_commissions",
        "ca/wage_loss_replacement_contributions",
        "ca/t4ap_disability_benefits",
        "ca/uccb_designated_to_dependant",
        "ca/ei_maternity_parental_benefits",
        "ca/support_payments_received_total",
        # Form 5000-G "Emergency services volunteers": the conflict of the $1,000 exemption (line
        # 10105) with the VFA or SRVA, checked to be 0 (`ca/count_refused_by_conditions`). The
        # form reads it nowhere; the checks are in part
        # `29_emergency_services_volunteer_checks.yaml`.
        "ca/emergency_services_volunteer_conflict_checked",
    }
)

STEPS = {
    # Schedule 3 (form 5000-S3) Part 3: "For each Gain or loss enter as many lines as necessary."
    # Each property type lists one row per disposition: "(Column 2): Proceeds of disposition",
    # "(Column 3): Adjusted cost base", "(Column 4): Outlays and expenses", "(Column 5): Gain or
    # loss (column 2 minus columns 3 and 4)"; lines 1 to 8 (10700, 11000, 12400, 13200, 13800,
    # 15300, 15301, 15500) are each "Total gain or loss (add all the amounts under column 5)",
    # one step each.
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
    # The exports of the form ca/t1206_share_dispositions as amounts of the return.
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
    # Schedule 3 Part 3: lines 1 to 8 (10699, 10999, 12399, 13199, 13599, 15199, 15200, 15499) are
    # each "Total proceeds of disposition (add all the amounts under column 2)", one step each; the
    # totals feed no later line.
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/qsbcs_dispositions"},
        produces={"output": "ca/qsbcs_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/qffp_dispositions"},
        produces={"output": "ca/qffp_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/qffp_foreclosure_dispositions"},
        produces={"output": "ca/qffp_foreclosure_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/share_dispositions"},
        produces={"output": "ca/share_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/real_estate_dispositions"},
        produces={"output": "ca/real_estate_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/bond_dispositions"},
        produces={"output": "ca/bond_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/crypto_asset_dispositions"},
        produces={"output": "ca/crypto_asset_proceeds"},
    ),
    CapabilitySelection(
        name="ca/disposition_proceeds",
        params={},
        consumes={"dispositions": "ca/other_foreclosure_dispositions"},
        produces={"output": "ca/other_foreclosure_proceeds"},
    ),
    # Form T2091(IND) Part 1 and Part 3, one form for each property sold: "Divide line 21 by line
    # 22." (line 23, the exempt part, rounded half up to the cent), "Line 18 minus line 23 (if
    # negative, enter "0")" (line 24) and "Total capital gain" (line 54, which is line 24 when
    # Part 2 is not completed), added over the properties.
    CapabilitySelection(
        name="ca/principal_residence_gain",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_gain"},
    ),
    # Form T2091(IND) Part 2 line 27 "Line 25 minus line 26" "Pre-1982 gain before principal
    # residence exemption": the total over the properties of that line of each one (0 where the form
    # says to enter "0").
    CapabilitySelection(
        name="ca/principal_residence_line_27",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_27"},
    ),
    # Form T2091(IND) Part 2 line 29 "Line 2 plus 1 (see note on page 4)": the total over the
    # properties of that line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_29",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_29"},
    ),
    # Form T2091(IND) Part 2 line 30 "Multiply line 28 by line 29.": the total over the properties
    # of that line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_30",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_30"},
    ),
    # Form T2091(IND) Part 2 line 32 "Divide line 30 by line 31.": the total over the properties of
    # that line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_32",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_32"},
    ),
    # Form T2091(IND) Part 2 line 33 "Line 27 minus line 32 (if negative, enter "0")" "Pre-1982
    # gain": the total over the properties of that line of each one (0 where the form says to enter
    # "0").
    CapabilitySelection(
        name="ca/principal_residence_line_33",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_33"},
    ),
    # Form T2091(IND) Part 2 line 38 "Add lines 35 to 37.": the total over the properties of that
    # line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_38",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_38"},
    ),
    # Form T2091(IND) Part 2 line 39 "Line 34 minus line 38" "Post-1981 gain before principal
    # residence exemption": the total over the properties of that line of each one (0 where the form
    # says to enter "0").
    CapabilitySelection(
        name="ca/principal_residence_line_39",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_39"},
    ),
    # Form T2091(IND) Part 2 line 42 "Multiply line 40 by line 41.": the total over the properties
    # of that line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_42",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_42"},
    ),
    # Form T2091(IND) Part 2 line 44 "Divide line 42 by line 43.": the total over the properties of
    # that line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_44",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_44"},
    ),
    # Form T2091(IND) Part 2 line 45 "Line 39 minus line 44 (if negative, enter "0")" "Post-1981
    # gain": the total over the properties of that line of each one (0 where the form says to enter
    # "0").
    CapabilitySelection(
        name="ca/principal_residence_line_45",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_45"},
    ),
    # Form T2091(IND) Part 2 line 48 "Line 46 minus line 47 (if negative, enter "0")" "Post-1981
    # loss": the total over the properties of that line of each one (0 where the form says to enter
    # "0").
    CapabilitySelection(
        name="ca/principal_residence_line_48",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_48"},
    ),
    # Form T2091(IND) Part 2 line 51 "Line 49 plus line 50": the total over the properties of that
    # line of each one (0 where the area is not completed).
    CapabilitySelection(
        name="ca/principal_residence_line_51",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_51"},
    ),
    # Form T2091(IND) Part 2 line 53 "Line 51 minus line 52 (if negative, enter "0")" "Net capital
    # gain": the total over the properties of that line of each one (0 where the form says to enter
    # "0").
    CapabilitySelection(
        name="ca/principal_residence_line_53",
        params={"rounding": "ca/principal_residence_gain_rounding"},
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_53"},
    ),
    # Form T2091(IND)-WS line 3 "Total number of years designated before 1995 (line 1 plus line
    # 2)": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_3",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_3"},
    ),
    # Form T2091(IND)-WS line 6 "Total number of years owned before 1995 (line 4 plus line 5)":
    # the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_6",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_6"},
    ),
    # Form T2091(IND)-WS Chart 1 line 16 "Multiply line 14 by 1.1.": the total over the
    # properties of that line of each one (0 where the chart is not completed, "Complete this
    # chart if the amount on line 7 is more than the amount on line 10.").
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_16",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_16"},
    ),
    # Form T2091(IND)-WS Chart 1 line 17 "Line 15 minus line 16 (if negative, enter "0")": the
    # total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_17",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_17"},
    ),
    # Form T2091(IND)-WS Chart 1 line 18 "Line 14 minus line 17": the total over the properties
    # of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_18",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_18"},
    ),
    # Form T2091(IND)-WS line 19 "Enter the amount from line 18 if you completed Chart 1.
    # Otherwise, enter the amount from line 10.": the total over the properties of that line of
    # each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_19",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_19"},
    ),
    # Form T2091(IND)-WS line 21 "Line 19 minus line 20" "Adjusted gain before principal
    # residence exemption": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_21",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_21"},
    ),
    # Form T2091(IND)-WS line 23 "Line 3 plus 1 (see note below)": the total over the properties
    # of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_23",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_23"},
    ),
    # Form T2091(IND)-WS line 24 "Multiply line 22 by line 23.": the total over the properties
    # of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_24",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_24"},
    ),
    # Form T2091(IND)-WS line 26 "Divide line 24 by line 25.": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_26",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_26"},
    ),
    # Form T2091(IND)-WS line 27 "Line 21 minus line 26" "Net adjusted gain": the total over the
    # properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_27",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_27"},
    ),
    # Form T2091(IND)-WS line 30 "Line 28 minus line 29" "Adjusted pre-1982 gain before principal
    # residence exemption": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_30",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_30"},
    ),
    # Form T2091(IND)-WS line 32 "Line 2 plus 1 (see note below)": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_32",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_32"},
    ),
    # Form T2091(IND)-WS line 33 "Multiply line 31 by line 32.": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_33",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_33"},
    ),
    # Form T2091(IND)-WS line 35 "Divide line 33 by line 34.": the total over the properties of that
    # line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_35",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_35"},
    ),
    # Form T2091(IND)-WS line 36 "Line 30 minus line 35 (if negative, enter "0")" "Adjusted pre-1982
    # gain": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_36",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_36"},
    ),
    # Form T2091(IND)-WS line 40 "Line 38 plus line 39": the total over the properties of that line
    # of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_40",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_40"},
    ),
    # Form T2091(IND)-WS line 41 "Line 37 minus line 40" "Adjusted post-1981 gain before principal
    # residence exemption": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_41",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_41"},
    ),
    # Form T2091(IND)-WS line 44 "Multiply line 42 by line 43.": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_44",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_44"},
    ),
    # Form T2091(IND)-WS line 46 "Divide line 44 by line 45.": the total over the properties of that
    # line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_46",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_46"},
    ),
    # Form T2091(IND)-WS line 47 "Line 41 minus line 46 (if negative, enter "0")" "Adjusted
    # post-1981 gain": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_47",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_47"},
    ),
    # Form T2091(IND)-WS line 50 "Line 48 minus line 49 (if negative, enter "0")" "Adjusted
    # post-1981 loss": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_50",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_50"},
    ),
    # Form T2091(IND)-WS line 53 "Line 51 plus line 52": the total over the properties of that line
    # of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_53",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_53"},
    ),
    # Form T2091(IND)-WS line 55 "Line 53 minus line 54 (if negative, enter "0")" "Net adjusted
    # gain": the total over the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_55",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_55"},
    ),
    # Form T2091(IND)-WS line 58 "Enter whichever amount is less: line 56 or line 57." "Total
    # adjusted gain before reduction for non-qualifying real or immovable property": the total over
    # the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_58",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_58"},
    ),
    # Form T2091(IND)-WS line 59 "If you completed Part 2, enter the amount from line 58.
    # Otherwise, enter the amount from line 27.": the total over the properties of that line of
    # each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_59",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_59"},
    ),
    # Form T2091(IND)-WS line 61 "Multiply line 59 by line 60.": the total over the properties
    # of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_61",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_61"},
    ),
    # Form T2091(IND)-WS line 63 "Divide line 61 by line 62.": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_63",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_63"},
    ),
    # Form T2091(IND)-WS line 64 "Line 59 minus line 63" "Total adjusted gain": the total over
    # the properties of that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_64",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_64"},
    ),
    # Form T2091(IND)-WS line 66 "Enter whichever amount is less: line 64 or line 65."
    # "Reduction as a result of the capital gains election": the total over the properties of
    # that line of each one.
    CapabilitySelection(
        name="ca/principal_residence_worksheet_line_66",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_worksheet_line_66"},
    ),
    # Form T2091(IND) Part 4 line 56 "Reduction as a result of the capital gains election (line
    # 66 of Form T2091(IND)-WS)": the total over the properties of that line of each one (0 for
    # a property with no election).
    CapabilitySelection(
        name="ca/principal_residence_line_56",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_56"},
    ),
    # Form T2091(IND) Part 4 line 57 "Line 55 minus line 56 (if negative, enter "0")" "Capital
    # gain": the total over the properties of that line of each one, entered on line 15800 of
    # Schedule 3 ("Enter the amount from line 57 on line 15800 of Schedule 3, Capital Gains or
    # Losses, for dispositions or deemed dispositions.").
    CapabilitySelection(
        name="ca/principal_residence_line_57",
        params={
            "rounding": "ca/principal_residence_gain_rounding",
            "chart_1_factor": "ca/principal_residence_chart_1_factor",
        },
        consumes={"properties": "ca/principal_residence_properties"},
        produces={"output": "ca/principal_residence_line_57"},
    ),
    # Part 3, Personal-use property: "Line 9 and line 15800: Total gain only (add all the amounts
    # under column 5)", each row's proceeds and adjusted cost base at least the Guide T4037 $1,000
    # ("Proceeds of disposition (whichever is more: selling price or $1,000)"; "ACB (whichever is
    # more: cost or $1,000) plus outlays and expenses"): the rows' gains, a row's loss counting 0,
    # then line 9 itself, a sum of those rows and line 57 of T2091(IND) Part 4 ("Enter the amount
    # from line 57 on line 15800 of Schedule 3").
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
    # Part 3, Listed personal property: the rows' gains and losses (column 5) added, then line 10
    # and line 15900 "Net gain only": that total less the unapplied listed personal property
    # losses from other years, not below zero.
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
    # Part 3 "Line 11: Add lines 1 to 10. Total gains or losses of qualified properties and
    # other properties ="; Part 4 "Line 12: Amount from line 11 of the previous page" is the same
    # artifact, so it has no step of its own.
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
    # Part 4 "Line 14: Line 12 minus line 13 =" (line 13 and line 16100 is the deferral checked at
    # most line 4, `ca/capital_gains_deferral_checked`).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_of_qualified_and_other_properties",
            "less": "ca/capital_gains_deferral_checked",
        },
        produces={"output": "ca/capital_gains_after_deferral"},
    ),
    # Part 4 "Line 17: Add lines 14 to 16. =" (lines 15 and 16, 17400 and 17600, are inputs).
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
    # Part 4 "Line 19 and line 19100: Total gains or losses before reserves: line 17 minus line
    # 18 =" (line 18 and line 17800 is the business investment loss reduction already computed).
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={
            "amount": "ca/capital_gains_before_investment_loss_reduction",
            "less": "ca/business_investment_loss_reduction",
        },
        produces={"output": "ca/capital_gains_before_reserves"},
    ),
    # Part 4 "Line 20 and line 19200: Reserves to be included in (or deducted from) income from Form
    # T2017": the record total of the summary form's line 31 (`ca/t2017.t2017_line_31`, one record),
    # "Total reserve to be included in income".
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t2017.t2017_line_31"},
        produces={"output": "ca/schedule_3_line_19200"},
    ),
    # Part 4 "Line 21 and line 19700: Line 19 plus line 20 Total capital gains or losses =" (line
    # 20 and line 19200 is the total above).
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/capital_gains_before_reserves", "ca/schedule_3_line_19200")},
        produces={"output": "ca/capital_gain"},
    ),
    # Part 5 line 22 is the same artifact as line 21; line 24 "Line 22 multiplied by the
    # percentage on line 23" (signed, the included capital gain), then line 26 and line 19900
    # "Line 24 plus line 25 If positive, enter the result on line 12700 of your return": line 24
    # and line 25 (the partnership gains at full inclusion, a caller input) as the parts of a sum
    # not below zero, so the taxable capital gains stay non-negative.
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
    # T1 line 9 (12000) "Amount of dividends (eligible and other than eligible)" and line
    # 12010 "Amount of dividends (other than eligible)" (use Federal Worksheet): the Federal
    # Worksheet's "Lines 12000 and 12010 - Taxable amount of dividends from taxable Canadian
    # corporations", line 5 "Add lines 1 to 4. Enter this amount on line 12010 of your
    # return." (the T3, T4PS, T5 and T5013 slip boxes of lines 1 to 4) and line 10 "Add lines
    # 6 to 9. Enter this amount on line 12000 of your return." (lines 6 to 9). For dividends
    # with no information slip, line 11 "Actual amount of eligible dividends received" and
    # line 12 "Applicable rate 138%" give line 13 "Line 11 multiplied by the percentage from
    # line 12"; line 14 "Actual amount of dividends other than eligible dividends received"
    # and line 15 "Applicable rate 115%" give line 16 "Line 14 multiplied by the percentage
    # from line 15 Include this amount on line 12010 of your return."; line 17 "Line 13 plus
    # line 16. Include this amount on line 12000 of your return." The rates are above one, so
    # they are fractions, not rates. Line 12010 is line 5 plus line 16 and line 12000 is line
    # 10 plus line 17.
    # Each of lines 1 to 4 is a part of the same slip type's amount on lines 6 to 9 (the whole
    # in the Federal Worksheet's lines 12000 and 12010), so each part is checked to be at most its
    # whole (`core/at_most`) before the sum of lines 1 to 4 reads it. An amount above its whole is
    # refused, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t3_taxable_dividends_other_than_eligible",
            "bound": "ca/t3_taxable_dividends",
        },
        produces={"output": "ca/t3_taxable_dividends_other_than_eligible_checked"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t4ps_taxable_dividends_other_than_eligible",
            "bound": "ca/t4ps_taxable_dividends",
        },
        produces={"output": "ca/t4ps_taxable_dividends_other_than_eligible_checked"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t5_taxable_dividends_other_than_eligible",
            "bound": "ca/t5_taxable_dividends",
        },
        produces={"output": "ca/t5_taxable_dividends_other_than_eligible_checked"},
    ),
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/t5013_taxable_dividends_other_than_eligible",
            "bound": "ca/t5013_taxable_dividends",
        },
        produces={"output": "ca/t5013_taxable_dividends_other_than_eligible_checked"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_taxable_dividends_other_than_eligible_checked",
                "ca/t4ps_taxable_dividends_other_than_eligible_checked",
                "ca/t5_taxable_dividends_other_than_eligible_checked",
                "ca/t5013_taxable_dividends_other_than_eligible_checked",
            )
        },
        produces={"output": "ca/slip_taxable_dividends_other_than_eligible"},
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
                "ca/slip_taxable_dividends_other_than_eligible",
                "ca/other_dividends_grossed_up",
                "ca/t1206_under_18_dividend_amount",
            )
        },
        produces={"output": "ca/taxable_dividends_other_than_eligible"},
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
    # T1 Step 2 line 10 (12100) "Interest and other investment income (use Federal
    # Worksheet)": the Federal Worksheet's "Line 12100 - Interest and other investment
    # income" line 9 "Add lines 1 to 8.", in line order, then line 11 "Line 9 minus line
    # 10. Enter this amount on line 12100 of your return." with line 10 "Interest and other
    # investment income, included on line 9, received and reported in previous years".
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
    # Federal Worksheet line 10 "Interest and other investment income, included on line 9, received
    # and reported in previous years" is at most line 9 ("Add lines 1 to 8."): an amount above it is
    # an input error (`InputAboveBoundError`), not capped. The checked amount is the one line 11
    # subtracts.
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
    # T1 line 32 and line 14700 "Add lines 29 to 31 (see line 25000 in Step 4).": workers'
    # compensation benefits (14400), social assistance payments (14500) and net federal
    # supplements paid (14600), in line order.
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
    # T1 line 33 and line 15000 "Line 28 plus line 32 Total income": every income line
    # the return lists, in line order (lines 1 to 20, line 13 being the net rental
    # income, line 12600 "Net"; here with the amount of dividends of line 9 (12000), the
    # taxable capital gains of line 14 and the taxable support payments of line 15, then
    # line 32); line 27 "Add lines 22 to 26. Net self-employment income" (line 28 is line 21 plus
    # line 27) comes after line 20, before lines 29 to 31 (line 32).
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
    # T1 line 123 (40425) "Federal dividend tax credit (use Federal Worksheet)": the Federal
    # Worksheet's "Line 40425 - Federal dividend tax credit", line 5 "Add lines 1 to 4." of
    # the credits shown on the T3, T4PS, T5 and T5013 slips. For dividends with no
    # information slip, line A "Amount from line 12000 of your return (Note 1)" and line B
    # "Amount from line 12010 of your return (Note 1)", Note 1 being "Enter only the amount
    # of dividends that were not shown on an information slip.", so line A is the
    # Worksheet's line 17 and line B its line 16, each its own step; line 6 is "Line B,
    # multiplied by 9.0301%"; line C is "Amount A minus amount B", and line 7 (printed
    # "Line 2") is line C "multiplied by 15.0198%"; line 8 is "Line 6 plus line 7" and
    # line 9 "Line 5 plus line 8 Enter this amount on line 40425 of your return."
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/t3_dividend_tax_credit",
                "ca/t4ps_dividend_tax_credit",
                "ca/t5_dividend_tax_credit",
                "ca/t5013_dividend_tax_credit",
            )
        },
        produces={"output": "ca/slip_dividend_tax_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": ("ca/dividends_without_a_slip_grossed_up", "ca/t1206_under_18_dividend_amount")
        },
        produces={"output": "ca/dividends_amount_a"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/other_dividends_grossed_up", "ca/t1206_under_18_dividend_amount")},
        produces={"output": "ca/dividends_amount_b"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/dividend_credit_rate_other_than_eligible"},
        consumes={"base": "ca/dividends_amount_b"},
        produces={"output": "ca/other_dividends_credit"},
    ),
    CapabilitySelection(
        name="core/subtract",
        params={},
        consumes={"amount": "ca/dividends_amount_a", "less": "ca/dividends_amount_b"},
        produces={"output": "ca/dividends_amount_a_less_b"},
    ),
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/dividend_credit_rate_eligible"},
        consumes={"base": "ca/dividends_amount_a_less_b"},
        produces={"output": "ca/eligible_dividends_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/other_dividends_credit", "ca/eligible_dividends_credit")},
        produces={"output": "ca/no_slip_dividend_tax_credit"},
    ),
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": ("ca/slip_dividend_tax_credit", "ca/no_slip_dividend_tax_credit")},
        produces={"output": "ca/dividend_tax_credit"},
    ),
    # T1 line 125 "Add lines 122 to 124.": line 122 "Amount from line 35000", line 123 (40425),
    # the federal dividend tax credit, and line 124 (40427), the minimum tax carryover applied
    # on Form T691 Part 8 line 12, in line order.
    CapabilitySelection(
        name="core/sum",
        params={},
        consumes={
            "parts": (
                "ca/non_refundable_tax_credits",
                "ca/dividend_tax_credit",
                "ca/amt_minimum_tax_carryover_applied",
            )
        },
        produces={"output": "ca/credits_against_basic_federal_tax"},
    ),
    # T1 line 27 "Add lines 22 to 26. Net self-employment income": line 22 (13500) business
    # income, line 23 (13700) professional income, line 24 (13900) commission income, line 25
    # (14100) farming income and line 26 (14300) fishing income, the "Net" box of each, in line
    # order. Line 28 "Line 21 plus line 27" is not a step of its own: total income (line 15000)
    # adds line 27 to the lines 1 to 20, in line order.
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
            ),
        },
        produces={"output": "ca/net_self_employment_income"},
    ),
    # Form 5000-G "Emergency services volunteers": the $1,000 exemption on line 10105 (box 87 of the
    # T4) and the VFA or SRVA (lines 31220 and 31240) are a choice, not both. The conflict is a
    # count of 1 or 0 from the conditions dataset; a count of 1 is refused, not capped.
    CapabilitySelection(
        name="ca/count_by_conditions",
        params={"conditions": "ca/emergency_services_volunteer_conflicts"},
        consumes={
            "counts": (
                "ca/volunteer_firefighters_conditions_met_checked",
                "ca/search_and_rescue_conditions_met_checked",
            ),
            "amounts": ("ca/emergency_services_volunteer_exempt_income",),
        },
        produces={"output": "ca/emergency_services_volunteer_conflict"},
    ),
    CapabilitySelection(
        name="ca/count_refused_by_conditions",
        params={"conditions": "ca/emergency_services_volunteer_conflict_refused"},
        consumes={"count": "ca/emergency_services_volunteer_conflict"},
        produces={"output": "ca/emergency_services_volunteer_conflict_checked"},
    ),
}

WIRING = {
    (
        SumNotBelowZero,
        frozenset({SHARE_GAIN_OR_LOSS}),
        frozenset({SHARE_GAIN_NOT_BELOW_ZERO}),
    ),
    (
        AtMost,
        frozenset({CAPITAL_GAINS_DEFERRAL, SHARE_GAIN_NOT_BELOW_ZERO}),
        frozenset({CAPITAL_GAINS_DEFERRAL_CHECKED}),
    ),
    (ApplyRate, frozenset({CAPITAL_GAIN}), frozenset({INCLUDED_CAPITAL_GAIN})),
    (
        SumNotBelowZero,
        frozenset({INCLUDED_CAPITAL_GAIN, PARTNERSHIP_GAINS_AT_FULL_INCLUSION}),
        frozenset({TAXABLE_CAPITAL_GAINS}),
    ),
    (DispositionGains, frozenset({QSBCS_DISPOSITIONS}), frozenset({QSBCS_GAIN_OR_LOSS})),
    (QffpGains, frozenset({QFFP_DISPOSITIONS}), frozenset({QFFP_GAIN_OR_LOSS})),
    (
        QffpGains,
        frozenset({QFFP_FORECLOSURE_DISPOSITIONS}),
        frozenset({QFFP_FORECLOSURE_GAIN_OR_LOSS}),
    ),
    (
        DispositionGains,
        frozenset({SHARE_DISPOSITIONS}),
        frozenset({SHARE_GAIN_OR_LOSS}),
    ),
    (
        RecordTotal,
        frozenset({T1206_UNDER_18_DIVIDEND_AMOUNT_EXPORT}),
        frozenset({T1206_UNDER_18_DIVIDEND_AMOUNT}),
    ),
    (
        RecordTotal,
        frozenset({T1206_PART_1_LINE_3_AMOUNT_EXPORT}),
        frozenset({T1206_PART_1_LINE_3_AMOUNT}),
    ),
    (
        DepreciablePropertyGains,
        frozenset({REAL_ESTATE_DISPOSITIONS}),
        frozenset({REAL_ESTATE_GAIN_OR_LOSS}),
    ),
    (DispositionGains, frozenset({BOND_DISPOSITIONS}), frozenset({BOND_GAIN_OR_LOSS})),
    (
        DispositionGains,
        frozenset({CRYPTO_ASSET_DISPOSITIONS}),
        frozenset({CRYPTO_ASSET_GAIN_OR_LOSS}),
    ),
    (
        QffpGains,
        frozenset({OTHER_FORECLOSURE_DISPOSITIONS}),
        frozenset({OTHER_FORECLOSURE_GAIN_OR_LOSS}),
    ),
    (
        DispositionProceeds,
        frozenset({QSBCS_DISPOSITIONS}),
        frozenset({QSBCS_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({QFFP_DISPOSITIONS}),
        frozenset({QFFP_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({QFFP_FORECLOSURE_DISPOSITIONS}),
        frozenset({QFFP_FORECLOSURE_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({SHARE_DISPOSITIONS}),
        frozenset({SHARE_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({REAL_ESTATE_DISPOSITIONS}),
        frozenset({REAL_ESTATE_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({BOND_DISPOSITIONS}),
        frozenset({BOND_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({CRYPTO_ASSET_DISPOSITIONS}),
        frozenset({CRYPTO_ASSET_PROCEEDS}),
    ),
    (
        DispositionProceeds,
        frozenset({OTHER_FORECLOSURE_DISPOSITIONS}),
        frozenset({OTHER_FORECLOSURE_PROCEEDS}),
    ),
    (
        PersonalUsePropertyGains,
        frozenset({PERSONAL_USE_PROPERTY_DISPOSITIONS}),
        frozenset({PERSONAL_USE_PROPERTY_GAIN_ROWS}),
    ),
    (
        PrincipalResidenceGain,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_GAIN}),
    ),
    (
        PrincipalResidenceWorksheetLine3Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3}),
    ),
    (
        PrincipalResidenceWorksheetLine6Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6}),
    ),
    (
        PrincipalResidenceWorksheetLine16Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16}),
    ),
    (
        PrincipalResidenceWorksheetLine17Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17}),
    ),
    (
        PrincipalResidenceWorksheetLine18Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18}),
    ),
    (
        PrincipalResidenceWorksheetLine19Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19}),
    ),
    (
        PrincipalResidenceWorksheetLine21Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21}),
    ),
    (
        PrincipalResidenceWorksheetLine23Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23}),
    ),
    (
        PrincipalResidenceWorksheetLine24Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24}),
    ),
    (
        PrincipalResidenceWorksheetLine26Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26}),
    ),
    (
        PrincipalResidenceWorksheetLine27Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27}),
    ),
    (
        PrincipalResidenceWorksheetLine30Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30}),
    ),
    (
        PrincipalResidenceWorksheetLine32Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32}),
    ),
    (
        PrincipalResidenceWorksheetLine33Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33}),
    ),
    (
        PrincipalResidenceWorksheetLine35Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35}),
    ),
    (
        PrincipalResidenceWorksheetLine36Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36}),
    ),
    (
        PrincipalResidenceWorksheetLine40Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40}),
    ),
    (
        PrincipalResidenceWorksheetLine41Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41}),
    ),
    (
        PrincipalResidenceWorksheetLine44Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44}),
    ),
    (
        PrincipalResidenceWorksheetLine46Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46}),
    ),
    (
        PrincipalResidenceWorksheetLine47Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47}),
    ),
    (
        PrincipalResidenceWorksheetLine50Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50}),
    ),
    (
        PrincipalResidenceWorksheetLine53Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53}),
    ),
    (
        PrincipalResidenceWorksheetLine55Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55}),
    ),
    (
        PrincipalResidenceWorksheetLine58Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58}),
    ),
    (
        PrincipalResidenceWorksheetLine59Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59}),
    ),
    (
        PrincipalResidenceWorksheetLine61Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61}),
    ),
    (
        PrincipalResidenceWorksheetLine63Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63}),
    ),
    (
        PrincipalResidenceWorksheetLine64Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64}),
    ),
    (
        PrincipalResidenceWorksheetLine66Capability,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66}),
    ),
    (
        PrincipalResidencePart4Line56,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_56}),
    ),
    (
        PrincipalResidencePart4Line57,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_57}),
    ),
    (
        PrincipalResidencePart2Line27,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_27}),
    ),
    (
        PrincipalResidencePart2Line29,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_29}),
    ),
    (
        PrincipalResidencePart2Line30,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_30}),
    ),
    (
        PrincipalResidencePart2Line32,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_32}),
    ),
    (
        PrincipalResidencePart2Line33,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_33}),
    ),
    (
        PrincipalResidencePart2Line38,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_38}),
    ),
    (
        PrincipalResidencePart2Line39,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_39}),
    ),
    (
        PrincipalResidencePart2Line42,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_42}),
    ),
    (
        PrincipalResidencePart2Line44,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_44}),
    ),
    (
        PrincipalResidencePart2Line45,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_45}),
    ),
    (
        PrincipalResidencePart2Line48,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_48}),
    ),
    (
        PrincipalResidencePart2Line51,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_51}),
    ),
    (
        PrincipalResidencePart2Line53,
        frozenset({PRINCIPAL_RESIDENCE_PROPERTIES}),
        frozenset({PRINCIPAL_RESIDENCE_LINE_53}),
    ),
    (
        Sum,
        frozenset({PERSONAL_USE_PROPERTY_GAIN_ROWS, PRINCIPAL_RESIDENCE_LINE_57}),
        frozenset({PERSONAL_USE_PROPERTY_GAIN}),
    ),
    (
        DispositionGains,
        frozenset({LISTED_PERSONAL_PROPERTY_DISPOSITIONS}),
        frozenset({LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS}),
    ),
    (
        SubtractNotBelowZero,
        frozenset(
            {LISTED_PERSONAL_PROPERTY_GAIN_OR_LOSS, UNAPPLIED_LISTED_PERSONAL_PROPERTY_LOSSES}
        ),
        frozenset({LISTED_PERSONAL_PROPERTY_NET_GAIN}),
    ),
    (
        Sum,
        frozenset(
            {
                QSBCS_GAIN_OR_LOSS,
                QFFP_GAIN_OR_LOSS,
                QFFP_FORECLOSURE_GAIN_OR_LOSS,
                SHARE_GAIN_OR_LOSS,
                REAL_ESTATE_GAIN_OR_LOSS,
                BOND_GAIN_OR_LOSS,
                CRYPTO_ASSET_GAIN_OR_LOSS,
                OTHER_FORECLOSURE_GAIN_OR_LOSS,
                PERSONAL_USE_PROPERTY_GAIN,
                LISTED_PERSONAL_PROPERTY_NET_GAIN,
            }
        ),
        frozenset({CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES}),
    ),
    (
        Subtract,
        frozenset(
            {CAPITAL_GAINS_OF_QUALIFIED_AND_OTHER_PROPERTIES, CAPITAL_GAINS_DEFERRAL_CHECKED}
        ),
        frozenset({CAPITAL_GAINS_AFTER_DEFERRAL}),
    ),
    (
        Sum,
        frozenset(
            {CAPITAL_GAINS_AFTER_DEFERRAL, SLIP_CAPITAL_GAINS_OR_LOSSES, T3_CAPITAL_GAINS_OR_LOSSES}
        ),
        frozenset({CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION}),
    ),
    (
        Subtract,
        frozenset(
            {CAPITAL_GAINS_BEFORE_INVESTMENT_LOSS_REDUCTION, BUSINESS_INVESTMENT_LOSS_REDUCTION}
        ),
        frozenset({CAPITAL_GAINS_BEFORE_RESERVES}),
    ),
    (RecordTotal, frozenset({T2017_LINE_31_EXPORT}), frozenset({SCHEDULE_3_LINE_19200})),
    (
        Sum,
        frozenset({CAPITAL_GAINS_BEFORE_RESERVES, SCHEDULE_3_LINE_19200}),
        frozenset({CAPITAL_GAIN}),
    ),
    (
        AtMost,
        frozenset({T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE, T3_TAXABLE_DIVIDENDS}),
        frozenset({T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE, T4PS_TAXABLE_DIVIDENDS}),
        frozenset({T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE, T5_TAXABLE_DIVIDENDS}),
        frozenset({T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
    ),
    (
        AtMost,
        frozenset({T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE, T5013_TAXABLE_DIVIDENDS}),
        frozenset({T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED}),
    ),
    (
        Sum,
        frozenset(
            {
                T3_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
                T4PS_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
                T5_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
                T5013_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
            }
        ),
        frozenset({SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE}),
    ),
    (
        Sum,
        frozenset(
            {
                T3_TAXABLE_DIVIDENDS,
                T4PS_TAXABLE_DIVIDENDS,
                T5_TAXABLE_DIVIDENDS,
                T5013_TAXABLE_DIVIDENDS,
            }
        ),
        frozenset({SLIP_TAXABLE_DIVIDENDS}),
    ),
    (
        ApplyFraction,
        frozenset({ELIGIBLE_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP}),
        frozenset({ELIGIBLE_DIVIDENDS_GROSSED_UP}),
    ),
    (
        ApplyFraction,
        frozenset({OTHER_DIVIDENDS_RECEIVED_WITHOUT_A_SLIP}),
        frozenset({OTHER_DIVIDENDS_GROSSED_UP}),
    ),
    (
        Sum,
        frozenset({ELIGIBLE_DIVIDENDS_GROSSED_UP, OTHER_DIVIDENDS_GROSSED_UP}),
        frozenset({DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP}),
    ),
    (
        Sum,
        frozenset(
            {
                SLIP_TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE,
                OTHER_DIVIDENDS_GROSSED_UP,
                T1206_UNDER_18_DIVIDEND_AMOUNT,
            }
        ),
        frozenset({TAXABLE_DIVIDENDS_OTHER_THAN_ELIGIBLE}),
    ),
    (
        Sum,
        frozenset(
            {
                SLIP_TAXABLE_DIVIDENDS,
                DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP,
                T1206_UNDER_18_DIVIDEND_AMOUNT,
            }
        ),
        frozenset({TAXABLE_DIVIDENDS}),
    ),
    (
        Sum,
        frozenset(
            {
                T3_INVESTMENT_INCOME,
                T5_INVESTMENT_INCOME,
                T5013_INVESTMENT_INCOME,
                INVESTMENT_INCOME_CREDITED_NOT_RECEIVED,
                TAX_REFUND_INTEREST,
                FOREIGN_INVESTMENT_INCOME,
                INVESTMENT_INCOME_WITHOUT_A_SLIP,
                INVESTMENT_ROYALTIES,
            }
        ),
        frozenset({INVESTMENT_INCOME_BEFORE_PRIOR_YEARS}),
    ),
    (
        AtMost,
        frozenset(
            {INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS, INVESTMENT_INCOME_BEFORE_PRIOR_YEARS}
        ),
        frozenset({INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED}),
    ),
    (
        Subtract,
        frozenset(
            {
                INVESTMENT_INCOME_BEFORE_PRIOR_YEARS,
                INVESTMENT_INCOME_REPORTED_IN_PREVIOUS_YEARS_APPLIED,
            }
        ),
        frozenset({INTEREST_AND_OTHER_INVESTMENT_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {WORKERS_COMPENSATION_BENEFITS, SOCIAL_ASSISTANCE_PAYMENTS, NET_FEDERAL_SUPPLEMENTS}
        ),
        frozenset({INCOME_SUPPORT_BENEFITS}),
    ),
    (
        Sum,
        frozenset(
            {
                EMPLOYMENT_INCOME,
                OTHER_EMPLOYMENT_INCOME,
                OLD_AGE_SECURITY,
                CPP_OR_QPP_BENEFITS,
                OTHER_PENSIONS_AND_SUPERANNUATION,
                T2205_ON_LINE_11500,
                ELECTED_SPLIT_PENSION_AMOUNT,
                UNIVERSAL_CHILD_CARE_BENEFIT,
                EI_AND_OTHER_BENEFITS,
                TAXABLE_DIVIDENDS,
                INTEREST_AND_OTHER_INVESTMENT_INCOME,
                NET_PARTNERSHIP_INCOME,
                RDSP_INCOME,
                NET_RENTAL_INCOME,
                TAXABLE_CAPITAL_GAINS,
                TAXABLE_SUPPORT_PAYMENTS,
                RRSP_INCOME,
                T2205_ON_LINE_12900,
                FHSA_INCOME,
                OTHER_FHSA_INCOME,
                OTHER_INCOME,
                T2205_ON_LINE_13000,
                TAXABLE_SCHOLARSHIPS,
                NET_SELF_EMPLOYMENT_INCOME,
                INCOME_SUPPORT_BENEFITS,
            }
        ),
        frozenset({TOTAL_INCOME}),
    ),
    (
        Sum,
        frozenset(
            {
                T3_DIVIDEND_TAX_CREDIT,
                T4PS_DIVIDEND_TAX_CREDIT,
                T5_DIVIDEND_TAX_CREDIT,
                T5013_DIVIDEND_TAX_CREDIT,
            }
        ),
        frozenset({SLIP_DIVIDEND_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset({DIVIDENDS_WITHOUT_A_SLIP_GROSSED_UP, T1206_UNDER_18_DIVIDEND_AMOUNT}),
        frozenset({DIVIDENDS_AMOUNT_A}),
    ),
    (
        Sum,
        frozenset({OTHER_DIVIDENDS_GROSSED_UP, T1206_UNDER_18_DIVIDEND_AMOUNT}),
        frozenset({DIVIDENDS_AMOUNT_B}),
    ),
    (ApplyRate, frozenset({DIVIDENDS_AMOUNT_B}), frozenset({OTHER_DIVIDENDS_CREDIT})),
    (
        Subtract,
        frozenset({DIVIDENDS_AMOUNT_A, DIVIDENDS_AMOUNT_B}),
        frozenset({DIVIDENDS_AMOUNT_A_LESS_B}),
    ),
    (
        ApplyRate,
        frozenset({DIVIDENDS_AMOUNT_A_LESS_B}),
        frozenset({ELIGIBLE_DIVIDENDS_CREDIT}),
    ),
    (
        Sum,
        frozenset({OTHER_DIVIDENDS_CREDIT, ELIGIBLE_DIVIDENDS_CREDIT}),
        frozenset({NO_SLIP_DIVIDEND_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset({SLIP_DIVIDEND_TAX_CREDIT, NO_SLIP_DIVIDEND_TAX_CREDIT}),
        frozenset({DIVIDEND_TAX_CREDIT}),
    ),
    (
        Sum,
        frozenset(
            {NON_REFUNDABLE_TAX_CREDITS, DIVIDEND_TAX_CREDIT, AMT_MINIMUM_TAX_CARRYOVER_APPLIED}
        ),
        frozenset({CREDITS_AGAINST_BASIC_FEDERAL_TAX}),
    ),
    (
        Sum,
        frozenset(
            {
                BUSINESS_INCOME,
                PROFESSIONAL_INCOME,
                COMMISSION_INCOME,
                FARMING_INCOME,
                FISHING_INCOME,
            }
        ),
        frozenset({NET_SELF_EMPLOYMENT_INCOME}),
    ),
    (
        CountByConditions,
        frozenset(
            {
                VOLUNTEER_FIREFIGHTERS_CONDITIONS_MET_CHECKED,
                SEARCH_AND_RESCUE_CONDITIONS_MET_CHECKED,
                EMERGENCY_SERVICES_VOLUNTEER_EXEMPT_INCOME,
            }
        ),
        frozenset({EMERGENCY_SERVICES_VOLUNTEER_CONFLICT}),
    ),
    (
        CountRefusedByConditions,
        frozenset({EMERGENCY_SERVICES_VOLUNTEER_CONFLICT}),
        frozenset({EMERGENCY_SERVICES_VOLUNTEER_CONFLICT_CHECKED}),
    ),
}
