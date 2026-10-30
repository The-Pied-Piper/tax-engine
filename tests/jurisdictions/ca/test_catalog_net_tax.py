"""Registered and money kinds of the federal catalog family `net_tax`."""

from __future__ import annotations

from decimal import Decimal

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    BUSINESS_INCOME_NOT_BELOW_ZERO,
    COMMISSION_INCOME_NOT_BELOW_ZERO,
    CPP_PAYABLE_ON_SELF_EMPLOYMENT,
    EI_PAYABLE_ON_SELF_EMPLOYMENT,
    FARMING_INCOME_NOT_BELOW_ZERO,
    FISHING_INCOME_NOT_BELOW_ZERO,
    INCOME_BEFORE_LOSSES,
    INCOME_TAX_DEDUCTED,
    INCOME_TAX_DEDUCTED_AFTER_ELECTION,
    NET_FEDERAL_TAX,
    NET_RENTAL_INCOME_NOT_BELOW_ZERO,
    PROFESSIONAL_INCOME_NOT_BELOW_ZERO,
    RC359_EMPLOYERS,
    RC359_EMPLOYMENT_INCOME,
    RC359_EPSP_CONTRIBUTIONS,
    RC359_EXCESS_EPSP_AMOUNT,
    RC359_LINE_4,
    RC359_LINE_6,
    RC359_LINE_8,
    RC359_OTHER_EMPLOYMENT_INCOME,
    RC359_PROVINCE,
    RC359_TAX_ON_EXCESS_EPSP,
    RC359_TAX_TOTAL,
    SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
    SPECIAL_TAXES,
    SPLIT_INCOME_LINE_10,
    SPLIT_INCOME_LINE_13,
    SPLIT_INCOME_LINE_14,
    SPLIT_INCOME_LINE_15,
    SPLIT_INCOME_LINE_18,
    SPLIT_INCOME_LINE_19,
    SPLIT_INCOME_LINE_20,
    SPLIT_INCOME_LINE_21,
    SPLIT_INCOME_LINE_22,
    SPLIT_INCOME_LINE_23,
    SPLIT_INCOME_LINE_24,
    SPLIT_INCOME_LINE_29,
    SPLIT_INCOME_LINE_30,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, SIGNED

# --- Form RC359, Tax on Excess Employees Profit Sharing Plan Amounts (one copy per employer) -----

RC359_KINDS = (
    RC359_EPSP_CONTRIBUTIONS,
    RC359_EMPLOYMENT_INCOME,
    RC359_OTHER_EMPLOYMENT_INCOME,
    RC359_LINE_4,
    RC359_LINE_6,
    RC359_EXCESS_EPSP_AMOUNT,
    RC359_LINE_8,
    RC359_TAX_ON_EXCESS_EPSP,
    RC359_TAX_TOTAL,
)


def test_the_rc359_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/rc359_employers") is RC359_EMPLOYERS
    assert registry.get("ca/rc359_epsp_contributions") is RC359_EPSP_CONTRIBUTIONS
    assert registry.get("ca/rc359_employment_income") is RC359_EMPLOYMENT_INCOME
    assert registry.get("ca/rc359_other_employment_income") is RC359_OTHER_EMPLOYMENT_INCOME
    assert registry.get("ca/rc359_province") is RC359_PROVINCE
    assert registry.get("ca/rc359_line_4") is RC359_LINE_4
    assert registry.get("ca/rc359_line_6") is RC359_LINE_6
    assert registry.get("ca/rc359_excess_epsp_amount") is RC359_EXCESS_EPSP_AMOUNT
    assert registry.get("ca/rc359_line_8") is RC359_LINE_8
    assert registry.get("ca/rc359_tax_on_excess_epsp") is RC359_TAX_ON_EXCESS_EPSP
    assert registry.get("ca/rc359_tax_total") is RC359_TAX_TOTAL


def test_the_rc359_employers_is_a_record_list_of_the_four_form_fields_in_line_order() -> None:
    # Form RC359 lines 1, 2, 3 and 8: the T4PS box 41 contributions, the T4 employment income, the
    # security options and other employment income, and the province of residence code.
    assert isinstance(RC359_EMPLOYERS, RecordListKind)
    assert RC359_EMPLOYERS.fields == (
        RC359_EPSP_CONTRIBUTIONS,
        RC359_EMPLOYMENT_INCOME,
        RC359_OTHER_EMPLOYMENT_INCOME,
        RC359_PROVINCE,
    )


def test_the_rc359_amounts_are_decimals_and_the_province_is_an_int_code() -> None:
    for kind in RC359_KINDS:
        assert kind.value_type is Decimal, kind.identifier
    assert RC359_PROVINCE.value_type is int
    assert "ca/rc359_province" in COUNTS


def test_the_rc359_inputs_are_non_negative() -> None:
    # Lines 1, 2 and 3 are amounts the caller enters from the slips, and the province is a code
    # of 1 to 14 (0 and the codes the chart does not list are refused by the rate table).
    for kind in (
        RC359_EPSP_CONTRIBUTIONS,
        RC359_EMPLOYMENT_INCOME,
        RC359_OTHER_EMPLOYMENT_INCOME,
        RC359_PROVINCE,
    ):
        assert kind.non_negative is True, kind.identifier


def test_rc359_lines_4_and_6_are_signed_because_the_form_prints_no_floor(
    registry: ArtifactRegistry,
) -> None:
    # Line 4 "Line 2 minus line 3" and line 6 "Line 4 multiplied by the percentage from line 5"
    # print no "(if negative, enter "0")". Line 6 is signed with line 4 (to be confirmed).
    for kind in (RC359_LINE_4, RC359_LINE_6):
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED
        assert registry.kind(kind.identifier) is kind


def test_the_rc359_excess_amount_and_the_tax_lines_are_not_below_zero(
    registry: ArtifactRegistry,
) -> None:
    # Line 7 "Line 1 minus line 6 (if negative, enter "0")" is floored; line 8 is a printed
    # percentage, not a rate; line 9 is line 7 multiplied by line 8; line 41800 totals line 9.
    for kind in (
        RC359_EXCESS_EPSP_AMOUNT,
        RC359_LINE_8,
        RC359_TAX_ON_EXCESS_EPSP,
        RC359_TAX_TOTAL,
    ):
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_net_tax_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/special_taxes") is SPECIAL_TAXES
    assert registry.get("ca/net_federal_tax") is NET_FEDERAL_TAX
    assert registry.get("ca/cpp_payable_on_self_employment") is CPP_PAYABLE_ON_SELF_EMPLOYMENT
    assert registry.get("ca/ei_payable_on_self_employment") is EI_PAYABLE_ON_SELF_EMPLOYMENT
    assert registry.get("ca/social_benefits_repayment_payable") is SOCIAL_BENEFITS_REPAYMENT_PAYABLE
    assert registry.get("ca/total_payable") is TOTAL_PAYABLE
    assert registry.get("ca/income_tax_deducted") is INCOME_TAX_DEDUCTED
    assert registry.get("ca/split_income_line_10") is SPLIT_INCOME_LINE_10
    assert registry.get("ca/split_income_line_13") is SPLIT_INCOME_LINE_13
    assert registry.get("ca/split_income_line_14") is SPLIT_INCOME_LINE_14
    assert registry.get("ca/split_income_line_15") is SPLIT_INCOME_LINE_15
    assert registry.get("ca/split_income_line_18") is SPLIT_INCOME_LINE_18
    assert registry.get("ca/split_income_line_19") is SPLIT_INCOME_LINE_19
    assert registry.get("ca/split_income_line_20") is SPLIT_INCOME_LINE_20
    assert registry.get("ca/split_income_line_21") is SPLIT_INCOME_LINE_21
    assert registry.get("ca/split_income_line_22") is SPLIT_INCOME_LINE_22
    assert registry.get("ca/split_income_line_23") is SPLIT_INCOME_LINE_23
    assert registry.get("ca/split_income_line_24") is SPLIT_INCOME_LINE_24
    assert registry.get("ca/split_income_line_29") is SPLIT_INCOME_LINE_29
    assert registry.get("ca/split_income_line_30") is SPLIT_INCOME_LINE_30


def test_the_net_tax_kinds_are_money() -> None:
    for kind in (
        SPECIAL_TAXES,
        NET_FEDERAL_TAX,
        CPP_PAYABLE_ON_SELF_EMPLOYMENT,
        EI_PAYABLE_ON_SELF_EMPLOYMENT,
        SOCIAL_BENEFITS_REPAYMENT_PAYABLE,
        TOTAL_PAYABLE,
        INCOME_TAX_DEDUCTED,
        SPLIT_INCOME_LINE_10,
        SPLIT_INCOME_LINE_13,
        SPLIT_INCOME_LINE_14,
        SPLIT_INCOME_LINE_15,
        SPLIT_INCOME_LINE_18,
        SPLIT_INCOME_LINE_19,
        SPLIT_INCOME_LINE_20,
        SPLIT_INCOME_LINE_21,
        SPLIT_INCOME_LINE_22,
        SPLIT_INCOME_LINE_23,
        SPLIT_INCOME_LINE_24,
        SPLIT_INCOME_LINE_29,
        SPLIT_INCOME_LINE_30,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_income_tax_deducted_after_election_is_the_non_negative_amount_the_credits_read(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 43700 after Form T1032: line 39 or line 42 when the election applies, otherwise the
    # checked amount; the total credits sum reads it.
    assert INCOME_TAX_DEDUCTED_AFTER_ELECTION.value_type is Decimal
    assert INCOME_TAX_DEDUCTED_AFTER_ELECTION.non_negative is True
    assert INCOME_TAX_DEDUCTED_AFTER_ELECTION.identifier == "ca/income_tax_deducted_after_election"
    assert (
        registry.get("ca/income_tax_deducted_after_election") is INCOME_TAX_DEDUCTED_AFTER_ELECTION
    )


def test_the_income_before_losses_is_a_non_negative_money_kind_beside_its_input(
    registry: ArtifactRegistry,
) -> None:
    # The income before losses is the income lines with each loss counted as 0, so a loss shown in
    # brackets in total income does not lower the amount it bounds.
    assert INCOME_BEFORE_LOSSES.value_type is Decimal
    assert INCOME_BEFORE_LOSSES.non_negative is True
    assert registry.get("ca/income_before_losses") is INCOME_BEFORE_LOSSES
    for floored in (
        NET_RENTAL_INCOME_NOT_BELOW_ZERO,
        BUSINESS_INCOME_NOT_BELOW_ZERO,
        PROFESSIONAL_INCOME_NOT_BELOW_ZERO,
        COMMISSION_INCOME_NOT_BELOW_ZERO,
        FARMING_INCOME_NOT_BELOW_ZERO,
        FISHING_INCOME_NOT_BELOW_ZERO,
    ):
        assert floored.value_type is Decimal
        assert floored.non_negative is True
        assert registry.get(floored.identifier) is floored


def test_the_t1206_part_2_lines_that_print_no_floor_are_signed(registry: ArtifactRegistry) -> None:
    # Form T1206 Part 2 line 15 "Line 10 minus line 14" and line 22 "Line 15 minus line 21" print no
    # "(if negative, enter "0")", so each is signed; line 24 "Line 22 minus line 23 (if negative,
    # enter "0")" is the floored line, and line 23 multiplies the non-negative federal foreign tax
    # credit by a share.
    for kind in (SPLIT_INCOME_LINE_15, SPLIT_INCOME_LINE_22):
        assert kind.non_negative is False, kind.identifier
        assert registry.kind(kind.identifier) is kind
        assert kind.identifier in SIGNED
    assert SPLIT_INCOME_LINE_23.non_negative is True
    assert SPLIT_INCOME_LINE_24.non_negative is True


def test_the_other_t1206_part_2_lines_are_non_negative(registry: ArtifactRegistry) -> None:
    # Lines 10, 13, 14, 19, 20, 21, 23, 29 and 30 add, take a rate or a share of, or compare
    # non-negative figures, and lines 18 and 24 print "(if negative, enter "0")".
    for kind in (
        SPLIT_INCOME_LINE_10,
        SPLIT_INCOME_LINE_13,
        SPLIT_INCOME_LINE_14,
        SPLIT_INCOME_LINE_18,
        SPLIT_INCOME_LINE_19,
        SPLIT_INCOME_LINE_20,
        SPLIT_INCOME_LINE_21,
        SPLIT_INCOME_LINE_23,
        SPLIT_INCOME_LINE_24,
        SPLIT_INCOME_LINE_29,
        SPLIT_INCOME_LINE_30,
    ):
        assert kind.identifier not in SIGNED, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_social_benefits_repayment_payable_is_a_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 146 and line 42200 "Social benefits repayment (amount from line 23500)" carries the
    # non-negative line 23500.
    assert SOCIAL_BENEFITS_REPAYMENT_PAYABLE.value_type is Decimal
    assert SOCIAL_BENEFITS_REPAYMENT_PAYABLE.non_negative is True
    assert registry.kind("ca/social_benefits_repayment_payable").non_negative is True
    assert "ca/social_benefits_repayment_payable" not in SIGNED
