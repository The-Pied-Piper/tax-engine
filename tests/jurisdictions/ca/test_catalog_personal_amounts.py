"""Registered and money kinds of the federal catalog family `personal_amounts`."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    AGE_AMOUNT,
    AGE_AMOUNT_BEFORE_COUNT,
    AGE_INCOME_OVER_THRESHOLD,
    AGE_INCOME_THRESHOLD,
    AGE_MAXIMUM,
    AGE_REDUCTION,
    BASIC_PERSONAL_AMOUNT,
    BORN_IN_1960_OR_EARLIER,
    BORN_IN_1960_OR_EARLIER_CHECKED,
    CAREGIVER_AMOUNT,
    CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
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
    DEPENDANT_CARE_EXPENSES,
    DEPENDANT_CAREGIVER_AGED_18_OR_OLDER,
    DEPENDANT_CAREGIVER_AGED_18_OR_OLDER_CHECKED,
    DEPENDANT_CAREGIVER_AMOUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT,
    DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT,
    DEPENDANT_CAREGIVER_BEFORE_MAXIMUM,
    DEPENDANT_CAREGIVER_ELIGIBLE,
    DEPENDANT_CAREGIVER_ELIGIBLE_CHECKED,
    DEPENDANT_CAREGIVER_LIMIT,
    DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT,
    DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED,
    DEPENDANT_CREDIT_AMOUNTS,
    DEPENDANT_INFIRMITY_SUPPLEMENT,
    DEPENDANT_NET_INCOME,
    DEPENDANT_TAXABLE_INCOME,
    DEPENDANT_UNDER_18,
    DISABILITY_AMOUNT_FOR_SELF,
    DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE,
    DISABILITY_DEPENDANTS,
    DISABILITY_SELF_BASE_AMOUNT,
    DISABILITY_SELF_CARE_EXPENSES,
    DISABILITY_SELF_CARE_OVER_THRESHOLD,
    DISABILITY_SELF_CARE_THRESHOLD,
    DISABILITY_SELF_SUPPLEMENT,
    DISABILITY_SELF_SUPPLEMENT_MAXIMUM,
    DISABILITY_SELF_WORKSHEET_AMOUNT,
    DISABILITY_TRANSFERRED_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT,
    ELIGIBLE_DEPENDANT_AMOUNT_BASIS,
    ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT,
    ELIGIBLE_DEPENDANTS,
    ELIGIBLE_DEPENDANTS_CHECKED,
    ELIGIBLE_FOR_DISABILITY_AMOUNT,
    ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED,
    FEDERAL_BASIC_TAX,
    INFIRM_CHILDREN,
    INFIRM_CHILDREN_AMOUNT,
    INFIRM_DEPENDANTS,
    MEDICAL_CLAIM,
    MEDICAL_EXPENSES,
    MEDICAL_EXPENSES_OVER_THRESHOLD,
    MEDICAL_NET_INCOME_SHARE,
    MEDICAL_THRESHOLD,
    OTHER_DEPENDANT_MEDICAL_EXPENSES,
    OTHER_DEPENDANTS,
    OTHER_DEPENDANTS_MEDICAL,
    PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
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
    SPOUSE_AMOUNT,
    SPOUSE_AMOUNT_BASIS,
    SPOUSE_AMOUNT_BEFORE_COUNT,
    SPOUSE_AND_DEPENDANT_BOTH,
    SPOUSE_AND_DEPENDANT_BOTH_CHECKED,
    SPOUSE_CAREGIVER_AMOUNT,
    SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT,
    SPOUSE_CAREGIVER_BASE,
    SPOUSE_CAREGIVER_BEFORE_MAXIMUM,
    SPOUSE_CAREGIVER_ELIGIBLE,
    SPOUSE_CAREGIVER_ELIGIBLE_CHECKED,
    SPOUSE_CAREGIVER_LIMIT,
    SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT,
    SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED,
    SPOUSE_INFIRMITY_SUPPLEMENT,
    SPOUSE_NET_INCOME,
    SPOUSES_CLAIMED,
    SPOUSES_CLAIMED_CHECKED,
    UNDER_18_AND_AGED_18_OR_OLDER,
    UNDER_18_AND_AGED_18_OR_OLDER_CHECKED,
    UNDER_18_AND_BORN_IN_1960_OR_EARLIER,
    UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED,
    UNDER_18_ON_DECEMBER_31,
    UNDER_18_ON_DECEMBER_31_CHECKED,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, REGISTERED, SIGNED


def test_the_personal_amounts_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/federal_basic_tax") is FEDERAL_BASIC_TAX
    assert registry.get("ca/basic_personal_amount") is BASIC_PERSONAL_AMOUNT
    assert registry.get("ca/born_in_1960_or_earlier") is BORN_IN_1960_OR_EARLIER
    assert registry.get("ca/age_maximum") is AGE_MAXIMUM
    assert registry.get("ca/age_income_threshold") is AGE_INCOME_THRESHOLD
    assert registry.get("ca/age_income_over_threshold") is AGE_INCOME_OVER_THRESHOLD
    assert registry.get("ca/age_reduction") is AGE_REDUCTION
    assert registry.get("ca/age_amount_before_count") is AGE_AMOUNT_BEFORE_COUNT
    assert registry.get("ca/age_amount") is AGE_AMOUNT
    assert registry.get("ca/spouses_claimed") is SPOUSES_CLAIMED
    assert registry.get("ca/spouse_caregiver_eligible") is SPOUSE_CAREGIVER_ELIGIBLE
    assert registry.get("ca/spouse_net_income") is SPOUSE_NET_INCOME
    assert registry.get("ca/spouse_infirmity_supplement") is SPOUSE_INFIRMITY_SUPPLEMENT
    assert registry.get("ca/spouse_amount_basis") is SPOUSE_AMOUNT_BASIS
    assert registry.get("ca/spouse_amount_before_count") is SPOUSE_AMOUNT_BEFORE_COUNT
    assert registry.get("ca/spouse_amount") is SPOUSE_AMOUNT
    assert registry.get("ca/eligible_dependants") is ELIGIBLE_DEPENDANTS
    assert registry.get("ca/dependant_net_income") is DEPENDANT_NET_INCOME
    assert (
        registry.get("ca/eligible_dependant_amount_before_count")
        is ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT
    )
    assert registry.get("ca/eligible_dependant_amount") is ELIGIBLE_DEPENDANT_AMOUNT
    assert registry.get("ca/spouse_caregiver_base") is SPOUSE_CAREGIVER_BASE
    assert registry.get("ca/spouse_caregiver_before_maximum") is SPOUSE_CAREGIVER_BEFORE_MAXIMUM
    assert registry.get("ca/spouse_caregiver_limit") is SPOUSE_CAREGIVER_LIMIT
    assert (
        registry.get("ca/spouse_caregiver_amount_before_count")
        is SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT
    )
    assert registry.get("ca/spouse_caregiver_amount") is SPOUSE_CAREGIVER_AMOUNT
    assert registry.get("ca/dependant_caregiver_eligible") is DEPENDANT_CAREGIVER_ELIGIBLE
    assert (
        registry.get("ca/dependant_caregiver_aged_18_or_older")
        is DEPENDANT_CAREGIVER_AGED_18_OR_OLDER
    )
    assert registry.get("ca/dependant_infirmity_supplement") is DEPENDANT_INFIRMITY_SUPPLEMENT
    assert registry.get("ca/eligible_dependant_amount_basis") is ELIGIBLE_DEPENDANT_AMOUNT_BASIS
    assert (
        registry.get("ca/dependant_caregiver_before_maximum") is DEPENDANT_CAREGIVER_BEFORE_MAXIMUM
    )
    assert registry.get("ca/dependant_caregiver_limit") is DEPENDANT_CAREGIVER_LIMIT
    assert (
        registry.get("ca/dependant_caregiver_amount_before_count")
        is DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT
    )
    assert (
        registry.get("ca/dependant_caregiver_amount_before_age_count")
        is DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT
    )
    assert registry.get("ca/dependant_caregiver_amount") is DEPENDANT_CAREGIVER_AMOUNT
    assert (
        registry.get("ca/caregiver_amount_for_spouse_or_dependant")
        is CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT
    )
    assert registry.get("ca/infirm_dependants") is INFIRM_DEPENDANTS
    assert registry.get("ca/caregiver_amount") is CAREGIVER_AMOUNT
    assert registry.get("ca/other_dependant_medical_expenses") is OTHER_DEPENDANT_MEDICAL_EXPENSES
    assert registry.get("ca/other_dependants") is OTHER_DEPENDANTS
    assert registry.get("ca/other_dependants_medical") is OTHER_DEPENDANTS_MEDICAL
    assert registry.get("ca/medical_expenses") is MEDICAL_EXPENSES
    assert registry.get("ca/medical_net_income_share") is MEDICAL_NET_INCOME_SHARE
    assert registry.get("ca/medical_threshold") is MEDICAL_THRESHOLD
    assert registry.get("ca/medical_expenses_over_threshold") is MEDICAL_EXPENSES_OVER_THRESHOLD
    assert registry.get("ca/medical_claim") is MEDICAL_CLAIM
    assert registry.get("ca/dependant_under_18") is DEPENDANT_UNDER_18
    assert registry.get("ca/dependant_care_expenses") is DEPENDANT_CARE_EXPENSES
    assert registry.get("ca/dependant_credit_amounts") is DEPENDANT_CREDIT_AMOUNTS
    assert registry.get("ca/dependant_taxable_income") is DEPENDANT_TAXABLE_INCOME
    assert registry.get("ca/disability_dependants") is DISABILITY_DEPENDANTS
    assert registry.get("ca/disability_transferred_amount") is DISABILITY_TRANSFERRED_AMOUNT
    assert (
        registry.get("ca/residence_years_designated_after_1981")
        is RESIDENCE_YEARS_DESIGNATED_AFTER_1981
    )
    assert (
        registry.get("ca/residence_years_designated_1972_to_1981")
        is RESIDENCE_YEARS_DESIGNATED_1972_TO_1981
    )
    assert registry.get("ca/residence_years_owned_after_1981") is RESIDENCE_YEARS_OWNED_AFTER_1981
    assert (
        registry.get("ca/residence_years_owned_1972_to_1981") is RESIDENCE_YEARS_OWNED_1972_TO_1981
    )
    assert registry.get("ca/residence_proceeds") is RESIDENCE_PROCEEDS
    assert registry.get("ca/residence_outlays") is RESIDENCE_OUTLAYS
    assert registry.get("ca/residence_adjusted_cost_base") is RESIDENCE_ADJUSTED_COST_BASE
    assert registry.get("ca/residence_plus_one_year") is RESIDENCE_PLUS_ONE_YEAR
    assert registry.get("ca/principal_residence_properties") is PRINCIPAL_RESIDENCE_PROPERTIES
    assert registry.get("ca/principal_residence_gain") is PRINCIPAL_RESIDENCE_GAIN
    assert registry.get("ca/residence_part_2_applies") is RESIDENCE_PART_2_APPLIES
    assert (
        registry.get("ca/residence_adjusted_cost_base_dec_31_1981")
        is RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981
    )
    assert registry.get("ca/residence_fmv_dec_31_1981") is RESIDENCE_FMV_DEC_31_1981
    assert (
        registry.get("ca/residence_cost_base_adjustments_after_1981")
        is RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981
    )
    assert registry.get("ca/cca_class_number") is CCA_CLASS_NUMBER
    assert registry.get("ca/cca_ucc_at_start") is CCA_UCC_AT_START
    assert registry.get("ca/cca_additions") is CCA_ADDITIONS
    assert registry.get("ca/cca_proceeds") is CCA_PROCEEDS
    assert registry.get("ca/cca_aiip_additions") is CCA_AIIP_ADDITIONS
    assert registry.get("ca/cca_riip_additions") is CCA_RIIP_ADDITIONS
    assert registry.get("ca/cca_diep_additions") is CCA_DIEP_ADDITIONS
    assert registry.get("ca/cca_diep_proceeds") is CCA_DIEP_PROCEEDS
    assert registry.get("ca/cca_immediate_expensing") is CCA_IMMEDIATE_EXPENSING
    assert registry.get("ca/cca_claimed") is CCA_CLAIMED
    assert registry.get("ca/cca_no_property_left") is CCA_NO_PROPERTY_LEFT
    assert registry.get("ca/cca_personal_part_remaining") is CCA_PERSONAL_PART_REMAINING
    assert registry.get("ca/cca_half_year_rule_differs") is CCA_HALF_YEAR_RULE_DIFFERS
    assert registry.get("ca/cca_rate_election") is CCA_RATE_ELECTION
    assert registry.get("ca/cca_vehicle_acquired_year") is CCA_VEHICLE_ACQUIRED_YEAR
    assert registry.get("ca/cca_vehicle_cost") is CCA_VEHICLE_COST
    assert registry.get("ca/cca_vehicle_from_non_arms_length") is CCA_VEHICLE_FROM_NON_ARMS_LENGTH
    assert (
        registry.get("ca/cca_vehicle_non_arms_length_fair_market_value")
        is CCA_VEHICLE_NON_ARMS_LENGTH_FAIR_MARKET_VALUE
    )
    assert registry.get("ca/cca_vehicle_seller_cost") is CCA_VEHICLE_SELLER_COST
    assert registry.get("ca/cca_vehicle_change_in_use") is CCA_VEHICLE_CHANGE_IN_USE
    assert (
        registry.get("ca/cca_vehicle_change_in_use_fair_market_value")
        is CCA_VEHICLE_CHANGE_IN_USE_FAIR_MARKET_VALUE
    )
    assert registry.get("ca/cca_change_in_use") is CCA_CHANGE_IN_USE
    assert (
        registry.get("ca/cca_change_in_use_fair_market_value")
        is CCA_CHANGE_IN_USE_FAIR_MARKET_VALUE
    )
    assert registry.get("ca/cca_vehicle_government_assistance") is CCA_VEHICLE_GOVERNMENT_ASSISTANCE
    assert registry.get("ca/cca_zepv_proceeds") is CCA_ZEPV_PROCEEDS
    assert registry.get("ca/cca_zepv_diep_proceeds") is CCA_ZEPV_DIEP_PROCEEDS
    assert registry.get("ca/cca_ucc_at_end") is CCA_UCC_AT_END
    assert registry.get("ca/infirm_children") is INFIRM_CHILDREN
    assert registry.get("ca/infirm_children_amount") is INFIRM_CHILDREN_AMOUNT
    assert registry.get("ca/disability_amount_for_self") is DISABILITY_AMOUNT_FOR_SELF
    assert registry.get("ca/eligible_for_disability_amount") is ELIGIBLE_FOR_DISABILITY_AMOUNT
    assert registry.get("ca/under_18_on_december_31") is UNDER_18_ON_DECEMBER_31
    assert registry.get("ca/disability_self_care_expenses") is DISABILITY_SELF_CARE_EXPENSES
    assert registry.get("ca/disability_self_base_amount") is DISABILITY_SELF_BASE_AMOUNT
    assert (
        registry.get("ca/disability_self_supplement_maximum") is DISABILITY_SELF_SUPPLEMENT_MAXIMUM
    )
    assert registry.get("ca/disability_self_care_threshold") is DISABILITY_SELF_CARE_THRESHOLD
    assert (
        registry.get("ca/disability_self_care_over_threshold")
        is DISABILITY_SELF_CARE_OVER_THRESHOLD
    )
    assert registry.get("ca/disability_self_supplement") is DISABILITY_SELF_SUPPLEMENT
    assert registry.get("ca/disability_self_worksheet_amount") is DISABILITY_SELF_WORKSHEET_AMOUNT
    assert (
        registry.get("ca/disability_amount_for_self_if_eligible")
        is DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE
    )


def test_the_personal_amounts_kinds_are_money() -> None:
    for kind in (
        BASIC_PERSONAL_AMOUNT,
        AGE_MAXIMUM,
        AGE_INCOME_THRESHOLD,
        AGE_INCOME_OVER_THRESHOLD,
        AGE_REDUCTION,
        AGE_AMOUNT_BEFORE_COUNT,
        AGE_AMOUNT,
        SPOUSE_NET_INCOME,
        SPOUSE_INFIRMITY_SUPPLEMENT,
        SPOUSE_AMOUNT_BASIS,
        SPOUSE_AMOUNT_BEFORE_COUNT,
        SPOUSE_AMOUNT,
        DEPENDANT_NET_INCOME,
        ELIGIBLE_DEPENDANT_AMOUNT_BEFORE_COUNT,
        ELIGIBLE_DEPENDANT_AMOUNT,
        SPOUSE_CAREGIVER_BASE,
        SPOUSE_CAREGIVER_BEFORE_MAXIMUM,
        SPOUSE_CAREGIVER_LIMIT,
        SPOUSE_CAREGIVER_AMOUNT_BEFORE_COUNT,
        SPOUSE_CAREGIVER_AMOUNT,
        DEPENDANT_INFIRMITY_SUPPLEMENT,
        ELIGIBLE_DEPENDANT_AMOUNT_BASIS,
        DEPENDANT_CAREGIVER_BEFORE_MAXIMUM,
        DEPENDANT_CAREGIVER_LIMIT,
        DEPENDANT_CAREGIVER_AMOUNT_BEFORE_COUNT,
        DEPENDANT_CAREGIVER_AMOUNT_BEFORE_AGE_COUNT,
        DEPENDANT_CAREGIVER_AMOUNT,
        CAREGIVER_AMOUNT_FOR_SPOUSE_OR_DEPENDANT,
        CAREGIVER_AMOUNT,
        OTHER_DEPENDANT_MEDICAL_EXPENSES,
        OTHER_DEPENDANTS_MEDICAL,
        MEDICAL_EXPENSES,
        MEDICAL_NET_INCOME_SHARE,
        MEDICAL_THRESHOLD,
        MEDICAL_EXPENSES_OVER_THRESHOLD,
        MEDICAL_CLAIM,
        DEPENDANT_CARE_EXPENSES,
        DEPENDANT_CREDIT_AMOUNTS,
        DEPENDANT_TAXABLE_INCOME,
        DISABILITY_TRANSFERRED_AMOUNT,
        RESIDENCE_PROCEEDS,
        RESIDENCE_OUTLAYS,
        RESIDENCE_ADJUSTED_COST_BASE,
        PRINCIPAL_RESIDENCE_GAIN,
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
        CCA_PERSONAL_PART_REMAINING,
        CCA_UCC_AT_END,
        INFIRM_CHILDREN_AMOUNT,
        DISABILITY_AMOUNT_FOR_SELF,
        DISABILITY_SELF_CARE_EXPENSES,
        DISABILITY_SELF_BASE_AMOUNT,
        DISABILITY_SELF_SUPPLEMENT_MAXIMUM,
        DISABILITY_SELF_CARE_THRESHOLD,
        DISABILITY_SELF_CARE_OVER_THRESHOLD,
        DISABILITY_SELF_SUPPLEMENT,
        DISABILITY_SELF_WORKSHEET_AMOUNT,
        DISABILITY_AMOUNT_FOR_SELF_IF_ELIGIBLE,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_disability_amount_for_self_callers_are_counts_and_the_care_expenses_are_money() -> (
    None
):
    for count in (ELIGIBLE_FOR_DISABILITY_AMOUNT, UNDER_18_ON_DECEMBER_31):
        assert count.value_type is int, count.identifier
        assert count.non_negative is True, count.identifier
    assert DISABILITY_SELF_CARE_EXPENSES.value_type is Decimal
    assert DISABILITY_SELF_CARE_EXPENSES.non_negative is True


# --- Form T2091(IND) Part 2: the lines of the pre-1982 and post-1981 gains (lines 27 to 53) -------
#
# One output kind per computed line, each the total over the properties of that line. A line that
# can be negative (a figure of its own, not floored) is signed; the others are never negative.

PART_2_LINE_KINDS: list[tuple[int, ArtifactKind[Decimal]]] = [
    (27, PRINCIPAL_RESIDENCE_LINE_27),
    (29, PRINCIPAL_RESIDENCE_LINE_29),
    (30, PRINCIPAL_RESIDENCE_LINE_30),
    (32, PRINCIPAL_RESIDENCE_LINE_32),
    (33, PRINCIPAL_RESIDENCE_LINE_33),
    (38, PRINCIPAL_RESIDENCE_LINE_38),
    (39, PRINCIPAL_RESIDENCE_LINE_39),
    (42, PRINCIPAL_RESIDENCE_LINE_42),
    (44, PRINCIPAL_RESIDENCE_LINE_44),
    (45, PRINCIPAL_RESIDENCE_LINE_45),
    (48, PRINCIPAL_RESIDENCE_LINE_48),
    (51, PRINCIPAL_RESIDENCE_LINE_51),
    (53, PRINCIPAL_RESIDENCE_LINE_53),
]

SIGNED_PART_2_LINES = {27, 30, 32, 39, 42, 44}


def test_the_part_2_line_kinds_are_registered_under_their_line(registry: ArtifactRegistry) -> None:
    for line, kind in PART_2_LINE_KINDS:
        assert kind.identifier == f"ca/principal_residence_line_{line}", line
        assert kind.value_type is Decimal, line
        assert registry.get(f"ca/principal_residence_line_{line}") is kind, line


def test_the_part_2_lines_that_can_be_negative_are_signed_kinds() -> None:
    # Line 27 "Line 25 minus line 26" and line 39 "Line 34 minus line 38" print no "(if negative,
    # enter "0")"; lines 30, 32, 42 and 44 multiply or divide them, so they can be negative too.
    for line, kind in PART_2_LINE_KINDS:
        if line in SIGNED_PART_2_LINES:
            assert kind.non_negative is False, line
        else:
            assert kind.non_negative is True, line


def test_the_part_2_lines_are_in_the_snapshot_with_their_signs() -> None:
    for line, kind in PART_2_LINE_KINDS:
        assert kind.identifier in REGISTERED, line
        assert (kind.identifier in SIGNED) is (line in SIGNED_PART_2_LINES), line


def test_the_part_2_applies_flag_is_a_count_in_the_snapshot() -> None:
    assert RESIDENCE_PART_2_APPLIES.identifier in COUNTS
    assert RESIDENCE_PART_2_APPLIES.identifier in REGISTERED
    for kind in (
        RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
        RESIDENCE_FMV_DEC_31_1981,
        RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    ):
        assert kind.identifier in REGISTERED
        assert kind.identifier not in COUNTS
        assert kind.identifier not in SIGNED


# --- Form T2091(IND)-WS and Part 4: the worksheet's inputs, its lines, and lines 56 and 57 -------
#
# The election's inputs are a starting figure each, fields of each record of the properties sold:
# a count of years or months, or an amount. The worksheet's lines are one output kind each, the
# total over the properties; a line the form does not floor can be negative.

WORKSHEET_COUNTS = (
    RESIDENCE_T664_FILED,
    RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
)

WORKSHEET_MONEY_INPUTS = (
    RESIDENCE_WS_DESIGNATED_PROCEEDS,
    RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
    RESIDENCE_WS_FMV_FEB_22_1994,
    RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
    RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
)

WORKSHEET_LINE_KINDS: list[tuple[int, ArtifactKind[Decimal]]] = [
    (3, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_3),
    (6, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_6),
    (16, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_16),
    (17, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_17),
    (18, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_18),
    (19, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_19),
    (21, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_21),
    (23, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_23),
    (24, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_24),
    (26, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_26),
    (27, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_27),
    (59, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_59),
    (61, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_61),
    (63, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_63),
    (64, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_64),
    (66, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_66),
]

# Line 18 "Line 14 minus line 17" and the lines after it print no floor; lines 16, 17, 3, 6 and 23
# are never negative (a multiplication of amounts, a floor, or a count of years).
SIGNED_WORKSHEET_LINES = {18, 19, 21, 24, 26, 27, 59, 61, 63, 64, 66}


def test_the_worksheet_counts_are_non_negative_int_counts_in_the_snapshot(
    registry: ArtifactRegistry,
) -> None:
    for kind in WORKSHEET_COUNTS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert registry.get(kind.identifier) is kind
        assert kind.identifier in COUNTS
        assert kind.identifier in REGISTERED


def test_the_worksheet_money_inputs_are_non_negative_decimals_in_the_snapshot(
    registry: ArtifactRegistry,
) -> None:
    for kind in WORKSHEET_MONEY_INPUTS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert registry.get(kind.identifier) is kind
        assert kind.identifier in REGISTERED
        assert kind.identifier not in COUNTS
        assert kind.identifier not in SIGNED


def test_the_worksheet_record_fields_are_appended_to_the_properties_record() -> None:
    # Worksheet line 12 is appended last, after the figures the worksheet already read.
    assert PRINCIPAL_RESIDENCE_PROPERTIES.fields[-10:] == (
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


def test_the_worksheet_line_kinds_are_registered_under_their_line(
    registry: ArtifactRegistry,
) -> None:
    for line, kind in WORKSHEET_LINE_KINDS:
        assert kind.identifier == f"ca/principal_residence_worksheet_line_{line}", line
        assert kind.value_type is Decimal, line
        assert registry.get(f"ca/principal_residence_worksheet_line_{line}") is kind, line


def test_the_worksheet_lines_that_can_be_negative_are_signed_kinds() -> None:
    for line, kind in WORKSHEET_LINE_KINDS:
        assert kind.non_negative is (line not in SIGNED_WORKSHEET_LINES), line


def test_the_worksheet_lines_are_in_the_snapshot_with_their_signs() -> None:
    for line, kind in WORKSHEET_LINE_KINDS:
        assert kind.identifier in REGISTERED, line
        assert (kind.identifier in SIGNED) is (line in SIGNED_WORKSHEET_LINES), line


def test_the_part_4_lines_are_registered_with_their_signs(registry: ArtifactRegistry) -> None:
    # Line 56 "Reduction ... (line 66 of Form T2091(IND)-WS)" prints no floor; line 57 is floored.
    assert PRINCIPAL_RESIDENCE_LINE_56.identifier == "ca/principal_residence_line_56"
    assert PRINCIPAL_RESIDENCE_LINE_56.value_type is Decimal
    assert PRINCIPAL_RESIDENCE_LINE_56.non_negative is False
    assert PRINCIPAL_RESIDENCE_LINE_56.identifier in SIGNED
    assert registry.get("ca/principal_residence_line_56") is PRINCIPAL_RESIDENCE_LINE_56

    assert PRINCIPAL_RESIDENCE_LINE_57.identifier == "ca/principal_residence_line_57"
    assert PRINCIPAL_RESIDENCE_LINE_57.value_type is Decimal
    assert PRINCIPAL_RESIDENCE_LINE_57.non_negative is True
    assert PRINCIPAL_RESIDENCE_LINE_57.identifier not in SIGNED
    assert registry.get("ca/principal_residence_line_57") is PRINCIPAL_RESIDENCE_LINE_57


# --- Form T2091(IND)-WS Part 2: the lines 30 to 58 that are calculated, and their signs --------
#
# Each calculated line of Part 2 is one kind, the total over the properties sold of that line. A
# line the form does not floor can be negative: the differences and the products of a signed
# figure, and the quotients and the lesser amount of them. A sum of non-negative figures, a floored
# difference (area A and area B's line 47, area C's line 50 and area D's line 55) and a count are
# not negative.

PART_2_WORKSHEET_LINE_KINDS: list[tuple[int, ArtifactKind[Decimal]]] = [
    (30, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_30),
    (32, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_32),
    (33, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_33),
    (35, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_35),
    (36, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_36),
    (40, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_40),
    (41, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_41),
    (44, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_44),
    (46, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_46),
    (47, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_47),
    (50, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_50),
    (53, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_53),
    (55, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_55),
    (58, PRINCIPAL_RESIDENCE_WORKSHEET_LINE_58),
]

# Line 30 "Line 28 minus line 29", line 33 and line 35 (from it), line 41 "Line 37 minus line 40",
# lines 44 and 46 (from it) and line 58 "lesser of line 56 or line 57", which may be negative.
PART_2_SIGNED_LINES = {30, 33, 35, 41, 44, 46, 58}


def test_the_worksheet_part_2_line_kinds_are_registered_under_their_line(
    registry: ArtifactRegistry,
) -> None:
    for line, kind in PART_2_WORKSHEET_LINE_KINDS:
        assert kind.identifier == f"ca/principal_residence_worksheet_line_{line}", line
        assert kind.value_type is Decimal, line
        assert registry.get(f"ca/principal_residence_worksheet_line_{line}") is kind, line


def test_the_worksheet_part_2_line_kinds_are_signed_as_the_form_has_them() -> None:
    for line, kind in PART_2_WORKSHEET_LINE_KINDS:
        assert kind.non_negative is (line not in PART_2_SIGNED_LINES), line


def test_the_worksheet_part_2_line_kinds_are_in_the_snapshot_with_their_signs() -> None:
    for line, kind in PART_2_WORKSHEET_LINE_KINDS:
        assert kind.identifier in REGISTERED, line
        assert (kind.identifier in SIGNED) is (line in PART_2_SIGNED_LINES), line
        assert kind.identifier not in COUNTS, line


def test_the_worksheet_cost_base_adjustments_input_is_a_non_negative_money_field(
    registry: ArtifactRegistry,
) -> None:
    kind = RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994

    assert kind.identifier == "ca/residence_ws_cost_base_adjustments_to_feb_1994"
    assert kind.value_type is Decimal
    assert kind.non_negative is True
    assert registry.get(kind.identifier) is kind
    assert kind.identifier in REGISTERED
    assert kind.identifier not in SIGNED
    assert kind.identifier not in COUNTS


def test_the_eligible_dependants_checked_is_a_non_negative_count(
    registry: ArtifactRegistry,
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the eligible dependant amount is
    # multiplied by it (T1 line 30400); the raw count stays beside it.
    assert registry.get("ca/eligible_dependants_checked") is ELIGIBLE_DEPENDANTS_CHECKED
    assert registry.get("ca/eligible_dependants") is ELIGIBLE_DEPENDANTS
    assert ELIGIBLE_DEPENDANTS_CHECKED.value_type is int
    assert ELIGIBLE_DEPENDANTS_CHECKED.non_negative is True


def test_the_spouse_and_dependant_both_counts_are_registered_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # T1 lines 30300 and 30400 claimed together (Schedule 5): the count of the spouse amount and the
    # eligible dependant amount both above 0, and its checked count, which refuses a 1 (an input
    # error, not capped).
    for identifier, kind in (
        ("ca/spouse_and_dependant_both", SPOUSE_AND_DEPENDANT_BOTH),
        ("ca/spouse_and_dependant_both_checked", SPOUSE_AND_DEPENDANT_BOTH_CHECKED),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
        assert identifier in COUNTS
    assert SPOUSE_AND_DEPENDANT_BOTH_CHECKED is not SPOUSE_AND_DEPENDANT_BOTH


def test_the_caregiver_without_its_base_counts_are_registered_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 30425 (Schedule 5): the Canada caregiver amount claimed on line 51090 or line 51100
    # without the spouse or eligible dependant amount it builds on (line 30300 or line 30400), a
    # count of 1, and its checked count, which refuses a 1 (an input error, not capped).
    for identifier, kind in (
        ("ca/spouse_caregiver_without_spouse_amount", SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT),
        (
            "ca/spouse_caregiver_without_spouse_amount_checked",
            SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED,
        ),
        (
            "ca/dependant_caregiver_without_dependant_amount",
            DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT,
        ),
        (
            "ca/dependant_caregiver_without_dependant_amount_checked",
            DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED,
        ),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
        assert identifier in COUNTS
    assert (
        SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT_CHECKED is not SPOUSE_CAREGIVER_WITHOUT_SPOUSE_AMOUNT
    )
    assert (
        DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT_CHECKED
        is not DEPENDANT_CAREGIVER_WITHOUT_DEPENDANT_AMOUNT
    )


def test_the_under_18_with_another_age_counts_are_registered_non_negative_int_counts(
    registry: ArtifactRegistry,
) -> None:
    # Worksheet ON428 line 58440 (under 18 on December 31) entered with Form ON428 line 10 (born in
    # 1960 or earlier) or with 18 or older at the end of 2025, a count of 1, and its checked count,
    # which refuses a 1 (an input error, not capped).
    for identifier, kind in (
        ("ca/under_18_and_born_in_1960_or_earlier", UNDER_18_AND_BORN_IN_1960_OR_EARLIER),
        (
            "ca/under_18_and_born_in_1960_or_earlier_checked",
            UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED,
        ),
        ("ca/under_18_and_aged_18_or_older", UNDER_18_AND_AGED_18_OR_OLDER),
        ("ca/under_18_and_aged_18_or_older_checked", UNDER_18_AND_AGED_18_OR_OLDER_CHECKED),
    ):
        assert registry.get(identifier) is kind
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier
        assert identifier in COUNTS
    assert UNDER_18_AND_BORN_IN_1960_OR_EARLIER_CHECKED is not UNDER_18_AND_BORN_IN_1960_OR_EARLIER
    assert UNDER_18_AND_AGED_18_OR_OLDER_CHECKED is not UNDER_18_AND_AGED_18_OR_OLDER


def test_the_principal_residence_designation_box_is_a_non_negative_int_count(
    registry: ArtifactRegistry,
) -> None:
    kind = PRINCIPAL_RESIDENCE_DESIGNATION_BOX

    assert kind.identifier == "ca/principal_residence_designation_box"
    assert kind.value_type is int
    assert kind.non_negative is True
    assert registry.get(kind.identifier) is kind
    assert kind.identifier in REGISTERED
    assert kind.identifier in COUNTS
    assert kind.identifier not in SIGNED


YES_OR_NO_CHECKED = (
    (BORN_IN_1960_OR_EARLIER, BORN_IN_1960_OR_EARLIER_CHECKED),
    (SPOUSES_CLAIMED, SPOUSES_CLAIMED_CHECKED),
    (SPOUSE_CAREGIVER_ELIGIBLE, SPOUSE_CAREGIVER_ELIGIBLE_CHECKED),
    (DEPENDANT_CAREGIVER_ELIGIBLE, DEPENDANT_CAREGIVER_ELIGIBLE_CHECKED),
    (DEPENDANT_CAREGIVER_AGED_18_OR_OLDER, DEPENDANT_CAREGIVER_AGED_18_OR_OLDER_CHECKED),
    (ELIGIBLE_FOR_DISABILITY_AMOUNT, ELIGIBLE_FOR_DISABILITY_AMOUNT_CHECKED),
    (UNDER_18_ON_DECEMBER_31, UNDER_18_ON_DECEMBER_31_CHECKED),
)


@pytest.mark.parametrize(("raw", "checked"), YES_OR_NO_CHECKED, ids=lambda kind: kind.identifier)
def test_each_yes_or_no_checked_kind_is_a_non_negative_count_named_after_its_input(
    raw: ArtifactKind[int], checked: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the steps that read it; a count of 2 or
    # more is refused, not capped.
    assert checked.identifier == f"{raw.identifier}_checked"
    assert registry.get(checked.identifier) is checked
    assert checked.value_type is int
    assert checked.non_negative is True
