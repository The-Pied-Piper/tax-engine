"""Registered and money kinds of the federal catalog family `refundable_credits`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    CANADA_TRAINING_CREDIT,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EDUCATOR_SUPPLIES_EXPENSES,
    EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    HOME_RENOVATION_CLAIMED_BY_OTHERS,
    HOME_RENOVATION_EXPENDITURES,
    HOME_RENOVATION_LINE_3,
    HOME_RENOVATION_LINE_6,
    HOME_RENOVATION_LINE_8,
    HOME_RENOVATION_REIMBURSED,
    HOME_RENOVATIONS,
    JOURNALISM_LABOUR_TAX_CREDIT,
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
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
    NET_BUSINESS_INCOME,
    NET_COMMISSION_INCOME,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    NET_PROFESSIONAL_INCOME,
    PART_XII_2_TAX_CREDIT,
    PROVINCIAL_CREDITS,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    TAX_PAID_BY_INSTALMENTS,
)


def test_the_refundable_credits_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/provincial_credits") is PROVINCIAL_CREDITS
    assert registry.get("ca/canada_training_credit") is CANADA_TRAINING_CREDIT
    assert registry.get("ca/part_xii_2_tax_credit") is PART_XII_2_TAX_CREDIT
    assert (
        registry.get("ca/employee_and_partner_gst_hst_rebate")
        is EMPLOYEE_AND_PARTNER_GST_HST_REBATE
    )
    assert registry.get("ca/educator_supplies_expenses") is EDUCATOR_SUPPLIES_EXPENSES
    assert (
        registry.get("ca/educator_supplies_expenses_at_most_maximum")
        is EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM
    )
    assert registry.get("ca/educator_school_supply_credit") is EDUCATOR_SCHOOL_SUPPLY_CREDIT
    assert registry.get("ca/journalism_labour_tax_credit") is JOURNALISM_LABOUR_TAX_CREDIT
    assert registry.get("ca/tax_paid_by_instalments") is TAX_PAID_BY_INSTALMENTS
    assert registry.get("ca/net_business_income") is NET_BUSINESS_INCOME
    assert registry.get("ca/net_professional_income") is NET_PROFESSIONAL_INCOME
    assert registry.get("ca/net_commission_income") is NET_COMMISSION_INCOME
    assert registry.get("ca/net_farming_income") is NET_FARMING_INCOME
    assert registry.get("ca/net_fishing_income") is NET_FISHING_INCOME
    assert (
        registry.get("ca/medical_supplement_employment_income")
        is MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME
    )
    assert (
        registry.get("ca/medical_supplement_employment_income_less_wage_loss")
        is MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS
    )
    assert (
        registry.get("ca/medical_supplement_employment_deductions")
        is MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS
    )
    assert (
        registry.get("ca/medical_supplement_employment_working_income")
        is MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME
    )
    assert (
        registry.get("ca/medical_supplement_self_employment_income")
        is MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME
    )
    assert registry.get("ca/medical_supplement_working_income") is MEDICAL_SUPPLEMENT_WORKING_INCOME
    assert (
        registry.get("ca/medical_supplement_column_1_line_3") is MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3
    )
    assert (
        registry.get("ca/medical_supplement_column_1_line_5") is MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5
    )
    assert (
        registry.get("ca/medical_supplement_column_2_line_2") is MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2
    )
    assert (
        registry.get("ca/medical_supplement_column_2_line_3") is MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3
    )
    assert (
        registry.get("ca/medical_supplement_column_2_line_4") is MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4
    )
    assert (
        registry.get("ca/medical_supplement_column_2_line_5") is MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5
    )
    assert registry.get("ca/medical_supplement_line_6") is MEDICAL_SUPPLEMENT_LINE_6
    assert (
        registry.get("ca/medical_supplement_income_threshold")
        is MEDICAL_SUPPLEMENT_INCOME_THRESHOLD
    )
    assert registry.get("ca/medical_supplement_line_8") is MEDICAL_SUPPLEMENT_LINE_8
    assert registry.get("ca/medical_supplement_line_11") is MEDICAL_SUPPLEMENT_LINE_11
    assert registry.get("ca/medical_supplement_line_13") is MEDICAL_SUPPLEMENT_LINE_13
    assert registry.get("ca/medical_supplement_line_14") is MEDICAL_SUPPLEMENT_LINE_14
    assert registry.get("ca/medical_supplement_line_15") is MEDICAL_SUPPLEMENT_LINE_15
    assert registry.get("ca/medical_supplement_line_16") is MEDICAL_SUPPLEMENT_LINE_16
    assert (
        registry.get("ca/medical_supplement_if_working_income_met")
        is MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET
    )
    assert registry.get("ca/medical_supplement_if_resident") is MEDICAL_SUPPLEMENT_IF_RESIDENT
    assert (
        registry.get("ca/refundable_medical_expense_supplement")
        is REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT
    )


def test_the_refundable_credits_kinds_are_money() -> None:
    for kind in (
        PROVINCIAL_CREDITS,
        CANADA_TRAINING_CREDIT,
        PART_XII_2_TAX_CREDIT,
        EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
        EDUCATOR_SUPPLIES_EXPENSES,
        EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
        EDUCATOR_SCHOOL_SUPPLY_CREDIT,
        JOURNALISM_LABOUR_TAX_CREDIT,
        TAX_PAID_BY_INSTALMENTS,
        NET_BUSINESS_INCOME,
        NET_PROFESSIONAL_INCOME,
        NET_COMMISSION_INCOME,
        NET_FARMING_INCOME,
        NET_FISHING_INCOME,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
        MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
        MEDICAL_SUPPLEMENT_WORKING_INCOME,
        MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
        MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_4,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_5,
        MEDICAL_SUPPLEMENT_LINE_6,
        MEDICAL_SUPPLEMENT_INCOME_THRESHOLD,
        MEDICAL_SUPPLEMENT_LINE_8,
        MEDICAL_SUPPLEMENT_LINE_11,
        MEDICAL_SUPPLEMENT_LINE_13,
        MEDICAL_SUPPLEMENT_LINE_14,
        MEDICAL_SUPPLEMENT_LINE_15,
        MEDICAL_SUPPLEMENT_LINE_16,
        MEDICAL_SUPPLEMENT_IF_WORKING_INCOME_MET,
        MEDICAL_SUPPLEMENT_IF_RESIDENT,
        REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_home_renovation_kinds_are_registered_and_money(registry: ArtifactRegistry) -> None:
    # Schedule 12 line 1, line 2 and line 5 (the record's fields), lines 3, 6 and 8 (the totals over
    # the renovations) and T1 line 45355 (the credit, line 10 of Schedule 12).
    assert registry.get("ca/home_renovation_expenditures") is HOME_RENOVATION_EXPENDITURES
    assert registry.get("ca/home_renovation_reimbursed") is HOME_RENOVATION_REIMBURSED
    assert registry.get("ca/home_renovation_claimed_by_others") is HOME_RENOVATION_CLAIMED_BY_OTHERS
    assert registry.get("ca/home_renovation_line_3") is HOME_RENOVATION_LINE_3
    assert registry.get("ca/home_renovation_line_6") is HOME_RENOVATION_LINE_6
    assert registry.get("ca/home_renovation_line_8") is HOME_RENOVATION_LINE_8
    assert (
        registry.get("ca/multigenerational_home_renovation_credit")
        is MULTIGENERATIONAL_HOME_RENOVATION_CREDIT
    )
    for kind in (
        HOME_RENOVATION_EXPENDITURES,
        HOME_RENOVATION_REIMBURSED,
        HOME_RENOVATION_CLAIMED_BY_OTHERS,
        HOME_RENOVATION_LINE_3,
        HOME_RENOVATION_LINE_6,
        HOME_RENOVATION_LINE_8,
        MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_home_renovation_fields_are_non_negative_inputs() -> None:
    for kind in (
        HOME_RENOVATION_EXPENDITURES,
        HOME_RENOVATION_REIMBURSED,
        HOME_RENOVATION_CLAIMED_BY_OTHERS,
    ):
        assert kind.non_negative is True, kind.identifier


def test_the_multigenerational_home_renovation_credit_is_non_negative() -> None:
    # Line 10 of Schedule 12: line 8 multiplied by 14.5%, the amount for T1 line 45355.
    assert MULTIGENERATIONAL_HOME_RENOVATION_CREDIT.identifier == (
        "ca/multigenerational_home_renovation_credit"
    )
    assert MULTIGENERATIONAL_HOME_RENOVATION_CREDIT.non_negative is True


def test_the_home_renovations_are_a_record_list_of_three_fields(registry: ArtifactRegistry) -> None:
    # Schedule 12 Step 1: the table of each qualifying renovation, one record for each, holding
    # line 1 (total qualifying expenditures), line 2 (reimbursed) and line 5 (claimed by other
    # eligible individuals). The caller lists the renovations, so there is no eligibility field.
    assert isinstance(HOME_RENOVATIONS, RecordListKind)
    assert HOME_RENOVATIONS.identifier == "ca/home_renovations"
    assert HOME_RENOVATIONS.value_type is RecordList
    assert HOME_RENOVATIONS.fields == (
        HOME_RENOVATION_EXPENDITURES,
        HOME_RENOVATION_REIMBURSED,
        HOME_RENOVATION_CLAIMED_BY_OTHERS,
    )
    assert registry.get("ca/home_renovations") is HOME_RENOVATIONS
