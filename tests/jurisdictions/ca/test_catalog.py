"""Snapshot of the `ca/` artifact kind identifiers, as the application registers them.

Identifiers appear in stored results and in what callers receive, so changing or removing one is a
breaking change: update this snapshot only on purpose. Each package snapshots its own namespace;
declaring a kind in this package's catalog adds it here. The kinds are registered explicitly,
as the composition root does, into a fresh registry. The snapshot itself is `REGISTERED` in
`catalog_snapshot.py`; the per-family checks are in `test_catalog_<family>.py`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import Artifact, ArtifactCatalog, ArtifactKind, ArtifactRegistry
from tax_engine.domain.errors import InvalidRecordError, NegativeArtifactError
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    ADVANCED_CANADA_WORKERS_BENEFIT,
    AGED_18_OR_OLDER_AT_END_OF_2025,
    CAREGIVER_AMOUNT,
    CATALOG,
    CCA_ADDITIONS,
    CCA_AIIP_ADDITIONS,
    CCA_CHANGE_IN_USE,
    CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_CLAIMED,
    CCA_CLASS_NUMBER,
    CCA_DIEP_ADDITIONS,
    CCA_DIEP_PROCEEDS,
    CCA_HALF_YEAR_RULE_DIFFERS,
    CCA_IMMEDIATE_EXPENSING,
    CCA_NO_PROPERTY_LEFT,
    CCA_PERSONAL_PART_REMAINING,
    CCA_PROCEEDS,
    CCA_RATE_ELECTION,
    CCA_RIIP_ADDITIONS,
    CCA_SOLD_ZEPVS,
    CCA_UCC_AT_END,
    CCA_UCC_AT_START,
    CCA_VEHICLE_ACQUIRED_YEAR,
    CCA_VEHICLE_CHANGE_IN_USE,
    CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
    CCA_VEHICLE_COST,
    CCA_VEHICLE_FROM_NON_ARMS_LENGTH,
    CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
    CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
    CCA_VEHICLE_SELLER_COST,
    CCA_ZEPV_DIEP_PROCEEDS,
    CCA_ZEPV_PROCEEDS,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    CREDITS_AGAINST_FEDERAL_TAX,
    DEDUCTIONS_FROM_TOTAL_INCOME,
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_NET_INCOME,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
    DISABILITY_DEPENDANTS,
    DISABILITY_TRANSFERRED_AMOUNT,
    EDUCATOR_SCHOOL_SUPPLY_CREDIT,
    EDUCATOR_SUPPLIES_EXPENSES,
    EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
    FEDERAL_TAX_LESS_CREDITS,
    FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76,
    FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
    FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
    FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
    FHSA_ANNUAL_LIMIT,
    FHSA_ANNUAL_LIMIT_FROM_STEP_2,
    FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
    FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_AVAILABLE,
    FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
    FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
    FHSA_CONTRIBUTIONS_LIMIT,
    FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
    FHSA_DEDUCTION,
    FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
    FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
    FHSA_MAXIMUM_DEDUCTION,
    FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED,
    FHSA_NET_RRSP_TRANSFER_AMOUNT,
    FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
    FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
    FHSA_TOTAL_ANNUAL_LIMITS,
    FHSA_TOTAL_DESIGNATED_TRANSFERS,
    FHSA_TOTAL_RRSP_TRANSFERS,
    FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
    FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
    FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
    INCOME_TAX_DEDUCTED,
    INFIRM_DEPENDANTS,
    ITC_RECAPTURE,
    ITC_RECAPTURE_AT_15_PERCENT,
    ITC_RECAPTURE_AT_20_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
    ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
    JOURNALISM_LABOUR_TAX_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT,
    LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
    LABOUR_SPONSORED_FUNDS_NET_COST,
    MEDICAL_CLAIM,
    MEDICAL_EXPENSES,
    MEDICAL_EXPENSES_OVER_THRESHOLD,
    MEDICAL_NET_INCOME_SHARE,
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
    MEDICAL_THRESHOLD,
    NET_BUSINESS_INCOME,
    NET_COMMISSION_INCOME,
    NET_FARMING_INCOME,
    NET_FISHING_INCOME,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_PROFESSIONAL_INCOME,
    OTHER_DEPENDANT_MEDICAL_EXPENSES,
    OTHER_DEPENDANTS,
    OTHER_DEPENDANTS_MEDICAL,
    OTHER_EMPLOYMENT_EXPENSES,
    PART_XII_2_TAX_CREDIT,
    POLITICAL_CONTRIBUTIONS,
    POLITICAL_CREDIT,
    POLITICAL_CREDIT_BEFORE_MAXIMUM,
    POLITICAL_CREDIT_CHOSEN_COLUMN,
    POLITICAL_CREDIT_COLUMN_1_LINE_2,
    POLITICAL_CREDIT_COLUMN_1_LINE_3,
    POLITICAL_CREDIT_COLUMN_1_LINE_5,
    POLITICAL_CREDIT_COLUMN_1_LINE_6,
    POLITICAL_CREDIT_COLUMN_1_LINE_7,
    POLITICAL_CREDIT_COLUMN_2_LINE_2,
    POLITICAL_CREDIT_COLUMN_2_LINE_3,
    POLITICAL_CREDIT_COLUMN_2_LINE_5,
    POLITICAL_CREDIT_COLUMN_2_LINE_6,
    POLITICAL_CREDIT_COLUMN_2_LINE_7,
    POLITICAL_CREDIT_COLUMN_3_LINE_2,
    POLITICAL_CREDIT_COLUMN_3_LINE_3,
    POLITICAL_CREDIT_COLUMN_3_LINE_5,
    POLITICAL_CREDIT_COLUMN_3_LINE_6,
    POLITICAL_CREDIT_COLUMN_3_LINE_7,
    POLITICAL_CREDIT_SHORTCUT_AMOUNT,
    POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_PROPERTIES,
    REFUND,
    REFUND_OR_BALANCE_OWING,
    REFUNDABLE_MEDICAL_EXPENSE_SUPPLEMENT,
    RESIDENCE_ADJUSTED_COST_BASE,
    RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
    RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    RESIDENCE_FMV_DEC_31_1981,
    RESIDENCE_OUTLAYS,
    RESIDENCE_PART_2_APPLIES,
    RESIDENCE_PLUS_ONE_YEAR,
    RESIDENCE_PROCEEDS,
    RESIDENCE_T664_FILED,
    RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
    RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    RESIDENCE_WS_DESIGNATED_PROCEEDS,
    RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
    RESIDENCE_WS_FMV_FEB_22_1994,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
    RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
    RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
    RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_YEARS_OWNED_1972_TO_1981,
    RESIDENCE_YEARS_OWNED_AFTER_1981,
    RESIDENT_IN_CANADA_THROUGHOUT_2025,
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
    RRSP_AMOUNT_DEDUCTED,
    SPECIAL_TAXES,
    SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
    SPOUSE_RDSP_INCOME,
    SPOUSE_RDSP_INCOME_REPAYMENT,
    SPOUSE_UCCB_REPAYMENT,
    SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
    TAX_PAID_BY_INSTALMENTS,
    TAXABLE_INCOME,
    TOTAL_INCOME,
    WAGE_LOSS_REPLACEMENT_PLAN_INCOME,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RATES, RECORD_LISTS, REGISTERED, SIGNED
from tests.kinds import non_negative


def test_registered_identifiers_snapshot(registry: ArtifactRegistry) -> None:
    identifiers = registry.identifiers()

    assert {i for i in identifiers if i.startswith("ca/")} == REGISTERED


def test_the_package_exposes_its_catalog() -> None:
    assert isinstance(tax_engine.jurisdictions.ca.catalog.CATALOG, ArtifactCatalog)
    assert tax_engine.jurisdictions.ca.catalog.CATALOG is CATALOG
    assert {kind.identifier for kind in CATALOG.kinds} == REGISTERED


def test_catalog_kinds_are_in_the_package_namespace() -> None:
    for kind in CATALOG.kinds:
        assert kind.identifier.startswith(f"{tax_engine.jurisdictions.ca.NAMESPACE}/")


def test_the_catalog_kinds_named_by_the_package_are_money() -> None:
    assert TAXABLE_INCOME.value_type is Decimal
    assert FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76.value_type is Decimal


def test_every_registered_kind_but_the_counts_and_record_lists_is_money(
    registry: ArtifactRegistry,
) -> None:
    for identifier in REGISTERED - COUNTS - RECORD_LISTS - RATES:
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind)
        assert kind.value_type is Decimal, identifier


def test_the_counts_are_int_kinds_in_the_package_namespace(registry: ArtifactRegistry) -> None:
    assert COUNTS <= REGISTERED
    for identifier in COUNTS:
        kind = registry.get(identifier)
        assert isinstance(kind, ArtifactKind)
        assert kind.identifier.startswith(f"{tax_engine.jurisdictions.ca.NAMESPACE}/")
        assert kind.value_type is int, identifier


def test_every_kind_but_the_balance_is_declared_non_negative(registry: ArtifactRegistry) -> None:
    # No other `ca/` line can be negative on the forms as modelled.
    # A record list is not an amount: it is never declared non-negative, its fields are.
    for kind in CATALOG.kinds:
        if kind.identifier not in SIGNED | RECORD_LISTS | RATES:
            assert non_negative(kind) is True, kind.identifier
    for identifier in REGISTERED - SIGNED - RECORD_LISTS - RATES:
        assert non_negative(registry.kind(identifier)) is True, identifier


def test_the_refund_or_balance_owing_is_signed(registry: ArtifactRegistry) -> None:
    # T1 line 167 "Line 149 minus line 166 If the amount is negative, enter it on line 48400
    # below. If the amount is positive, enter it on line 48500 below. Refund or balance owing":
    # negative is a refund, so the kind is not declared non-negative.
    assert non_negative(REFUND_OR_BALANCE_OWING) is False
    assert non_negative(registry.kind("ca/refund_or_balance_owing")) is False
    assert SIGNED <= REGISTERED


def test_the_total_income_is_signed(registry: ArtifactRegistry) -> None:
    # T1 line 33 and line 15000 "Line 28 plus line 32 Total income" prints no floor, and the
    # General Guide for lines 13499 to 14300 says "If you have a loss, show it on the applicable
    # line using brackets": a loss larger than the other income is a negative total income. The
    # floor stays at line 23600 (`ca/net_income`).
    assert non_negative(TOTAL_INCOME) is False
    assert non_negative(registry.kind("ca/total_income")) is False
    assert non_negative(NET_INCOME) is True
    assert Artifact(TOTAL_INCOME, Decimal("-2000.00")).value == Decimal("-2000.00")


def test_the_net_income_before_adjustments_is_signed(registry: ArtifactRegistry) -> None:
    # T1 line 54 and line 23400 "Line 34 minus line 53 (if negative, show in brackets) Net income
    # before adjustments": the brackets are a negative figure, unlike line 56 (line 23600) "Line 54
    # minus line 55 (if negative, enter "0")", which stays the non-negative `ca/net_income`.
    assert non_negative(NET_INCOME_BEFORE_ADJUSTMENTS) is False
    assert non_negative(registry.kind("ca/net_income_before_adjustments")) is False
    assert non_negative(NET_INCOME) is True
    assert non_negative(DEDUCTIONS_FROM_TOTAL_INCOME) is True


def test_the_schedule_15_lines_that_print_no_floor_are_signed(registry: ArtifactRegistry) -> None:
    # Schedule 15 (FHSA) Steps 2 and 3: lines 3, 5, 9, 11, 23, 27, 36, 45, 48, 51, 54, 56 and 58
    # subtract (or add a line that subtracts, or take the lesser of such a line) with no "(if
    # negative, enter "0")".
    for kind in (
        FHSA_CONTRIBUTIONS_IN_2025_BEFORE_FIRST_QUALIFYING_WITHDRAWAL,
        FHSA_CONTRIBUTIONS_PLUS_VARIABLE_B_AMOUNT,
        FHSA_CONTRIBUTIONS_IN_2024_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
        FHSA_CONTRIBUTIONS_AFTER_FIRST_QUALIFYING_WITHDRAWAL,
        FHSA_NET_RRSP_TRANSFER_AMOUNT,
        FHSA_NET_RRSP_TRANSFER_AMOUNT_FOR_2024_AND_PRIOR_YEARS,
        FHSA_NET_TRANSFER_AMOUNT_AFTER_PRIOR_YEARS,
        FHSA_ANNUAL_LIMITS_LESS_DEDUCTIONS,
        FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS,
        FHSA_MAXIMUM_DEDUCTION,
        FHSA_UNUSED_CONTRIBUTIONS_PLUS_CONTRIBUTIONS,
        FHSA_CONTRIBUTIONS_AVAILABLE,
        FHSA_UNUSED_CONTRIBUTIONS_CARRIED_FORWARD,
    ):
        assert non_negative(kind) is False, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is False, kind.identifier


def test_the_schedule_15_lines_that_print_a_floor_or_add_non_negative_figures_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Lines 12, 13, 29, 39 and 50 print "(if negative, enter "0")"; lines 16, 19, 22, 32, 33, 35,
    # 40 and 43 and the deduction (line 57, at most line 51) add or take the lesser of
    # non-negative lines.
    for kind in (
        FHSA_EXCESS_DESIGNATED_WITHDRAWALS,
        FHSA_CONTRIBUTIONS_LIMIT,
        FHSA_ANNUAL_AMOUNT_WITH_CARRYFORWARD,
        FHSA_TOTAL_RRSP_TRANSFERS,
        FHSA_TOTAL_DESIGNATED_TRANSFERS,
        FHSA_NET_TRANSFER_AMOUNT_LESS_VARIABLE_H_AMOUNT,
        FHSA_ANNUAL_AMOUNT_FOR_2024_WITH_CARRYFORWARD,
        FHSA_TRANSFER_AMOUNT_AT_MOST_LIMIT,
        FHSA_TRANSFER_AMOUNT_PLUS_VARIABLE_F_AMOUNT,
        FHSA_ANNUAL_AMOUNT_AFTER_TRANSFERS,
        FHSA_ANNUAL_LIMIT_FROM_STEP_2,
        FHSA_ANNUAL_LIMIT,
        FHSA_TOTAL_ANNUAL_LIMITS,
        FHSA_LIFETIME_LIMIT_LESS_DEDUCTIONS_AND_TRANSFERS,
        FHSA_DEDUCTION,
        # Lines 2, 8 and 44 checked against lines 1, 7 and 42: each is at most a non-negative whole.
        FHSA_CONTRIBUTIONS_IN_2025_AFTER_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
        FHSA_CONTRIBUTIONS_IN_2024_BEFORE_FIRST_QUALIFYING_WITHDRAWAL_CHECKED,
        FHSA_DEDUCTIONS_FOR_2024_AND_PRIOR_YEARS_CHECKED,
    ):
        assert non_negative(kind) is True, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is True, kind.identifier


def test_the_fhsa_maximum_participation_period_count_is_a_non_negative_int() -> None:
    # Schedule 15 Step 2: "If your maximum participation period (MPP) ended in a prior year, ...
    # Enter "0" on line 40": a caller's 0 or 1 count.
    assert FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED.value_type is int
    assert non_negative(FHSA_MAXIMUM_PARTICIPATION_PERIOD_ENDED) is True


def test_the_income_tax_deducted_is_non_negative() -> None:
    # T1 line 150 (line 43700) "Total income tax deducted (amounts from all Canadian slips)".
    assert non_negative(INCOME_TAX_DEDUCTED) is True


def test_the_rrsp_amount_deducted_is_non_negative() -> None:
    # Schedule 7 line 18 "Enter your RRSP, PRPP, or SPP contributions you are deducting for 2025
    # (cannot be more than the amount on line 17).": an amount the filer states.
    assert non_negative(RRSP_AMOUNT_DEDUCTED) is True


def test_the_step_6_credit_lines_are_non_negative(registry: ArtifactRegistry) -> None:
    # T1 lines 45600, 45700, 46800, 46900, 47555 and 47600 are slip, receipt or form amounts of
    # money paid or credited to the filer, none of which prints a negative figure; line 48400
    # "Refund" is the negative of line 167 and is entered only when line 167 is negative, so it is
    # never below zero, unlike line 167 (`ca/refund_or_balance_owing`), which stays signed.
    for kind in (
        PART_XII_2_TAX_CREDIT,
        EMPLOYEE_AND_PARTNER_GST_HST_REBATE,
        EDUCATOR_SUPPLIES_EXPENSES,
        EDUCATOR_SUPPLIES_EXPENSES_AT_MOST_MAXIMUM,
        EDUCATOR_SCHOOL_SUPPLY_CREDIT,
        JOURNALISM_LABOUR_TAX_CREDIT,
        TAX_PAID_BY_INSTALMENTS,
        REFUND,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is True, kind.identifier
    assert non_negative(REFUND_OR_BALANCE_OWING) is False


def test_the_infirm_dependants_are_a_record_list_of_their_net_incomes(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 5 line 30450's chart, per dependant: line 2 "Infirm dependant's net income from
    # line 23600 of their return", the one field a record holds (the caller lists only the
    # dependants who are eligible, so there are no eligibility fields).
    assert RECORD_LISTS <= REGISTERED
    assert isinstance(INFIRM_DEPENDANTS, RecordListKind)
    assert INFIRM_DEPENDANTS.identifier == "ca/infirm_dependants"
    assert INFIRM_DEPENDANTS.value_type is RecordList
    assert INFIRM_DEPENDANTS.fields == (DEPENDANT_NET_INCOME,)
    assert registry.get("ca/infirm_dependants") is INFIRM_DEPENDANTS


def test_the_record_list_reuses_the_dependants_net_income_kind() -> None:
    # Schedule 5 line 4 and ON428 line 15 read the same kind; here it is the field of a record.
    assert INFIRM_DEPENDANTS.fields[0] is DEPENDANT_NET_INCOME
    assert DEPENDANT_NET_INCOME.identifier == "ca/dependant_net_income"
    assert non_negative(DEPENDANT_NET_INCOME) is True


def test_the_infirm_dependants_hold_a_net_income_each_in_the_callers_order() -> None:
    dependants = RecordList(
        INFIRM_DEPENDANTS.fields,
        [{DEPENDANT_NET_INCOME: Decimal("5000")}, {DEPENDANT_NET_INCOME: Decimal("25000")}],
    )

    assert [record[DEPENDANT_NET_INCOME] for record in dependants.records] == [
        Decimal("5000"),
        Decimal("25000"),
    ]


def test_the_caregiver_amount_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 82 (line 30450) "Canada caregiver amount for other infirm dependants age 18 or
    # older (complete Schedule 5)": the total of the allowable amounts, each at least "0".
    assert CAREGIVER_AMOUNT.identifier == "ca/caregiver_amount"
    assert CAREGIVER_AMOUNT.value_type is Decimal
    assert non_negative(CAREGIVER_AMOUNT) is True
    assert registry.kind("ca/caregiver_amount") is CAREGIVER_AMOUNT


def test_the_other_dependants_are_a_record_list_of_expenses_and_net_income(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet, line 33199, "Complete one column for each dependant": line 1 "Medical
    # expenses for other dependant" and, for line 2, the dependant's net income. A list of its own:
    # the infirm dependants of line 30450 are a different set of people.
    assert isinstance(OTHER_DEPENDANTS, RecordListKind)
    assert OTHER_DEPENDANTS.identifier == "ca/other_dependants"
    assert OTHER_DEPENDANTS.value_type is RecordList
    assert OTHER_DEPENDANTS.fields == (OTHER_DEPENDANT_MEDICAL_EXPENSES, DEPENDANT_NET_INCOME)
    assert OTHER_DEPENDANTS is not INFIRM_DEPENDANTS
    assert registry.get("ca/other_dependants") is OTHER_DEPENDANTS


def test_the_other_dependants_list_reuses_the_dependants_net_income_kind() -> None:
    assert OTHER_DEPENDANTS.fields[1] is DEPENDANT_NET_INCOME


def test_the_other_dependants_hold_expenses_and_net_income_each_in_the_callers_order() -> None:
    dependants = RecordList(
        OTHER_DEPENDANTS.fields,
        [
            {
                OTHER_DEPENDANT_MEDICAL_EXPENSES: Decimal("3000"),
                DEPENDANT_NET_INCOME: Decimal("10000"),
            },
            {
                OTHER_DEPENDANT_MEDICAL_EXPENSES: Decimal("1000"),
                DEPENDANT_NET_INCOME: Decimal("40000"),
            },
        ],
    )

    assert [record[OTHER_DEPENDANT_MEDICAL_EXPENSES] for record in dependants.records] == [
        Decimal("3000"),
        Decimal("1000"),
    ]


def test_the_other_dependant_medical_expenses_are_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet, line 33199, line 1 "Medical expenses for other dependant".
    assert OTHER_DEPENDANT_MEDICAL_EXPENSES.identifier == "ca/other_dependant_medical_expenses"
    assert OTHER_DEPENDANT_MEDICAL_EXPENSES.value_type is Decimal
    assert non_negative(OTHER_DEPENDANT_MEDICAL_EXPENSES) is True
    assert registry.kind("ca/other_dependant_medical_expenses") is OTHER_DEPENDANT_MEDICAL_EXPENSES


def test_the_other_dependants_medical_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 33199 "Allowable amount of medical expenses for other dependants": the total of
    # each dependant's line 3, which is "0" when negative.
    assert OTHER_DEPENDANTS_MEDICAL.identifier == "ca/other_dependants_medical"
    assert OTHER_DEPENDANTS_MEDICAL.value_type is Decimal
    assert non_negative(OTHER_DEPENDANTS_MEDICAL) is True
    assert registry.kind("ca/other_dependants_medical") is OTHER_DEPENDANTS_MEDICAL


# Form T776 Chart B, "Non-compliant amount of CCA for short-term rentals": "Column 1: Class number",
# "Column 4: Related portion of the available CCA from column 21 in Area A", "Column 5: Number of
# days the residential property was a non-compliant short-term rental" and "Column 6: Number of
# days the residential property was a short-term rental" (columns 2 and 3, the address and the
# unit number, are labels the engine does not use). Columns 5 and 6 are the days kinds of Chart A.


def test_medical_expenses_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 107 and line 33099 "Medical expenses for self, spouse or common-law partner and
    # your dependent children under 18 years of age": a starting amount.
    assert MEDICAL_EXPENSES.identifier == "ca/medical_expenses"
    assert MEDICAL_EXPENSES.value_type is Decimal
    assert non_negative(MEDICAL_EXPENSES) is True
    assert registry.kind("ca/medical_expenses") is MEDICAL_EXPENSES


def test_medical_net_income_share_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 108 "Amount from line 23600" "multiplied by 3%".
    assert MEDICAL_NET_INCOME_SHARE.identifier == "ca/medical_net_income_share"
    assert MEDICAL_NET_INCOME_SHARE.value_type is Decimal
    assert non_negative(MEDICAL_NET_INCOME_SHARE) is True
    assert registry.kind("ca/medical_net_income_share") is MEDICAL_NET_INCOME_SHARE


def test_medical_threshold_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 109 "Enter whichever is less: $2,834 or the amount from line 108."
    assert MEDICAL_THRESHOLD.identifier == "ca/medical_threshold"
    assert MEDICAL_THRESHOLD.value_type is Decimal
    assert non_negative(MEDICAL_THRESHOLD) is True
    assert registry.kind("ca/medical_threshold") is MEDICAL_THRESHOLD


def test_medical_expenses_over_threshold_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 110 "Line 107 minus line 109 (if negative, enter "0")".
    assert MEDICAL_EXPENSES_OVER_THRESHOLD.identifier == "ca/medical_expenses_over_threshold"
    assert MEDICAL_EXPENSES_OVER_THRESHOLD.value_type is Decimal
    assert non_negative(MEDICAL_EXPENSES_OVER_THRESHOLD) is True
    assert registry.kind("ca/medical_expenses_over_threshold") is MEDICAL_EXPENSES_OVER_THRESHOLD


def test_medical_claim_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # T1 line 112 and line 33200 "Line 110 plus line 111".
    assert MEDICAL_CLAIM.identifier == "ca/medical_claim"
    assert MEDICAL_CLAIM.value_type is Decimal
    assert non_negative(MEDICAL_CLAIM) is True
    assert registry.kind("ca/medical_claim") is MEDICAL_CLAIM


def test_the_disability_dependants_are_a_record_list_of_the_worksheets_figures(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 31800", per dependant: whether they were "under 18 years of age on
    # December 31, 2025", line 3 "Total of child care and attendant care expenses for your
    # dependant that you or another person claimed", line 9 "amount from line 98 of your
    # dependant's return" and line 11 "Dependant's taxable income from line 26000 of their
    # return": the four fields a record holds, in the worksheet's line order (the caller lists
    # only the dependants who qualify, so there are no eligibility fields).
    assert RECORD_LISTS <= REGISTERED
    assert isinstance(DISABILITY_DEPENDANTS, RecordListKind)
    assert DISABILITY_DEPENDANTS.identifier == "ca/disability_dependants"
    assert DISABILITY_DEPENDANTS.value_type is RecordList
    assert non_negative(DISABILITY_DEPENDANTS) is False
    assert DISABILITY_DEPENDANTS.fields == (
        DEPENDANT_UNDER_18,
        DEPENDANT_CARE_EXPENSES,
        DEPENDANT_CREDIT_AMOUNTS,
        DEPENDANT_TAXABLE_INCOME,
    )
    assert registry.get("ca/disability_dependants") is DISABILITY_DEPENDANTS


def test_the_disability_dependants_fields_are_kinds_of_their_own() -> None:
    assert DEPENDANT_UNDER_18.identifier == "ca/dependant_under_18"
    assert DEPENDANT_CARE_EXPENSES.identifier == "ca/dependant_care_expenses"
    assert DEPENDANT_CREDIT_AMOUNTS.identifier == "ca/dependant_credit_amounts"
    assert DEPENDANT_TAXABLE_INCOME.identifier == "ca/dependant_taxable_income"
    # Not the net income of line 30400's dependant: another figure of another return.
    assert DEPENDANT_NET_INCOME not in DISABILITY_DEPENDANTS.fields
    for kind in DISABILITY_DEPENDANTS.fields:
        assert non_negative(kind) is True, kind.identifier


def test_the_dependant_under_18_is_a_non_negative_int_count(registry: ArtifactRegistry) -> None:
    # "If the dependant was under 18 years of age on December 31, 2025, ...": a yes or no, taken
    # as a count of 0 or 1 like the forms' other yes or no questions.
    assert DEPENDANT_UNDER_18.value_type is int
    assert non_negative(DEPENDANT_UNDER_18) is True
    assert registry.kind("ca/dependant_under_18") is DEPENDANT_UNDER_18


@pytest.mark.parametrize(
    "kind", [DEPENDANT_CARE_EXPENSES, DEPENDANT_CREDIT_AMOUNTS, DEPENDANT_TAXABLE_INCOME]
)
def test_the_disability_dependants_amounts_are_non_negative_decimals(
    kind: ArtifactKind[Decimal], registry: ArtifactRegistry
) -> None:
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert registry.kind(kind.identifier) is kind


def disability_record(**changes: object) -> dict[ArtifactKind[Any], object]:
    """One dependant aged 20 with the ticket's chosen figures, with `changes` by field name."""
    record: dict[ArtifactKind[Any], object] = {
        DEPENDANT_UNDER_18: 0,
        DEPENDANT_CARE_EXPENSES: Decimal("0"),
        DEPENDANT_CREDIT_AMOUNTS: Decimal("16129"),
        DEPENDANT_TAXABLE_INCOME: Decimal("20000"),
    }
    names: dict[str, ArtifactKind[Any]] = {
        "under_18": DEPENDANT_UNDER_18,
        "care_expenses": DEPENDANT_CARE_EXPENSES,
        "credit_amounts": DEPENDANT_CREDIT_AMOUNTS,
        "taxable_income": DEPENDANT_TAXABLE_INCOME,
    }
    for name, value in changes.items():
        record[names[name]] = value
    return record


def test_the_disability_dependants_hold_the_four_figures_each_in_the_callers_order() -> None:
    dependants = RecordList(
        DISABILITY_DEPENDANTS.fields,
        [
            disability_record(),
            disability_record(under_18=1, care_expenses=Decimal("5000"), credit_amounts=Decimal(0)),
        ],
    )

    assert [record[DEPENDANT_UNDER_18] for record in dependants.records] == [0, 1]
    assert [record[DEPENDANT_CARE_EXPENSES] for record in dependants.records] == [
        Decimal("0"),
        Decimal("5000"),
    ]
    assert [record[DEPENDANT_CREDIT_AMOUNTS] for record in dependants.records] == [
        Decimal("16129"),
        Decimal("0"),
    ]
    assert [record[DEPENDANT_TAXABLE_INCOME] for record in dependants.records] == [
        Decimal("20000"),
        Decimal("20000"),
    ]


def test_there_may_be_no_disability_dependants() -> None:
    assert RecordList(DISABILITY_DEPENDANTS.fields, []).records == ()


@pytest.mark.parametrize(
    "missing",
    [
        DEPENDANT_UNDER_18,
        DEPENDANT_CARE_EXPENSES,
        DEPENDANT_CREDIT_AMOUNTS,
        DEPENDANT_TAXABLE_INCOME,
    ],
)
def test_a_disability_dependant_missing_a_figure_is_an_invalid_record(
    missing: ArtifactKind[Any],
) -> None:
    record = disability_record()
    del record[missing]

    with pytest.raises(InvalidRecordError, match=f"item 1: missing field {missing.identifier}"):
        RecordList(DISABILITY_DEPENDANTS.fields, [record])


def test_the_second_disability_dependant_is_named_by_its_position() -> None:
    record = disability_record()
    del record[DEPENDANT_TAXABLE_INCOME]

    with pytest.raises(
        InvalidRecordError, match="item 2: missing field ca/dependant_taxable_income"
    ):
        RecordList(DISABILITY_DEPENDANTS.fields, [disability_record(), record])


def test_a_disability_dependant_with_another_figure_is_an_invalid_record() -> None:
    record = disability_record()
    record[DEPENDANT_NET_INCOME] = Decimal("5000")

    with pytest.raises(InvalidRecordError, match="item 1: unknown field ca/dependant_net_income"):
        RecordList(DISABILITY_DEPENDANTS.fields, [record])


@pytest.mark.parametrize(
    ("change", "identifier"),
    [
        ({"under_18": -1}, "ca/dependant_under_18"),
        ({"care_expenses": Decimal("-0.01")}, "ca/dependant_care_expenses"),
        ({"credit_amounts": Decimal("-1")}, "ca/dependant_credit_amounts"),
        ({"taxable_income": Decimal("-1")}, "ca/dependant_taxable_income"),
    ],
)
def test_a_negative_disability_dependant_figure_is_refused(
    change: dict[str, object], identifier: str
) -> None:
    with pytest.raises(NegativeArtifactError, match=f"item 1: {identifier} cannot be negative"):
        RecordList(DISABILITY_DEPENDANTS.fields, [disability_record(**change)])


@pytest.mark.parametrize(
    "change",
    [
        {"under_18": Decimal("1")},
        {"under_18": True},
        {"care_expenses": 5000},
        {"credit_amounts": "16129"},
        {"taxable_income": 20000.0},
    ],
)
def test_a_disability_dependant_figure_of_the_wrong_type_is_refused(
    change: dict[str, object],
) -> None:
    with pytest.raises(TypeError):
        RecordList(DISABILITY_DEPENDANTS.fields, [disability_record(**change)])


def test_the_disability_transferred_amount_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 100 (line 31800) "Disability amount transferred from a dependant (use Federal
    # Worksheet)": the total of the worksheet's line 13 amounts, each the lesser of two amounts
    # that are at least "0".
    assert DISABILITY_TRANSFERRED_AMOUNT.identifier == "ca/disability_transferred_amount"
    assert DISABILITY_TRANSFERRED_AMOUNT.value_type is Decimal
    assert non_negative(DISABILITY_TRANSFERRED_AMOUNT) is True
    assert registry.kind("ca/disability_transferred_amount") is DISABILITY_TRANSFERRED_AMOUNT


def test_the_principal_residence_properties_are_a_record_list_of_the_forms_input_lines(
    registry: ArtifactRegistry,
) -> None:
    # Form T2091(IND), per property ("Complete a separate form for each property you sold."):
    # line 1 and line 2 the years designated "After 1981" and "After 1971 and before 1982", line 5
    # and line 6 the years owned in the same periods, line 8 "Proceeds of disposition or deemed
    # disposition", line 9 "Outlays and expenses made or incurred related to the disposition",
    # line 10 "Adjusted cost base at the time of disposition", and whether the "plus one" rule
    # applies: the fields a record holds, in the form's line order (lines 3, 4, 7 and 14 onward
    # are worked out).
    assert RECORD_LISTS <= REGISTERED
    assert isinstance(PRINCIPAL_RESIDENCE_PROPERTIES, RecordListKind)
    assert PRINCIPAL_RESIDENCE_PROPERTIES.identifier == "ca/principal_residence_properties"
    assert PRINCIPAL_RESIDENCE_PROPERTIES.value_type is RecordList
    assert non_negative(PRINCIPAL_RESIDENCE_PROPERTIES) is False
    assert PRINCIPAL_RESIDENCE_PROPERTIES.fields == (
        RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
        RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
        RESIDENCE_YEARS_OWNED_AFTER_1981,
        RESIDENCE_YEARS_OWNED_1972_TO_1981,
        RESIDENCE_PROCEEDS,
        RESIDENCE_OUTLAYS,
        RESIDENCE_ADJUSTED_COST_BASE,
        RESIDENCE_PLUS_ONE_YEAR,
        RESIDENCE_PART_2_APPLIES,
        RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
        RESIDENCE_FMV_DEC_31_1981,
        RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
        RESIDENCE_T664_FILED,
        RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
        RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
        RESIDENCE_WS_DESIGNATED_PROCEEDS,
        RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
        RESIDENCE_WS_FMV_FEB_22_1994,
        RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
        RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
        RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
        RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    )
    assert registry.get("ca/principal_residence_properties") is PRINCIPAL_RESIDENCE_PROPERTIES


def test_the_principal_residence_properties_fields_are_kinds_of_their_own() -> None:
    assert RESIDENCE_YEARS_DESIGNATED_AFTER_1981.identifier == (
        "ca/residence_years_designated_after_1981"
    )
    assert RESIDENCE_YEARS_DESIGNATED_1972_TO_1981.identifier == (
        "ca/residence_years_designated_1972_to_1981"
    )
    assert RESIDENCE_YEARS_OWNED_AFTER_1981.identifier == "ca/residence_years_owned_after_1981"
    assert RESIDENCE_YEARS_OWNED_1972_TO_1981.identifier == (
        "ca/residence_years_owned_1972_to_1981"
    )
    assert RESIDENCE_PROCEEDS.identifier == "ca/residence_proceeds"
    assert RESIDENCE_OUTLAYS.identifier == "ca/residence_outlays"
    assert RESIDENCE_ADJUSTED_COST_BASE.identifier == "ca/residence_adjusted_cost_base"
    assert RESIDENCE_PLUS_ONE_YEAR.identifier == "ca/residence_plus_one_year"
    assert RESIDENCE_PART_2_APPLIES.identifier == "ca/residence_part_2_applies"
    assert RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981.identifier == (
        "ca/residence_adjusted_cost_base_dec_31_1981"
    )
    assert RESIDENCE_FMV_DEC_31_1981.identifier == "ca/residence_fmv_dec_31_1981"
    assert RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981.identifier == (
        "ca/residence_cost_base_adjustments_after_1981"
    )
    for kind in PRINCIPAL_RESIDENCE_PROPERTIES.fields:
        assert non_negative(kind) is True, kind.identifier


@pytest.mark.parametrize(
    "kind",
    [
        RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
        RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
        RESIDENCE_YEARS_OWNED_AFTER_1981,
        RESIDENCE_YEARS_OWNED_1972_TO_1981,
        RESIDENCE_PLUS_ONE_YEAR,
        RESIDENCE_PART_2_APPLIES,
    ],
)
def test_the_residence_years_and_the_plus_one_are_non_negative_int_counts(
    kind: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # Lines 1, 2, 5 and 6 are numbers of tax years; the "plus one" and whether Part 2 applies are
    # yes or no questions, taken as a count of 0 or 1 like the forms' other yes or no questions.
    assert kind.value_type is int
    assert non_negative(kind) is True
    assert registry.kind(kind.identifier) is kind


@pytest.mark.parametrize(
    "kind",
    [
        RESIDENCE_PROCEEDS,
        RESIDENCE_OUTLAYS,
        RESIDENCE_ADJUSTED_COST_BASE,
        RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
        RESIDENCE_FMV_DEC_31_1981,
        RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    ],
)
def test_the_residence_amounts_are_non_negative_decimals(
    kind: ArtifactKind[Decimal], registry: ArtifactRegistry
) -> None:
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert registry.kind(kind.identifier) is kind


def residence_record(**changes: object) -> dict[ArtifactKind[Any], object]:
    """One property with the ticket's example figures, with `changes` by field name."""
    record: dict[ArtifactKind[Any], object] = {
        RESIDENCE_YEARS_DESIGNATED_AFTER_1981: 6,
        RESIDENCE_YEARS_DESIGNATED_1972_TO_1981: 0,
        RESIDENCE_YEARS_OWNED_AFTER_1981: 10,
        RESIDENCE_YEARS_OWNED_1972_TO_1981: 0,
        RESIDENCE_PROCEEDS: Decimal("400000"),
        RESIDENCE_OUTLAYS: Decimal("5000"),
        RESIDENCE_ADJUSTED_COST_BASE: Decimal("95000"),
        RESIDENCE_PLUS_ONE_YEAR: 1,
        RESIDENCE_PART_2_APPLIES: 0,
        RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981: Decimal("0"),
        RESIDENCE_FMV_DEC_31_1981: Decimal("0"),
        RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981: Decimal("0"),
        RESIDENCE_T664_FILED: 0,
        RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981: 0,
        RESIDENCE_WS_YEARS_OWNED_AFTER_1981: 0,
        RESIDENCE_WS_DESIGNATED_PROCEEDS: Decimal("0"),
        RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994: Decimal("0"),
        RESIDENCE_WS_FMV_FEB_22_1994: Decimal("0"),
        RESIDENCE_WS_ELECTED_CAPITAL_GAIN: Decimal("0"),
        RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992: 0,
        RESIDENCE_WS_MONTHS_OWNED_AFTER_1971: 0,
        RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994: Decimal("0"),
    }
    names: dict[str, ArtifactKind[Any]] = {
        "designated_after_1981": RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
        "designated_1972_to_1981": RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
        "owned_after_1981": RESIDENCE_YEARS_OWNED_AFTER_1981,
        "owned_1972_to_1981": RESIDENCE_YEARS_OWNED_1972_TO_1981,
        "proceeds": RESIDENCE_PROCEEDS,
        "outlays": RESIDENCE_OUTLAYS,
        "adjusted_cost_base": RESIDENCE_ADJUSTED_COST_BASE,
        "plus_one": RESIDENCE_PLUS_ONE_YEAR,
        "part_2_applies": RESIDENCE_PART_2_APPLIES,
        "cost_base_1981": RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
        "fmv_1981": RESIDENCE_FMV_DEC_31_1981,
        "adjustments_after_1981": RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
        "t664_filed": RESIDENCE_T664_FILED,
        "ws_years_designated_after_1981": RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
        "ws_years_owned_after_1981": RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
        "ws_designated_proceeds": RESIDENCE_WS_DESIGNATED_PROCEEDS,
        "ws_cost_base_feb_22_1994": RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
        "ws_fmv_feb_22_1994": RESIDENCE_WS_FMV_FEB_22_1994,
        "ws_elected_capital_gain": RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
        "ws_months_owned_after_feb_1992": RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
        "ws_months_owned_after_1971": RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
        "ws_cost_base_adjustments_to_feb_1994": RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    }
    for name, value in changes.items():
        record[names[name]] = value
    return record


def test_the_principal_residence_properties_hold_the_twelve_figures_each_in_the_callers_order() -> (
    None
):
    properties = RecordList(
        PRINCIPAL_RESIDENCE_PROPERTIES.fields,
        [
            residence_record(),
            residence_record(
                designated_after_1981=2,
                designated_1972_to_1981=3,
                owned_after_1981=6,
                owned_1972_to_1981=4,
                proceeds=Decimal("500000"),
                outlays=Decimal("0"),
                plus_one=0,
            ),
        ],
    )

    assert [record[RESIDENCE_YEARS_DESIGNATED_AFTER_1981] for record in properties.records] == [
        6,
        2,
    ]
    assert [record[RESIDENCE_YEARS_DESIGNATED_1972_TO_1981] for record in properties.records] == [
        0,
        3,
    ]
    assert [record[RESIDENCE_YEARS_OWNED_AFTER_1981] for record in properties.records] == [10, 6]
    assert [record[RESIDENCE_YEARS_OWNED_1972_TO_1981] for record in properties.records] == [0, 4]
    assert [record[RESIDENCE_PROCEEDS] for record in properties.records] == [
        Decimal("400000"),
        Decimal("500000"),
    ]
    assert [record[RESIDENCE_OUTLAYS] for record in properties.records] == [
        Decimal("5000"),
        Decimal("0"),
    ]
    assert [record[RESIDENCE_ADJUSTED_COST_BASE] for record in properties.records] == [
        Decimal("95000"),
        Decimal("95000"),
    ]
    assert [record[RESIDENCE_PLUS_ONE_YEAR] for record in properties.records] == [1, 0]
    assert [record[RESIDENCE_PART_2_APPLIES] for record in properties.records] == [0, 0]


def test_there_may_be_no_principal_residence_properties() -> None:
    assert RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, []).records == ()


@pytest.mark.parametrize("missing", PRINCIPAL_RESIDENCE_PROPERTIES.fields)
def test_a_property_missing_a_figure_is_an_invalid_record(missing: ArtifactKind[Any]) -> None:
    record = residence_record()
    del record[missing]

    with pytest.raises(InvalidRecordError, match=f"item 1: missing field {missing.identifier}"):
        RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, [record])


def test_the_second_property_is_named_by_its_position() -> None:
    record = residence_record()
    del record[RESIDENCE_PROCEEDS]

    with pytest.raises(InvalidRecordError, match="item 2: missing field ca/residence_proceeds"):
        RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, [residence_record(), record])


@pytest.mark.parametrize(
    ("change", "identifier"),
    [
        ({"designated_after_1981": -1}, "ca/residence_years_designated_after_1981"),
        ({"designated_1972_to_1981": -1}, "ca/residence_years_designated_1972_to_1981"),
        ({"owned_after_1981": -1}, "ca/residence_years_owned_after_1981"),
        ({"owned_1972_to_1981": -1}, "ca/residence_years_owned_1972_to_1981"),
        ({"proceeds": Decimal("-0.01")}, "ca/residence_proceeds"),
        ({"outlays": Decimal("-1")}, "ca/residence_outlays"),
        ({"adjusted_cost_base": Decimal("-1")}, "ca/residence_adjusted_cost_base"),
        ({"plus_one": -1}, "ca/residence_plus_one_year"),
        ({"part_2_applies": -1}, "ca/residence_part_2_applies"),
        ({"t664_filed": -1}, "ca/residence_t664_filed"),
        ({"ws_years_designated_after_1981": -1}, "ca/residence_ws_years_designated_after_1981"),
        ({"ws_years_owned_after_1981": -1}, "ca/residence_ws_years_owned_after_1981"),
        ({"ws_designated_proceeds": Decimal("-1")}, "ca/residence_ws_designated_proceeds"),
        (
            {"ws_cost_base_feb_22_1994": Decimal("-0.01")},
            "ca/residence_ws_adjusted_cost_base_feb_22_1994",
        ),
        ({"ws_fmv_feb_22_1994": Decimal("-1")}, "ca/residence_ws_fmv_feb_22_1994"),
        ({"ws_elected_capital_gain": Decimal("-1")}, "ca/residence_ws_elected_capital_gain"),
        (
            {"ws_months_owned_after_feb_1992": -1},
            "ca/residence_ws_months_owned_after_feb_1992",
        ),
        ({"ws_months_owned_after_1971": -1}, "ca/residence_ws_months_owned_after_1971"),
        (
            {"ws_cost_base_adjustments_to_feb_1994": Decimal("-1")},
            "ca/residence_ws_cost_base_adjustments_to_feb_1994",
        ),
        ({"cost_base_1981": Decimal("-1")}, "ca/residence_adjusted_cost_base_dec_31_1981"),
        ({"fmv_1981": Decimal("-0.01")}, "ca/residence_fmv_dec_31_1981"),
        (
            {"adjustments_after_1981": Decimal("-1")},
            "ca/residence_cost_base_adjustments_after_1981",
        ),
    ],
)
def test_a_negative_property_figure_is_refused(change: dict[str, object], identifier: str) -> None:
    with pytest.raises(NegativeArtifactError, match=f"item 1: {identifier} cannot be negative"):
        RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, [residence_record(**change)])


@pytest.mark.parametrize(
    "change",
    [
        {"designated_after_1981": Decimal("6")},
        {"owned_after_1981": True},
        {"owned_1972_to_1981": 1.0},
        {"plus_one": Decimal("1")},
        {"proceeds": 400000},
        {"outlays": "5000"},
        {"adjusted_cost_base": 95000.0},
        {"part_2_applies": True},
        {"part_2_applies": Decimal("1")},
        {"fmv_1981": 90000},
        {"cost_base_1981": "40000.00"},
        {"adjustments_after_1981": 10000.0},
    ],
)
def test_a_property_figure_of_the_wrong_type_is_refused(change: dict[str, object]) -> None:
    with pytest.raises(TypeError):
        RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, [residence_record(**change)])


def test_the_principal_residence_gain_is_a_non_negative_decimal(registry: ArtifactRegistry) -> None:
    # Form T2091(IND) Part 3 line 54 "Total capital gain": line 24 "Line 18 minus line 23 (if
    # negative, enter "0")" for each property, totalled here.
    assert PRINCIPAL_RESIDENCE_GAIN.identifier == "ca/principal_residence_gain"
    assert PRINCIPAL_RESIDENCE_GAIN.value_type is Decimal
    assert non_negative(PRINCIPAL_RESIDENCE_GAIN) is True
    assert registry.kind("ca/principal_residence_gain") is PRINCIPAL_RESIDENCE_GAIN


# --- the capital cost allowance table, one record per class -------------------------------------
#
# T776 Area A, "Calculation of capital cost allowance (CCA) claim", one row per class, and T2125
# Area A with the same columns: the fields each class's record holds, shared by the rental and the
# business lists (each list is declared when its form is wired). Columns 4, 6, 8 and 9 (DIEPs) are
# left out, so column 10 is column 3 and column 13 is column 7.


@pytest.mark.parametrize(
    ("kind", "identifier"),
    [
        # "Column 1: Class number": a number such as 10.1 or 43.1, so a Decimal.
        (CCA_CLASS_NUMBER, "ca/cca_class_number"),
        # "Column 2: Undepreciated capital cost (UCC) at the start of the year".
        (CCA_UCC_AT_START, "ca/cca_ucc_at_start"),
        # "Column 3: Cost of additions in the year".
        (CCA_ADDITIONS, "ca/cca_additions"),
        # "Column 5: Proceeds of dispositions in the year".
        (CCA_PROCEEDS, "ca/cca_proceeds"),
        # "Column 11: Cost of remaining additions from column 10 that are AIIPs or ZEVs acquired
        # before 2025".
        (CCA_AIIP_ADDITIONS, "ca/cca_aiip_additions"),
        # "Column 12: Cost of remaining additions from column 10 that are RIIPs or ZEVs acquired
        # after 2024".
        (CCA_RIIP_ADDITIONS, "ca/cca_riip_additions"),
        # "Column 4: Cost of additions from column 3 that are DIEPs (property must be available
        # for use before 2025)".
        (CCA_DIEP_ADDITIONS, "ca/cca_diep_additions"),
        # "Column 6: Proceeds of dispositions of DIEP (enter amount from column 5 that relates to
        # DIEP from column 4)".
        (CCA_DIEP_PROCEEDS, "ca/cca_diep_proceeds"),
        # "Column 9: Immediate expensing amount for DIEPs (Note 5)": the caller's amount for the
        # class, a field of each record.
        (CCA_IMMEDIATE_EXPENSING, "ca/cca_immediate_expensing"),
        # T776 "Column 23: CCA claim for the year" (T2125 column 21): the amount claimed, an
        # election from 0 to the class's maximum.
        (CCA_CLAIMED, "ca/cca_claimed"),
        # T776 Area A Note 9: "you must subtract any remaining personal part of this property's cost
        # from the UCC at the end of the year": the caller's amount for the class, a field of each
        # record of the rental list.
        (CCA_PERSONAL_PART_REMAINING, "ca/cca_personal_part_remaining"),
        # T776 "Column 24: UCC at the end of the year (column 7 minus column 23)" (T2125 column
        # 22): a field of the closing list for next year.
        (CCA_UCC_AT_END, "ca/cca_ucc_at_end"),
    ],
)
def test_the_cca_table_fields_are_non_negative_decimals(
    registry: ArtifactRegistry, kind: ArtifactKind[Any], identifier: str
) -> None:
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert registry.kind(identifier) is kind


def test_no_property_left_in_the_class_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    # Note 3: "If no property is left in the class and there is a positive amount in this column,
    # deduct the amount from your income as a terminal loss": a caller's 1 if no property is left
    # in the class at the end of the year, else 0, as the other 0 or 1 counts of the forms.
    assert CCA_NO_PROPERTY_LEFT.identifier == "ca/cca_no_property_left"
    assert CCA_NO_PROPERTY_LEFT.value_type is int
    assert non_negative(CCA_NO_PROPERTY_LEFT) is True
    assert registry.kind("ca/cca_no_property_left") is CCA_NO_PROPERTY_LEFT


def test_the_half_year_rule_differs_is_a_non_negative_int_flag(registry: ArtifactRegistry) -> None:
    # Guide T4002 2025, "Column 18": "some properties are not subject to the half-year rule ...
    # most of those in Class 12, such as small tools"; "the half-year rule applies to the particular
    # property transferred". A row's additions are treated the opposite way from their class (1), or
    # as the class has them (0, or no field): 1 if so, else 0, as the other yes or no questions.
    assert CCA_HALF_YEAR_RULE_DIFFERS.identifier == "ca/cca_half_year_rule_differs"
    assert CCA_HALF_YEAR_RULE_DIFFERS.value_type is int
    assert non_negative(CCA_HALF_YEAR_RULE_DIFFERS) is True
    assert registry.kind("ca/cca_half_year_rule_differs") is CCA_HALF_YEAR_RULE_DIFFERS


def test_the_rate_election_is_a_non_negative_int_code(registry: ArtifactRegistry) -> None:
    # Guide T4036 2025, "Class 1 (4%)": "new buildings or parts of a building that are built for
    # use as a purpose-built residential rental ... may now be eligible for an accelerated CCA rate
    # of 10%"; "To be eligible for one of the additional allowances, you must elect to put a
    # building in a separate class. ... If you do not file an election to put it in a separate
    # class, the 4% rate will apply." A row's election is a whole-number code: 0 none (the class's
    # own rate), 1 purpose-built residential rental, 2 separate class at 6%, 3 separate class at
    # 10% (manufacturing or processing); the rates come from the class-rates dataset.
    assert CCA_RATE_ELECTION.identifier == "ca/cca_rate_election"
    assert CCA_RATE_ELECTION.value_type is int
    assert non_negative(CCA_RATE_ELECTION) is True
    assert registry.kind("ca/cca_rate_election") is CCA_RATE_ELECTION


def test_the_vehicle_acquired_year_is_a_non_negative_int_year(registry: ArtifactRegistry) -> None:
    # T2125 Area A endnote 2: "a passenger vehicle bought after April 18, 2021, that has been
    # included in Class 10.1" is adjusted; "If the passenger vehicle in Class 10.1 is not
    # designated for immediate expensing treatment, this special rule does not apply." A row's
    # year is the year the vehicle was acquired, or 0 when the rule does not apply to the row.
    assert CCA_VEHICLE_ACQUIRED_YEAR.identifier == "ca/cca_vehicle_acquired_year"
    assert CCA_VEHICLE_ACQUIRED_YEAR.value_type is int
    assert non_negative(CCA_VEHICLE_ACQUIRED_YEAR) is True
    assert registry.kind("ca/cca_vehicle_acquired_year") is CCA_VEHICLE_ACQUIRED_YEAR


def test_the_vehicle_cost_is_a_non_negative_amount(registry: ArtifactRegistry) -> None:
    # Guide T4002 "Class 10.1 (30%)": the prescribed amounts are "plus the GST/HST or PST"; the
    # actual cost of the vehicle is entered with the tax.
    assert CCA_VEHICLE_COST.identifier == "ca/cca_vehicle_cost"
    assert CCA_VEHICLE_COST.value_type is Decimal
    assert non_negative(CCA_VEHICLE_COST) is True
    assert registry.kind("ca/cca_vehicle_cost") is CCA_VEHICLE_COST


def test_the_t777_part_b_vehicle_answers_are_non_negative_ints(registry: ArtifactRegistry) -> None:
    # Guide T4044 2025, Part B column 3: bought from a non-arm's-length person, and a change in
    # use: yes or no answers, taken as 0 or 1 like the forms' other yes or no questions.
    for kind, identifier in (
        (CCA_VEHICLE_FROM_NON_ARMS_LENGTH, "ca/cca_vehicle_from_non_arms_length"),
        (CCA_VEHICLE_CHANGE_IN_USE, "ca/cca_vehicle_change_in_use"),
    ):
        assert kind.identifier == identifier
        assert kind.value_type is int
        assert non_negative(kind) is True
        assert registry.kind(identifier) is kind


def test_the_t777_part_b_vehicle_figures_are_non_negative_amounts(
    registry: ArtifactRegistry,
) -> None:
    # Guide T4044 2025, Part B column 3: the fair market value when acquired, the seller's cost
    # and the fair market value at a change in use.
    for kind, identifier in (
        (
            CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE,
            "ca/cca_vehicle_non_arms_length_fair_market_value",
        ),
        (CCA_VEHICLE_SELLER_COST, "ca/cca_vehicle_seller_cost"),
        (
            CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE,
            "ca/cca_vehicle_change_in_use_fair_market_value",
        ),
    ):
        assert kind.identifier == identifier
        assert kind.value_type is Decimal
        assert non_negative(kind) is True
        assert registry.kind(identifier) is kind


def test_the_t777_part_a_change_in_use_answer_is_a_non_negative_int(
    registry: ArtifactRegistry,
) -> None:
    # Guide T4044 2025, Part A column 3: a row that changed use is answered yes or no, taken as 0 or
    # 1 like the forms' other yes or no questions.
    assert CCA_CHANGE_IN_USE.identifier == "ca/cca_change_in_use"
    assert CCA_CHANGE_IN_USE.value_type is int
    assert non_negative(CCA_CHANGE_IN_USE) is True
    assert registry.kind("ca/cca_change_in_use") is CCA_CHANGE_IN_USE


def test_the_t777_part_a_change_in_use_fair_market_value_is_a_non_negative_amount(
    registry: ArtifactRegistry,
) -> None:
    # Guide T4044 2025, Part A column 3: the fair market value of the property at the time it starts
    # being used for employment.
    assert CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE.identifier == (
        "ca/cca_change_in_use_fair_market_value"
    )
    assert CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE.value_type is Decimal
    assert non_negative(CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE) is True
    assert registry.kind("ca/cca_change_in_use_fair_market_value") is (
        CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE
    )


def test_the_vehicle_government_assistance_is_a_signed_amount(registry: ArtifactRegistry) -> None:
    # T2125 Area A endnote 2: "you will have to adjust the actual cost of the vehicle for any
    # payments or repayments of government assistance that you may have received or repaid for
    # the vehicle": assistance received less assistance repaid, so it can be negative.
    assert CCA_VEHICLE_GOVERNMENT_ASSISTANCE.identifier == "ca/cca_vehicle_government_assistance"
    assert CCA_VEHICLE_GOVERNMENT_ASSISTANCE.value_type is Decimal
    assert non_negative(CCA_VEHICLE_GOVERNMENT_ASSISTANCE) is False
    assert (
        registry.kind("ca/cca_vehicle_government_assistance") is CCA_VEHICLE_GOVERNMENT_ASSISTANCE
    )
    record = RecordList(
        (CCA_CLASS_NUMBER, CCA_VEHICLE_GOVERNMENT_ASSISTANCE),
        [{CCA_CLASS_NUMBER: Decimal("10.1"), CCA_VEHICLE_GOVERNMENT_ASSISTANCE: Decimal("-500")}],
    )
    assert record.records[0][CCA_VEHICLE_GOVERNMENT_ASSISTANCE] == Decimal("-500")


def test_a_negative_vehicle_cost_is_refused() -> None:
    with pytest.raises(NegativeArtifactError, match="item 1: ca/cca_vehicle_cost cannot be neg"):
        RecordList(
            (CCA_CLASS_NUMBER, CCA_VEHICLE_COST),
            [{CCA_CLASS_NUMBER: Decimal("10.1"), CCA_VEHICLE_COST: Decimal("-1")}],
        )


def test_a_sold_zepvs_proceeds_are_a_non_negative_amount(registry: ArtifactRegistry) -> None:
    # Guide T4036 2025, "Class 54 (30%)": "If a zero-emission passenger vehicle is disposed of to a
    # person or partnership with whom you deal at arm's length, and its cost exceeds the prescribed
    # amount [...], the proceeds of disposition will be adjusted": the proceeds of one vehicle sold
    # in the year, as entered.
    assert CCA_ZEPV_PROCEEDS.identifier == "ca/cca_zepv_proceeds"
    assert CCA_ZEPV_PROCEEDS.value_type is Decimal
    assert non_negative(CCA_ZEPV_PROCEEDS) is True
    assert registry.kind("ca/cca_zepv_proceeds") is CCA_ZEPV_PROCEEDS


def test_a_sold_zepvs_diep_proceeds_are_a_non_negative_amount(registry: ArtifactRegistry) -> None:
    # Area A column 6 "Proceeds of dispositions of DIEP (enter amount from col. 5 that relates to
    # DIEP from col. 4)": the part of one vehicle's proceeds that relates to a DIEP.
    assert CCA_ZEPV_DIEP_PROCEEDS.identifier == "ca/cca_zepv_diep_proceeds"
    assert CCA_ZEPV_DIEP_PROCEEDS.value_type is Decimal
    assert non_negative(CCA_ZEPV_DIEP_PROCEEDS) is True
    assert registry.kind("ca/cca_zepv_diep_proceeds") is CCA_ZEPV_DIEP_PROCEEDS


@pytest.mark.parametrize(
    "kind", [CCA_ZEPV_PROCEEDS, CCA_ZEPV_DIEP_PROCEEDS], ids=lambda k: k.identifier
)
def test_a_negative_zepv_proceeds_amount_is_refused(kind: ArtifactKind[Any]) -> None:
    with pytest.raises(NegativeArtifactError, match=f"item 1: {kind.identifier} cannot be neg"):
        RecordList((kind,), [{kind: Decimal("-1")}])


def test_the_sold_zepvs_are_a_record_list_of_the_vehicle_and_its_proceeds(
    registry: ArtifactRegistry,
) -> None:
    # Guide T4036 2025, "Class 54 (30%)": "Class 54 may include both zero-emission passenger
    # vehicles that do and do not exceed the prescribed threshold. However, unlike Class 10.1,
    # Class 54 does not establish a separate class for each vehicle whose cost exceeds the
    # threshold.": a Class 54 row holds one record for each vehicle sold, with the year it was
    # acquired (0 when the rule does not apply to it), its cost, the government assistance for it,
    # its proceeds and the DIEP part of them.
    assert isinstance(CCA_SOLD_ZEPVS, RecordListKind)
    assert CCA_SOLD_ZEPVS.identifier == "ca/cca_sold_zepvs"
    assert CCA_SOLD_ZEPVS.value_type is RecordList
    assert non_negative(CCA_SOLD_ZEPVS) is False
    assert CCA_SOLD_ZEPVS.fields == (
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_ZEPV_PROCEEDS,
        CCA_ZEPV_DIEP_PROCEEDS,
    )
    assert registry.get("ca/cca_sold_zepvs") is CCA_SOLD_ZEPVS
    assert "ca/cca_sold_zepvs" in RECORD_LISTS


def test_a_sold_zepv_record_must_give_each_of_its_fields() -> None:
    whole: dict[ArtifactKind[Any], Decimal | int] = {
        CCA_VEHICLE_ACQUIRED_YEAR: 2024,
        CCA_VEHICLE_COST: Decimal("65000"),
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE: Decimal("-100"),
        CCA_ZEPV_PROCEEDS: Decimal("30000"),
        CCA_ZEPV_DIEP_PROCEEDS: Decimal("0"),
    }

    (kept,) = RecordList(CCA_SOLD_ZEPVS.fields, [whole]).records

    assert kept[CCA_ZEPV_PROCEEDS] == Decimal("30000")
    for field in CCA_SOLD_ZEPVS.fields:
        short = {key: value for key, value in whole.items() if key is not field}
        with pytest.raises(InvalidRecordError, match=f"item 1: missing field {field.identifier}"):
            RecordList(CCA_SOLD_ZEPVS.fields, [short])


def test_the_cca_table_fields_are_kinds_of_their_own() -> None:
    kinds = (
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_PROCEEDS,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_DIEP_ADDITIONS,
        CCA_DIEP_PROCEEDS,
        CCA_IMMEDIATE_EXPENSING,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
        CCA_PERSONAL_PART_REMAINING,
        CCA_HALF_YEAR_RULE_DIFFERS,
        CCA_RATE_ELECTION,
        CCA_VEHICLE_ACQUIRED_YEAR,
        CCA_VEHICLE_COST,
        CCA_VEHICLE_GOVERNMENT_ASSISTANCE,
        CCA_ZEPV_PROCEEDS,
        CCA_ZEPV_DIEP_PROCEEDS,
        CCA_UCC_AT_END,
    )

    assert len({kind.identifier for kind in kinds}) == 20
    assert {kind.identifier for kind in kinds} <= REGISTERED
    assert not {kind.identifier for kind in kinds} & RECORD_LISTS


def test_the_cca_table_fields_hold_one_class_per_record() -> None:
    fields = (
        CCA_CLASS_NUMBER,
        CCA_UCC_AT_START,
        CCA_ADDITIONS,
        CCA_PROCEEDS,
        CCA_AIIP_ADDITIONS,
        CCA_RIIP_ADDITIONS,
        CCA_CLAIMED,
        CCA_NO_PROPERTY_LEFT,
    )
    classes = RecordList(
        fields,
        [
            {
                CCA_CLASS_NUMBER: Decimal("10.1"),
                CCA_UCC_AT_START: Decimal("20000"),
                CCA_ADDITIONS: Decimal("0"),
                CCA_PROCEEDS: Decimal("0"),
                CCA_AIIP_ADDITIONS: Decimal("0"),
                CCA_RIIP_ADDITIONS: Decimal("0"),
                CCA_CLAIMED: Decimal("6000"),
                CCA_NO_PROPERTY_LEFT: 0,
            }
        ],
    )

    (record,) = classes.records
    assert record[CCA_CLASS_NUMBER] == Decimal("10.1")
    assert record[CCA_NO_PROPERTY_LEFT] == 0


def test_a_negative_cca_claim_is_refused() -> None:
    # T4036: "You can claim any amount you like, from zero to the maximum allowed for the year."
    with pytest.raises(NegativeArtifactError, match="item 1: ca/cca_claimed cannot be negative"):
        RecordList(
            (CCA_CLASS_NUMBER, CCA_CLAIMED),
            [{CCA_CLASS_NUMBER: Decimal("8"), CCA_CLAIMED: Decimal("-1")}],
        )


def test_the_special_tax_and_credit_lines_are_non_negative(registry: ArtifactRegistry) -> None:
    # T1 lines 131, 41300, 41400, 41500 and 41800 and the forms behind them (T2038(IND) Part C,
    # T1172 Parts A and B, the RC210 box 10 and the RL-10 slip) print amounts of tax, credit or
    # expenditure with no negative figure; the lines that carry or subtract them print a floor
    # or cannot be negative: line 132 adds line 131 to line 126, line 139 is "if negative, enter
    # "0"" and T1172's line 3 is the lesser of two such amounts, line 8 is line 1 less a line 7
    # that is at most line 1.
    for kind in (
        ITC_RECAPTURE_EXPENDITURE_AT_15_PERCENT,
        ITC_RECAPTURE_EXPENDITURE_AT_20_PERCENT,
        LABOUR_SPONSORED_FUNDS_NET_COST,
        ADVANCED_CANADA_WORKERS_BENEFIT,
        RESP_AIPS_RECEIVED_PART_A,
        RESP_AIPS_RRSP_CONTRIBUTIONS,
        RESP_AIPS_REDUCTION_USED_IN_PREVIOUS_YEARS,
        RESP_AIPS_RECEIVED_PART_B,
        RL_10_LABOUR_SPONSORED_FUND_AMOUNT,
        POLITICAL_CONTRIBUTIONS,
        ITC_RECAPTURE_AT_15_PERCENT,
        ITC_RECAPTURE_AT_20_PERCENT,
        ITC_RECAPTURE,
        POLITICAL_CREDIT_COLUMN_1_LINE_2,
        POLITICAL_CREDIT_COLUMN_1_LINE_3,
        POLITICAL_CREDIT_COLUMN_1_LINE_5,
        POLITICAL_CREDIT_COLUMN_1_LINE_6,
        POLITICAL_CREDIT_COLUMN_1_LINE_7,
        POLITICAL_CREDIT_COLUMN_2_LINE_2,
        POLITICAL_CREDIT_COLUMN_2_LINE_3,
        POLITICAL_CREDIT_COLUMN_2_LINE_5,
        POLITICAL_CREDIT_COLUMN_2_LINE_6,
        POLITICAL_CREDIT_COLUMN_2_LINE_7,
        POLITICAL_CREDIT_COLUMN_3_LINE_2,
        POLITICAL_CREDIT_COLUMN_3_LINE_3,
        POLITICAL_CREDIT_COLUMN_3_LINE_5,
        POLITICAL_CREDIT_COLUMN_3_LINE_6,
        POLITICAL_CREDIT_COLUMN_3_LINE_7,
        POLITICAL_CREDIT_CHOSEN_COLUMN,
        POLITICAL_CREDIT_SHORTCUT_THRESHOLD,
        POLITICAL_CREDIT_SHORTCUT_AMOUNT,
        POLITICAL_CREDIT_BEFORE_MAXIMUM,
        POLITICAL_CREDIT,
        LABOUR_SPONSORED_FUNDS_CREDIT_BEFORE_MAXIMUM,
        LABOUR_SPONSORED_FUNDS_CREDIT,
        CREDITS_AGAINST_FEDERAL_TAX,
        FEDERAL_TAX_LESS_CREDITS,
        RESP_AIPS_CONTRIBUTIONS_COUNTED,
        RESP_AIPS_LIFETIME_LIMIT,
        RESP_AIPS_SUBJECT_TO_TAX,
        RESP_AIPS_PART_A_TAX,
        RESP_AIPS_PART_B_TAX,
        RESP_AIPS_ADDITIONAL_TAX,
        SPECIAL_TAXES,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is True, kind.identifier


def test_the_t1172_lines_that_print_no_floor_are_signed(registry: ArtifactRegistry) -> None:
    # Form T1172 Part A: line 6 "Line 4 minus line 5" and line 7 "Amount from line 3 or 6, whichever
    # is less" print no "(if negative, enter "0")", so line 5 above 50,000.00 would make them
    # negative, as the form prints; line 8 "line 1 minus line 7" is never negative as line 7 is at
    # most line 3, which is at most line 1.
    assert non_negative(RESP_AIPS_LIMIT_REMAINING) is False
    assert non_negative(RESP_AIPS_REDUCTION) is False
    assert non_negative(registry.kind("ca/resp_aips_limit_remaining")) is False
    assert non_negative(registry.kind("ca/resp_aips_reduction")) is False
    assert non_negative(RESP_AIPS_CONTRIBUTIONS_COUNTED) is True
    assert non_negative(RESP_AIPS_SUBJECT_TO_TAX) is True


def test_the_t1172_part_a_count_is_a_non_negative_int() -> None:
    # Form T1172 "Part B - Fill out this part only if Part A does not apply to you": a caller's 0
    # (Part B) or 1 (Part A) count, as the other 0 or 1 counts of the forms.
    assert RESP_AIPS_PART_A_APPLIES.value_type is int
    assert non_negative(RESP_AIPS_PART_A_APPLIES) is True


def test_the_medical_supplement_counts_are_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 45200 - Refundable medical expense supplement": "You were resident
    # in Canada throughout 2025" and "You were 18 years of age or older at the end of 2025", each
    # a caller's 0 or 1 count as the other 0 or 1 counts of the forms.
    for kind in (RESIDENT_IN_CANADA_THROUGHOUT_2025, AGED_18_OR_OLDER_AT_END_OF_2025):
        assert kind.value_type is int, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.kind(kind.identifier) is kind
        assert kind.identifier in COUNTS


def test_the_medical_supplement_lines_that_print_no_floor_are_signed(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 45200 - Refundable medical expense supplement": column line 3 "Line 1
    # plus line 2" prints no "(if negative, enter "0")" and line 1 may be negative ("the amount you
    # would have entered if the instructions on line 23600 said "if negative, show in brackets""),
    # so the spouse's line 1 and each column's line 3 are signed; so is the employment income less
    # the wage-loss replacement plan amounts, which the worksheet floors only after the deductions
    # ("if the result is negative, consider it as "0"").
    for kind in (
        SPOUSE_NET_INCOME_BEFORE_ADJUSTMENTS,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME_LESS_WAGE_LOSS,
        MEDICAL_SUPPLEMENT_COLUMN_1_LINE_3,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_3,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is False, kind.identifier
        assert registry.kind(kind.identifier) is kind
        assert kind.identifier in SIGNED


def test_the_other_medical_supplement_lines_are_non_negative_decimals(
    registry: ArtifactRegistry,
) -> None:
    # The lines that print "(if negative, enter "0")", add non-negative figures, take a lesser or
    # are caller amounts the forms never print as negative.
    signed = {
        "ca/spouse_net_income_before_adjustments",
        "ca/medical_supplement_employment_income_less_wage_loss",
        "ca/cwb_net_income_total_line_10",
        "ca/medical_supplement_column_1_line_3",
        "ca/medical_supplement_column_2_line_3",
    }
    kinds = (
        OTHER_EMPLOYMENT_EXPENSES,
        NET_BUSINESS_INCOME,
        NET_PROFESSIONAL_INCOME,
        NET_COMMISSION_INCOME,
        NET_FARMING_INCOME,
        NET_FISHING_INCOME,
        WAGE_LOSS_REPLACEMENT_PLAN_INCOME,
        SPOUSE_UCCB_REPAYMENT,
        SPOUSE_RDSP_INCOME_REPAYMENT,
        SPOUSE_UNIVERSAL_CHILD_CARE_BENEFIT,
        SPOUSE_RDSP_INCOME,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_INCOME,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_DEDUCTIONS,
        MEDICAL_SUPPLEMENT_EMPLOYMENT_WORKING_INCOME,
        MEDICAL_SUPPLEMENT_SELF_EMPLOYMENT_INCOME,
        MEDICAL_SUPPLEMENT_WORKING_INCOME,
        MEDICAL_SUPPLEMENT_COLUMN_1_LINE_5,
        MEDICAL_SUPPLEMENT_COLUMN_2_LINE_2,
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
    )
    for kind in kinds:
        assert kind.identifier not in signed, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is True, kind.identifier


def _cca_record(
    fields: tuple[ArtifactKind[Any], ...],
) -> dict[ArtifactKind[Any], Decimal | int | RecordList]:
    """A record of 0 for each of `fields`, and no records for a record-list field."""
    return {
        field: (
            RecordList(field.fields, ())
            if isinstance(field, RecordListKind)
            else 0
            if field.value_type is int
            else Decimal(0)
        )
        for field in fields
    }


# --- Form T2125, Statement of Business or Professional Activities (T1 lines 13499 and 13500) ---


def test_the_four_credit_limit_kinds_are_gone() -> None:
    # The figures $350, $44,706, $1,100 and $38,000 are rows of the `year_amounts` datasets
    # `ca/business_vehicle_interest_limits` and `ca/business_vehicle_lease_limits`, not kinds.
    for name in ("interest_limit", "list_price_limit", "lease_charge_limit", "lease_cost_limit"):
        assert f"ca/business_vehicle_{name}" not in REGISTERED, name
        assert f"BUSINESS_VEHICLE_{name.upper()}" not in vars(
            tax_engine.jurisdictions.ca.catalog
        ), name


# --- Form T2042, Statement of Farming Activities (T1 lines 14099 and 14100) ---------------------


# --- Form T2121, Statement of Fishing Activities (T1 lines 14299 and 14300) ----------------------


# --- Form T2222, Northern Residents Deductions (T1 line 66 and line 25500) ---------------------


def test_the_lines_after_a_floor_are_non_negative(registry: ArtifactRegistry) -> None:
    # Schedule 8 Part 4 line 3 "Line 1 plus line 2 (if negative, enter "0")", line 6 and line 7
    # "(if negative, enter "0")", line 9 "(if negative, enter "0")"; Schedule 13 line 1 "(if
    # negative, enter "0")" and line 7 "(if negative, enter "0")".
    for kind in (
        CPP_PAYABLE_ON_SELF_EMPLOYMENT,
        EI_PAYABLE_ON_SELF_EMPLOYMENT,
    ):
        assert non_negative(kind) is True, kind.identifier
        assert non_negative(registry.kind(kind.identifier)) is True, kind.identifier


# --- the partner answer of Form T2125 (the count of the partner answer, checked).
