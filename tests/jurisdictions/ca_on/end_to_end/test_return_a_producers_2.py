"""CA-ON 2025 end to end, Return A: return a producers 2."""

from __future__ import annotations

from tax_engine.domain.capabilities.apply_rate import ApplyRate
from tax_engine.domain.capabilities.at_most import AtMost
from tax_engine.domain.capabilities.capped_amount import CappedAmount
from tax_engine.domain.capabilities.choose_by_count import ChooseByCount
from tax_engine.domain.capabilities.credit_amount import CreditAmount
from tax_engine.domain.capabilities.lesser_of import LesserOf
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.subtract_not_below_zero import SubtractNotBelowZero
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capabilities.times_count import TimesCount
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_4 import (
    ForeignBusinessTaxCreditLine4,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_5 import (
    ForeignBusinessTaxCreditLine5,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_7 import (
    ForeignBusinessTaxCreditLine7,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_8 import (
    ForeignBusinessTaxCreditLine8,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_10 import (
    ForeignBusinessTaxCreditLine10,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_business_tax_credit_line_11 import (
    ForeignBusinessTaxCreditLine11,
)
from tax_engine.jurisdictions.ca.capabilities.foreign_non_business_tax_credit import (
    ForeignNonBusinessTaxCredit,
)
from tax_engine.jurisdictions.ca.capabilities.lesser_of_when_positive import (
    LesserOfWhenPositive,
)
from tax_engine.jurisdictions.ca.capabilities.threshold_gate import ThresholdGate
from tax_engine.jurisdictions.ca.catalog import (
    ACWB_PAID_TO_YOU,
    ADVANCED_CANADA_WORKERS_BENEFIT,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT,
    BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX,
    CREDITS_AGAINST_FEDERAL_TAX,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EDUCATOR_SUPPLIES_EXPENSES,
    EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT,
    FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT,
    FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_AFTER_CREDITS,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT,
    FEDERAL_TAX_LINE_41700,
    FEDERAL_TAX_WITH_ITC_RECAPTURE,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_4,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_5,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_7,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_8,
    FOREIGN_BUSINESS_TAX_CREDIT_LINE_10,
    FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX,
    FOREIGN_TAX_CREDIT_NET_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME,
    FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS,
    FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME,
    ITC_RECAPTURE,
    ITC_RECAPTURE_AT_15_PERCENT,
    ITC_RECAPTURE_AT_20_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
    JOURNALISM_LABOUR_TAX_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
    LABOUR_SPONSORED_FUNDS_NET_COST,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4,
    MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
    MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
    MEDICAL_SUPPLEMENT_IF_RESIDENT,
    MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET,
    MEDICAL_SUPPLEMENT_INCOME_THRESHOLD,
    MEDICAL_SUPPLEMENT_LINE_6,
    MEDICAL_SUPPLEMENT_LINE_8,
    MEDICAL_SUPPLEMENT_LINE_11,
    MEDICAL_SUPPLEMENT_LINE_13,
    MEDICAL_SUPPLEMENT_LINE_14,
    MEDICAL_SUPPLEMENT_LINE_15,
    MEDICAL_SUPPLEMENT_LINE_16,
    MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
    MEDICAL_SUPPLEMENT_WORKING_INCOME,
    NET_FEDERAL_TAX,
    PART_XII_2_TAX_CREDIT,
    POLITICAL_CREDIT,
    POLITICAL_CREDIT_BEFORE_MAXIMUM,
    POLITICAL_CREDIT_CHOSEN_COLUMN,
    POLITICAL_CREDIT_SHORTCUT_AMOUNT,
    POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
    PROVINCIAL_CREDITS,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    RESP_AIPS_ADDITIONAL_TAX,
    RESP_AIPS_CONTRIBUTIONS_COUNTED,
    RESP_AIPS_LIFETIME_LIMIT,
    RESP_AIPS_LIMIT_REMAINING,
    RESP_AIPS_PART_A_APPLIES,
    RESP_AIPS_PART_A_TAX,
    RESP_AIPS_PART_B_TAX,
    RESP_AIPS_RECEIVED_PART_A,
    RESP_AIPS_RECEIVED_PART_B,
    RESP_AIPS_REDUCTION,
    RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
    RESP_AIPS_RRSP_CONTRIBUTIONS,
    RESP_AIPS_SUBJECT_TO_TAX,
    RL_10_LABOUR_SPONSORED_FUND_AMOUNT,
    SPECIAL_TAXES,
    TAX_PAID_BY_INSTALMENTS,
    TOTAL_CREDITS,
    TOTAL_PAYABLE,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tax_engine.jurisdictions.ca_on.capabilities.choose_by_range import ChooseByRange
from tax_engine.jurisdictions.ca_on.capabilities.coop_education_credit import (
    CoopEducationCredit,
)
from tax_engine.jurisdictions.ca_on.capabilities.flow_through_share_expenses import (
    FlowThroughShareExpenses,
)
from tax_engine.jurisdictions.ca_on.capabilities.quotient import Quotient
from tax_engine.jurisdictions.ca_on.capabilities.record_count import RecordCount
from tax_engine.jurisdictions.ca_on.catalog import (
    CLAIMS_SENIORS_CARE_CREDIT,
    COOP_EDUCATION_CREDIT,
    COOP_EDUCATION_FULL_SHARE,
    COOP_EDUCATION_PAYROLL_OVER_THRESHOLD,
    COOP_EDUCATION_PAYROLL_RANGE,
    COOP_EDUCATION_PAYROLL_THRESHOLD,
    COOP_EDUCATION_PHASE_OUT_SHARE,
    COOP_EDUCATION_PLACEMENT_COUNT,
    COOP_EDUCATION_REMAINING_SHARE,
    FERTILITY_CREDIT_BEFORE_MAXIMUM,
    FLOW_THROUGH_SHARE_CREDIT,
    FLOW_THROUGH_SHARE_EXPENSES,
    ONTARIO_CREDITS,
    ONTARIO_CREDITS_SUBTOTAL,
    ONTARIO_TAX,
    SENIORS_CARE_AMOUNT,
    SENIORS_CARE_BASE_AMOUNT,
    SENIORS_CARE_BEFORE_CLAIM,
    SENIORS_CARE_BEFORE_MAXIMUM,
    SENIORS_CARE_CREDIT,
    SENIORS_CARE_FAMILY_NET_INCOME,
    SENIORS_CARE_INCOME_OVER_BASE,
    SENIORS_CARE_REDUCTION,
    SENIORS_TRANSIT_CREDIT,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    FEDERAL_POLITICAL_COLUMN_LINES,
    POLITICAL_COLUMN_LINES,
    return_a,
)


def test_each_amount_is_produced_by_its_capability() -> None:
    worksheet = return_a()
    assert isinstance(worksheet.producer_of(SENIORS_CARE_BEFORE_MAXIMUM), ApplyRate)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_AMOUNT), CappedAmount)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_FAMILY_NET_INCOME), Sum)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_BASE_AMOUNT), CreditAmount)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_INCOME_OVER_BASE), SubtractNotBelowZero)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_REDUCTION), ApplyRate)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_BEFORE_CLAIM), SubtractNotBelowZero)
    assert isinstance(worksheet.producer_of(SENIORS_CARE_CREDIT), TimesCount)
    assert worksheet.producer_of(SENIORS_CARE_BEFORE_MAXIMUM) is not worksheet.producer_of(
        SENIORS_CARE_REDUCTION
    )
    assert worksheet.producer_of(SENIORS_CARE_INCOME_OVER_BASE) is not worksheet.producer_of(
        SENIORS_CARE_BEFORE_CLAIM
    )
    assert worksheet.producer_of(SENIORS_CARE_BEFORE_MAXIMUM) is not worksheet.producer_of(
        FERTILITY_CREDIT_BEFORE_MAXIMUM
    )
    assert worksheet.producer_of(CLAIMS_SENIORS_CARE_CREDIT) is None
    for column in (1, 2, 3):
        assert isinstance(worksheet.producer_of(POLITICAL_COLUMN_LINES[column][2]), CreditAmount)
        assert isinstance(
            worksheet.producer_of(POLITICAL_COLUMN_LINES[column][3]), SubtractNotBelowZero
        )
        assert isinstance(worksheet.producer_of(POLITICAL_COLUMN_LINES[column][5]), ApplyRate)
        assert isinstance(worksheet.producer_of(POLITICAL_COLUMN_LINES[column][6]), CreditAmount)
        assert isinstance(worksheet.producer_of(POLITICAL_COLUMN_LINES[column][7]), Sum)
    assert isinstance(worksheet.producer_of(ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM), ChooseByRange)
    assert isinstance(worksheet.producer_of(ontario.POLITICAL_CREDIT), CappedAmount)
    assert worksheet.producer_of(ontario.POLITICAL_CREDIT) is not worksheet.producer_of(
        ontario.POLITICAL_CREDIT_BEFORE_MAXIMUM
    )
    assert isinstance(worksheet.producer_of(FLOW_THROUGH_SHARE_EXPENSES), FlowThroughShareExpenses)
    assert isinstance(worksheet.producer_of(FLOW_THROUGH_SHARE_CREDIT), ApplyRate)
    assert worksheet.producer_of(FLOW_THROUGH_SHARE_CREDIT) is not worksheet.producer_of(
        SENIORS_TRANSIT_CREDIT
    )
    assert isinstance(worksheet.producer_of(ONTARIO_CREDITS_SUBTOTAL), Sum)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_PAYROLL_THRESHOLD), CreditAmount)
    assert isinstance(
        worksheet.producer_of(COOP_EDUCATION_PAYROLL_OVER_THRESHOLD), SubtractNotBelowZero
    )
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_PAYROLL_RANGE), CreditAmount)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_PHASE_OUT_SHARE), Quotient)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_FULL_SHARE), CreditAmount)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_REMAINING_SHARE), SubtractNotBelowZero)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_CREDIT), CoopEducationCredit)
    assert isinstance(worksheet.producer_of(COOP_EDUCATION_PLACEMENT_COUNT), RecordCount)
    assert worksheet.producer_of(COOP_EDUCATION_PAYROLL_THRESHOLD) is not worksheet.producer_of(
        COOP_EDUCATION_PAYROLL_RANGE
    )
    assert worksheet.producer_of(COOP_EDUCATION_PAYROLL_OVER_THRESHOLD) is not (
        worksheet.producer_of(COOP_EDUCATION_REMAINING_SHARE)
    )
    assert isinstance(worksheet.producer_of(ONTARIO_CREDITS), Sum)
    assert isinstance(worksheet.producer_of(PROVINCIAL_CREDITS), Sum)
    assert (
        len(
            {
                id(worksheet.producer_of(kind))
                for kind in (
                    ONTARIO_CREDITS_SUBTOTAL,
                    ONTARIO_CREDITS,
                    PROVINCIAL_CREDITS,
                    TOTAL_CREDITS,
                )
            }
        )
        == 4
    )
    assert isinstance(worksheet.producer_of(TOTAL_CREDITS), Sum)
    assert worksheet.producer_of(NET_FEDERAL_TAX) is not worksheet.producer_of(TOTAL_PAYABLE)
    assert worksheet.producer_of(NET_FEDERAL_TAX) is not worksheet.producer_of(TOTAL_CREDITS)
    assert worksheet.producer_of(TOTAL_PAYABLE) is not worksheet.producer_of(TOTAL_CREDITS)
    assert worksheet.producer_of(TOTAL_PAYABLE) is not worksheet.producer_of(ONTARIO_TAX)
    assert isinstance(worksheet.producer_of(REFUND_OR_BALANCE_OWING), Subtract)
    assert isinstance(
        worksheet.producer_of(EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM), CappedAmount
    )
    assert isinstance(worksheet.producer_of(EDUCATOR_SCHOOL_SUPPLY_CREDIT), ApplyRate)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME), Sum)
    assert isinstance(
        worksheet.producer_of(MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS), Subtract
    )
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS), Sum)
    assert isinstance(
        worksheet.producer_of(MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME), SubtractNotBelowZero
    )
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_WORKING_INCOME), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3), Sum)
    assert isinstance(
        worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5), SubtractNotBelowZero
    )
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4), Sum)
    assert isinstance(
        worksheet.producer_of(MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5), SubtractNotBelowZero
    )
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_6), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_INCOME_THRESHOLD), CreditAmount)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_8), SubtractNotBelowZero)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_11), Sum)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_13), ApplyRate)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_14), CappedAmount)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_15), ApplyRate)
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_16), SubtractNotBelowZero)
    assert isinstance(
        worksheet.producer_of(MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET), ThresholdGate
    )
    assert isinstance(worksheet.producer_of(MEDICAL_SUPPLEMENT_IF_RESIDENT), TimesCount)
    assert isinstance(worksheet.producer_of(REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT), TimesCount)
    assert worksheet.producer_of(MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET) is not (
        worksheet.producer_of(MEDICAL_SUPPLEMENT_LINE_16)
    )
    for kind in (
        PART_XII_2_TAX_CREDIT,
        EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
        EDUCATOR_SUPPLIES_EXPENSES,
        TAX_PAID_BY_INSTALMENTS,
        ontario.OPPORTUNITIES_FUND_DONATION,
    ):
        assert worksheet.producer_of(kind) is None, kind
    assert isinstance(worksheet.producer_of(JOURNALISM_LABOUR_TAX_CREDIT), RecordTotal)
    assert isinstance(worksheet.producer_of(REFUND), SubtractNotBelowZero)
    assert worksheet.producer_of(REFUND) is not worksheet.producer_of(REFUND_OR_BALANCE_OWING)
    assert isinstance(worksheet.producer_of(ontario.REFUND_BEFORE_DONATION), Sum)
    assert isinstance(worksheet.producer_of(ontario.OPPORTUNITIES_FUND_DONATION_CHECKED), AtMost)
    assert isinstance(worksheet.producer_of(ontario.NET_REFUND), Subtract)
    assert isinstance(worksheet.producer_of(ITC_RECAPTURE_AT_15_PERCENT), ApplyRate)
    assert isinstance(worksheet.producer_of(ITC_RECAPTURE_AT_20_PERCENT), ApplyRate)
    assert worksheet.producer_of(ITC_RECAPTURE_AT_15_PERCENT) is not worksheet.producer_of(
        ITC_RECAPTURE_AT_20_PERCENT
    )
    assert isinstance(worksheet.producer_of(ITC_RECAPTURE), Sum)
    assert isinstance(worksheet.producer_of(FEDERAL_TAX_WITH_ITC_RECAPTURE), Sum)
    # Form T2209 and T1 lines 128 to 130: net income (note 3) and basic federal tax (note 4), line 3
    # over the countries, lines 4 to 11, line 13 limited to line 42900, and line 130.
    assert isinstance(worksheet.producer_of(FOREIGN_TAX_CREDIT_NET_INCOME_DEDUCTIONS), Sum)
    assert isinstance(
        worksheet.producer_of(FOREIGN_TAX_CREDIT_NET_INCOME_BEFORE_SPLIT_INCOME), Subtract
    )
    assert isinstance(worksheet.producer_of(FOREIGN_TAX_CREDIT_NET_INCOME_WITH_SPLIT_INCOME), Sum)
    assert isinstance(worksheet.producer_of(FOREIGN_TAX_CREDIT_NET_INCOME), Subtract)
    assert isinstance(worksheet.producer_of(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT), Sum)
    assert isinstance(worksheet.producer_of(BASIC_FEDERAL_TAX_WITH_DIVIDEND_CREDIT_AND_SURTAX), Sum)
    assert isinstance(
        worksheet.producer_of(FOREIGN_TAX_CREDIT_BASIC_FEDERAL_TAX), SubtractNotBelowZero
    )
    assert isinstance(
        worksheet.producer_of(FEDERAL_NON_BUSINESS_FOREIGN_TAX_CREDIT), ForeignNonBusinessTaxCredit
    )
    for kind, cls in (
        (FOREIGN_BUSINESS_TAX_CREDIT_LINE_4, ForeignBusinessTaxCreditLine4),
        (FOREIGN_BUSINESS_TAX_CREDIT_LINE_5, ForeignBusinessTaxCreditLine5),
        (FOREIGN_BUSINESS_TAX_CREDIT_LINE_7, ForeignBusinessTaxCreditLine7),
        (FOREIGN_BUSINESS_TAX_CREDIT_LINE_8, ForeignBusinessTaxCreditLine8),
        (FOREIGN_BUSINESS_TAX_CREDIT_LINE_10, ForeignBusinessTaxCreditLine10),
        (FEDERAL_BUSINESS_FOREIGN_TAX_CREDIT, ForeignBusinessTaxCreditLine11),
    ):
        assert isinstance(worksheet.producer_of(kind), cls)
    assert isinstance(worksheet.producer_of(FEDERAL_FOREIGN_TAX_CREDIT_BEFORE_LIMIT), Sum)
    assert isinstance(worksheet.producer_of(FEDERAL_FOREIGN_TAX_CREDIT), LesserOfWhenPositive)
    assert isinstance(worksheet.producer_of(FEDERAL_TAX_LESS_FOREIGN_TAX_CREDIT), Subtract)
    assert worksheet.producer_of(FEDERAL_TAX_WITH_ITC_RECAPTURE) is not worksheet.producer_of(
        NET_FEDERAL_TAX
    )
    assert isinstance(
        worksheet.producer_of(LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM), ApplyRate
    )
    assert isinstance(worksheet.producer_of(LABOUR_SPONSORED_FUNDS_CREDIT), CappedAmount)
    for column in (1, 2, 3):
        assert isinstance(
            worksheet.producer_of(FEDERAL_POLITICAL_COLUMN_LINES[column][2]), CreditAmount
        )
        assert isinstance(
            worksheet.producer_of(FEDERAL_POLITICAL_COLUMN_LINES[column][3]), SubtractNotBelowZero
        )
        assert isinstance(
            worksheet.producer_of(FEDERAL_POLITICAL_COLUMN_LINES[column][5]), ApplyRate
        )
        assert isinstance(
            worksheet.producer_of(FEDERAL_POLITICAL_COLUMN_LINES[column][6]), CreditAmount
        )
        assert isinstance(worksheet.producer_of(FEDERAL_POLITICAL_COLUMN_LINES[column][7]), Sum)
    assert isinstance(worksheet.producer_of(POLITICAL_CREDIT_CHOSEN_COLUMN), ChooseByRange)
    assert isinstance(worksheet.producer_of(POLITICAL_CREDIT_SHORTCUT_THRESHOLD), CreditAmount)
    assert isinstance(worksheet.producer_of(POLITICAL_CREDIT_SHORTCUT_AMOUNT), CreditAmount)
    assert isinstance(worksheet.producer_of(POLITICAL_CREDIT_BEFORE_MAXIMUM), ChooseByRange)
    assert worksheet.producer_of(POLITICAL_CREDIT_BEFORE_MAXIMUM) is not worksheet.producer_of(
        POLITICAL_CREDIT_CHOSEN_COLUMN
    )
    assert isinstance(worksheet.producer_of(POLITICAL_CREDIT), CappedAmount)
    assert isinstance(worksheet.producer_of(CREDITS_AGAINST_FEDERAL_TAX), Sum)
    assert isinstance(worksheet.producer_of(FEDERAL_TAX_LESS_CREDITS), SubtractNotBelowZero)
    assert worksheet.producer_of(FEDERAL_TAX_LESS_CREDITS) is not worksheet.producer_of(
        FEDERAL_TAX_AFTER_CREDITS
    )
    # T1 line 139 and line 41700: chosen by the count of "line 11 is positive", between the federal
    # tax less credits and Part 6 line 14 of Form T691.
    assert isinstance(worksheet.producer_of(FEDERAL_TAX_LINE_41700), ChooseByCount)
    assert worksheet.producer_of(FEDERAL_TAX_LINE_41700) is not worksheet.producer_of(
        FEDERAL_TAX_LESS_CREDITS
    )
    assert isinstance(worksheet.producer_of(RESP_AIPS_CONTRIBUTIONS_COUNTED), LesserOf)
    assert isinstance(worksheet.producer_of(RESP_AIPS_LIFETIME_LIMIT), CreditAmount)
    assert isinstance(worksheet.producer_of(RESP_AIPS_LIMIT_REMAINING), Subtract)
    assert isinstance(worksheet.producer_of(RESP_AIPS_REDUCTION), LesserOf)
    assert worksheet.producer_of(RESP_AIPS_REDUCTION) is not worksheet.producer_of(
        RESP_AIPS_CONTRIBUTIONS_COUNTED
    )
    assert isinstance(worksheet.producer_of(RESP_AIPS_SUBJECT_TO_TAX), Subtract)
    assert isinstance(worksheet.producer_of(RESP_AIPS_PART_A_TAX), ApplyRate)
    assert isinstance(worksheet.producer_of(RESP_AIPS_PART_B_TAX), ApplyRate)
    assert worksheet.producer_of(RESP_AIPS_PART_A_TAX) is not worksheet.producer_of(
        RESP_AIPS_PART_B_TAX
    )
    assert isinstance(worksheet.producer_of(RESP_AIPS_ADDITIONAL_TAX), ChooseByCount)
    assert isinstance(worksheet.producer_of(SPECIAL_TAXES), Sum)
    assert isinstance(worksheet.producer_of(ADVANCED_CANADA_WORKERS_BENEFIT), LesserOf)
    for kind in (
        ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
        ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
        LABOUR_SPONSORED_FUNDS_NET_COST,
        ACWB_PAID_TO_YOU,
        RESP_AIPS_RECEIVED_PART_A,
        RESP_AIPS_RRSP_CONTRIBUTIONS,
        RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
        RESP_AIPS_RECEIVED_PART_B,
        RL_10_LABOUR_SPONSORED_FUND_AMOUNT,
    ):
        assert worksheet.producer_of(kind) is None, kind
    assert worksheet.producer_of(RESP_AIPS_PART_A_APPLIES) is None
