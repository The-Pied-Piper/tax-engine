"""Registered and money kinds of the federal catalog family `deductions`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.errors import InvalidRecordError
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.catalog import (
    CLERGY_ACCOMMODATION_COST,
    CLERGY_EMPLOYER_RESIDENCE_BENEFIT,
    CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED,
    CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT,
    CLERGY_OTHER_ACCOMMODATION_CLAIMS,
    CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED,
    CLERGY_QUALIFYING_EMPLOYMENT_INCOME,
    CLERGY_RESIDENCE_DEDUCTION,
    CLERGY_RESIDENCE_LINE_2,
    CLERGY_RESIDENCE_LINE_4,
    CLERGY_RESIDENCE_LINE_5,
    CLERGY_RESIDENCE_LINE_8,
    CLERGY_RESIDENCE_LINE_9,
    CLERGY_RESIDENCE_LINE_10,
    CLERGY_RESIDENCE_MONTHS_AMOUNT,
    CLERGY_RESIDENCE_PART_B_COMPLETED,
    CLERGY_RESIDENCE_TOTAL,
    CLERGY_RESIDENCE_TOTAL_LIMITED,
    CPP_ACTUAL_BASE_CONTRIBUTIONS,
    CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS,
    CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS,
    CPT20_EARNINGS,
    DISABILITY_SUPPORTS_DEDUCTION,
    EI_BENEFITS_REPAYMENT,
    EI_BENEFITS_REPAYMENT_CHECKED,
    EI_EXCLUDED_SLIP_NET_INCOME,
    EI_EXCLUDED_SLIPS,
    EI_EXCLUDED_SLIPS_NET_INCOME,
    EI_SELF_EMPLOYMENT_BEFORE_SLIPS,
    EI_SELF_EMPLOYMENT_EARNINGS,
    EI_SPECIAL_BENEFITS_AGREEMENT,
    EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED,
    NET_INCOME,
    NET_INCOME_BEFORE_ADJUSTMENTS,
    NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO,
    NET_INCOME_SIGNED,
    OAS_AND_FEDERAL_SUPPLEMENTS,
    OAS_BENEFITS_BASE_AMOUNT,
    OAS_OVERPAYMENT_RECOVERED,
    OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT,
    OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED,
    OTHER_SPLIT_INCOME,
    OTHER_SPLIT_INCOME_CHECKED,
    OTHER_SPLIT_INCOME_OWN_CHECKED,
    OTHER_SPLIT_INCOME_TOTAL,
    RC381_INSTANCES,
    RDSP_INCOME_REPAYMENT,
    RDSP_INCOME_REPAYMENT_CHECKED,
    SOCIAL_BENEFITS_LINE_5,
    SOCIAL_BENEFITS_LINE_6,
    SOCIAL_BENEFITS_LINE_10,
    SOCIAL_BENEFITS_LINE_11,
    SOCIAL_BENEFITS_LINE_14,
    SOCIAL_BENEFITS_LINE_15,
    SOCIAL_BENEFITS_LINE_17,
    SOCIAL_BENEFITS_LINE_18,
    SOCIAL_BENEFITS_LINE_19,
    SOCIAL_BENEFITS_LINE_21,
    SOCIAL_BENEFITS_REPAYMENT,
    SOCIAL_BENEFITS_REPAYMENT_APPLIES,
    SPLIT_INCOME_DIVIDENDS,
    SPLIT_INCOME_DIVIDENDS_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1,
    SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL,
    SPLIT_INCOME_DIVIDENDS_TOTAL,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
    SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370,
    SUPPORT_PAYMENTS_DEDUCTION,
    SUPPORT_PAYMENTS_MADE_TOTAL,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED,
    T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT,
    T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
    T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    T929_INSTANCES,
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
    TOSI_ADJUSTED_NET_INCOME,
    TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO,
    TOTAL_INCOME_FROM_FOREIGN_SOURCES,
    TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES,
    TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
    TOTAL_SPLIT_INCOME,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED
from tests.kinds import non_negative


def test_the_other_payments_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 25000 - Other payments deduction": the chart's amount may not be
    # above line 14700, a part of which it is. The checked amount is the output of `core/at_most`
    # with line 14700 (`ca/income_support_benefits`) as the bound; the choice on line 9 reads it
    # in place of the input.
    assert (
        registry.kind("ca/other_payments_deduction_above_limit_checked")
        is OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED
    )
    assert OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED is not OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT
    assert OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED.value_type is Decimal
    assert non_negative(OTHER_PAYMENTS_DEDUCTION_ABOVE_LIMIT_CHECKED) is True


def test_the_t1436_line_1_to_6_kinds_are_registered_money(registry: ArtifactRegistry) -> None:
    # Form T1436 (Capital Gains Worksheet) lines 1 to 6 and the Schedule 3 lines 543 and 544 they
    # read: each is a registered Decimal kind, the inputs and the steps alike.
    for identifier in (
        "ca/schedule_3_line_543",
        "ca/schedule_3_line_544",
        "ca/schedule_3_lines_543_and_544_total",
        "ca/capital_gains_deductions_1988_and_1989_amount_a",
        "ca/capital_gains_deductions_line_1",
        "ca/capital_gains_deductions_line_2",
        "ca/capital_gains_deductions_1988_and_1989_after_amount_a",
        "ca/capital_gains_deductions_1988_and_1989_limited",
        "ca/capital_gains_deductions_line_3",
        "ca/capital_gains_deductions_line_4",
        "ca/capital_gains_deductions_line_5",
        "ca/capital_gains_deductions_line_6",
    ):
        assert registry.kind(identifier).value_type is Decimal, identifier


def test_the_schedule_3_lines_543_and_544_are_the_non_negative_inputs(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 3 lines 543 and 544 are amounts of the form, with no floor printed and none needed:
    # the two are declared non-negative, as the six capital gains deductions inputs are.
    for identifier in ("ca/schedule_3_line_543", "ca/schedule_3_line_544"):
        assert non_negative(registry.kind(identifier)) is True, identifier


def test_the_t1436_lines_1_to_6_and_the_amount_a_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Lines 1, 2, 4, 5 and 6 multiply a non-negative amount by a positive printed factor; amount (a)
    # is "if negative, enter 0"; the sum of Schedule 3 lines 543 and 544 is non-negative.
    for identifier in (
        "ca/schedule_3_lines_543_and_544_total",
        "ca/capital_gains_deductions_1988_and_1989_amount_a",
        "ca/capital_gains_deductions_line_1",
        "ca/capital_gains_deductions_line_2",
        "ca/capital_gains_deductions_line_4",
        "ca/capital_gains_deductions_line_5",
        "ca/capital_gains_deductions_line_6",
    ):
        assert non_negative(registry.kind(identifier)) is True, identifier


def test_the_net_income_signed_is_the_signed_twin_of_the_net_income(
    registry: ArtifactRegistry,
) -> None:
    # T1 line 56 and line 23600 "Line 54 minus line 55 (if negative, enter "0")" stays the
    # non-negative `ca/net_income`; Form T1206 Part 1 line 5 "Net income from line 23600 of your
    # tax return (or the amount you would have entered if the instructions on line 23600 read "if
    # negative, show in brackets")" and Schedule ON479-A column 1 line 1 read the amount before
    # that floor, a kind of its own that is signed.
    assert NET_INCOME_SIGNED is not NET_INCOME
    assert NET_INCOME_SIGNED is not NET_INCOME_BEFORE_ADJUSTMENTS
    assert NET_INCOME_SIGNED.identifier == "ca/net_income_signed"
    assert non_negative(NET_INCOME_SIGNED) is False
    assert registry.kind("ca/net_income_signed") is NET_INCOME_SIGNED
    assert "ca/net_income_signed" in SIGNED
    assert non_negative(NET_INCOME) is True
    assert "ca/net_income" not in SIGNED


def test_the_tosi_adjusted_net_income_is_signed(registry: ArtifactRegistry) -> None:
    # Form T1206 Part 1 line 6 "TOSI-adjusted net income: line 4 plus line 5 If negative, enter
    # the result in brackets" (line 5 may itself be in brackets) prints no "(if negative, enter
    # "0")", so it is signed.
    assert non_negative(TOSI_ADJUSTED_NET_INCOME) is False
    assert registry.kind("ca/tosi_adjusted_net_income") is TOSI_ADJUSTED_NET_INCOME
    assert "ca/tosi_adjusted_net_income" in SIGNED


def test_the_tosi_adjusted_net_income_not_below_zero_is_its_non_negative_twin(
    registry: ArtifactRegistry,
) -> None:
    # "(If the TOSI-adjusted net income at line 6 is negative, use the negative value when it is
    # part of an adjusted net income calculation, otherwise use zero.)": the signed line 6 and a
    # second kind for "otherwise use zero", which the basic personal amount, the age amount and
    # Schedule 6 line 7 read.
    assert TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO is not TOSI_ADJUSTED_NET_INCOME
    assert non_negative(TOSI_ADJUSTED_NET_INCOME_NOT_BELOW_ZERO) is True
    assert non_negative(registry.kind("ca/tosi_adjusted_net_income_not_below_zero")) is True
    assert "ca/tosi_adjusted_net_income_not_below_zero" not in SIGNED


def test_the_checked_split_income_dividends_are_registered_non_negative_decimals(
    registry: ArtifactRegistry,
) -> None:
    # Line 1 as checked against the T1 dividends (`core/at_most`), line 2 as checked against line 1
    # and the T1 other than eligible dividends. The sum and the credits read these, not lines 1
    # and 2.
    assert registry.get("ca/split_income_dividends_checked") is SPLIT_INCOME_DIVIDENDS_CHECKED
    assert (
        registry.get("ca/split_income_dividends_other_than_eligible_part_of_line_1")
        is SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1
    )
    assert (
        registry.get("ca/split_income_dividends_other_than_eligible_checked")
        is SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED
    )
    for kind in (
        SPLIT_INCOME_DIVIDENDS_CHECKED,
        SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1,
        SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_checked_t1206_foreign_source_amounts_are_registered_non_negative_decimals(
    registry: ArtifactRegistry,
) -> None:
    # The part of line 3 from foreign sources (68370) is at most line 3 (`core/at_most`), and the
    # checked 68370 is at most the total from foreign sources (68380); line 23 reads the checked
    # 68370 over 68380. Line 49 reads the checked non-business part, which is at most its
    # non-business part of 68370, over the checked non-business total.
    assert (
        registry.get("ca/split_income_from_foreign_sources_part_of_line_3")
        is SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3
    )
    assert registry.get("ca/split_income_from_foreign_sources_checked") is (
        SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED
    )
    assert (
        registry.get("ca/split_income_non_business_from_foreign_sources_part_of_68370")
        is SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370
    )
    assert (
        registry.get("ca/total_non_business_income_from_foreign_sources_checked")
        is TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED
    )
    assert (
        registry.get("ca/split_income_non_business_from_foreign_sources_checked")
        is SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED
    )
    for kind in (
        SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3,
        SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
        SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370,
        TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
        SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_checked_other_split_income_is_a_registered_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Line 3 "All other split income" is at most the income before losses (the T1 income lines,
    # a loss counted as 0, `core/at_most`); the checked line 3 is what line 4 reads, and the raw
    # line 3
    # stays the bound of the foreign-source part of it.
    assert registry.get("ca/other_split_income_checked") is OTHER_SPLIT_INCOME_CHECKED
    assert OTHER_SPLIT_INCOME_CHECKED.value_type is Decimal
    assert non_negative(OTHER_SPLIT_INCOME_CHECKED) is True
    assert OTHER_SPLIT_INCOME_CHECKED.identifier not in SIGNED
    assert registry.get("ca/other_split_income_own_checked") is OTHER_SPLIT_INCOME_OWN_CHECKED
    assert registry.get("ca/other_split_income_total") is OTHER_SPLIT_INCOME_TOTAL
    assert registry.get("ca/split_income_dividends_total") is SPLIT_INCOME_DIVIDENDS_TOTAL
    assert (
        registry.get("ca/split_income_dividends_other_than_eligible_total")
        is SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_TOTAL
    )


def test_the_t1206_part_1_amounts_are_non_negative_decimals(registry: ArtifactRegistry) -> None:
    # Lines 1 to 3 are the caller's amounts of split income, and line 4 adds them; lines 68370 and
    # 68380 and their non-business parts (line 49) are the caller's amounts from foreign sources.
    for kind in (
        SPLIT_INCOME_DIVIDENDS,
        SPLIT_INCOME_DIVIDENDS_CHECKED,
        SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE,
        SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_PART_OF_LINE_1,
        SPLIT_INCOME_DIVIDENDS_OTHER_THAN_ELIGIBLE_CHECKED,
        OTHER_SPLIT_INCOME,
        OTHER_SPLIT_INCOME_CHECKED,
        SPLIT_INCOME_FROM_FOREIGN_SOURCES,
        TOTAL_INCOME_FROM_FOREIGN_SOURCES,
        SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES,
        TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES,
        TOTAL_NON_BUSINESS_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
        SPLIT_INCOME_FROM_FOREIGN_SOURCES_CHECKED,
        SPLIT_INCOME_FROM_FOREIGN_SOURCES_PART_OF_LINE_3,
        SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_PART_OF_68370,
        SPLIT_INCOME_NON_BUSINESS_FROM_FOREIGN_SOURCES_CHECKED,
        TOTAL_SPLIT_INCOME,
    ):
        assert kind.identifier not in SIGNED, kind.identifier
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_net_income_before_adjustments_not_below_zero_is_its_non_negative_twin(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 25000 - Other payments deduction" line 1 "Amount from line 23400 of
    # your return (if negative, enter "0")": line 23400 stays signed ("show in brackets") and,
    # once line 23500 reduces the net income of line 23600, this line needs its own floored kind.
    assert NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO is not NET_INCOME_BEFORE_ADJUSTMENTS
    assert NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO is not NET_INCOME
    assert non_negative(NET_INCOME_BEFORE_ADJUSTMENTS_NOT_BELOW_ZERO) is True
    assert non_negative(registry.kind("ca/net_income_before_adjustments_not_below_zero")) is True
    assert "ca/net_income_before_adjustments_not_below_zero" not in SIGNED


def test_the_social_benefits_chart_lines_that_print_no_floor_are_signed(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 23500 - Social benefits repayment": line 6 "Net income before
    # adjustments from line 23400 of your return" (line 23400 may be negative, and the T1206 line
    # 4 is added), line 11 "Line 6 minus line 10 =" and line 15 "Line 11 plus line 14 Adjusted net
    # income" print no "(if negative, enter "0")".
    for kind in (SOCIAL_BENEFITS_LINE_6, SOCIAL_BENEFITS_LINE_11, SOCIAL_BENEFITS_LINE_15):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is False, kind.identifier
        assert registry.kind(kind.identifier) is kind
        assert kind.identifier in SIGNED


def test_the_other_social_benefits_chart_lines_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Lines 5 and 17 print "(if negative, enter "0")"; the others add, take 15% of, or compare
    # non-negative figures. The two caller inputs are slip boxes.
    for kind in (
        OAS_OVERPAYMENT_RECOVERED,
        EI_BENEFITS_REPAYMENT,
        OAS_AND_FEDERAL_SUPPLEMENTS,
        SOCIAL_BENEFITS_LINE_5,
        SOCIAL_BENEFITS_LINE_10,
        SOCIAL_BENEFITS_LINE_14,
        OAS_BENEFITS_BASE_AMOUNT,
        SOCIAL_BENEFITS_LINE_17,
        SOCIAL_BENEFITS_LINE_18,
        SOCIAL_BENEFITS_LINE_19,
        SOCIAL_BENEFITS_LINE_21,
        SOCIAL_BENEFITS_REPAYMENT,
    ):
        assert kind.identifier not in SIGNED, kind.identifier
        assert non_negative(kind) is True, kind.identifier
        assert registry.kind(kind.identifier) is kind


def test_the_rdsp_income_repayment_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 23500 - Social benefits repayment" line 13 "RDSP income repayment
    # (included in the amount on line 23200 of your return)": the repayment is refused above the
    # caller's line 23200 amount (`ca/other_deductions`) as an input error, not capped. The checked
    # amount is the output of `core/at_most`, which lines 14 and 15 read in place of the input.
    assert registry.kind("ca/rdsp_income_repayment_checked") is RDSP_INCOME_REPAYMENT_CHECKED
    assert RDSP_INCOME_REPAYMENT_CHECKED.value_type is Decimal
    assert non_negative(RDSP_INCOME_REPAYMENT_CHECKED) is True
    assert RDSP_INCOME_REPAYMENT_CHECKED is not RDSP_INCOME_REPAYMENT
    assert RDSP_INCOME_REPAYMENT_CHECKED.identifier in REGISTERED


def test_the_ei_benefits_repayment_checked_kind_is_registered_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # Federal Worksheet "Line 23500 - Social benefits repayment" line 7 "EI benefits repayment from
    # line 4 of the repayment chart on your T4E slip, if any": the repayment is refused above the
    # EI and other benefits received on line 11900 (`ca/ei_and_other_benefits`) as an input error,
    # not capped. The repayment is part of the benefits, and the form prints no other limit. The
    # checked amount is the output of `core/at_most`, which lines 10 and 21 read in place of the
    # input.
    assert registry.kind("ca/ei_benefits_repayment_checked") is EI_BENEFITS_REPAYMENT_CHECKED
    assert EI_BENEFITS_REPAYMENT_CHECKED.value_type is Decimal
    assert non_negative(EI_BENEFITS_REPAYMENT_CHECKED) is True
    assert EI_BENEFITS_REPAYMENT_CHECKED is not EI_BENEFITS_REPAYMENT
    assert EI_BENEFITS_REPAYMENT_CHECKED.identifier in REGISTERED


def test_the_social_benefits_chart_applies_count_is_an_int_kind(registry: ArtifactRegistry) -> None:
    # The entry conditions of the chart ("Complete the chart below if one or both of the following
    # applies:") give a count, 1 when the chart applies and 0 otherwise.
    assert SOCIAL_BENEFITS_REPAYMENT_APPLIES.value_type is int
    assert registry.kind("ca/social_benefits_repayment_applies").value_type is int
    assert "ca/social_benefits_repayment_applies" in COUNTS


def test_the_ei_excluded_slips_are_a_record_list_of_the_net_income_of_each_slip(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 13 line 1: "If you received a T4 slip for self-employment income with EI premiums
    # in box 18, do not include any net income (or net loss) reported on lines 13500, 13700,
    # 13900, 14100, and 14300 of your return for that slip": one record per such slip, whose one
    # field is the net income (or net loss) reported for it.
    assert isinstance(EI_EXCLUDED_SLIPS, RecordListKind)
    assert EI_EXCLUDED_SLIPS.identifier == "ca/ei_excluded_slips"
    assert EI_EXCLUDED_SLIPS.value_type is RecordList
    assert non_negative(EI_EXCLUDED_SLIPS) is False
    assert EI_EXCLUDED_SLIPS.fields == (EI_EXCLUDED_SLIP_NET_INCOME,)
    assert registry.get("ca/ei_excluded_slips") is EI_EXCLUDED_SLIPS
    assert "ca/ei_excluded_slips" in RECORD_LISTS
    assert "ca/ei_excluded_slips" in REGISTERED


def test_the_net_income_of_an_excluded_slip_is_a_signed_decimal(
    registry: ArtifactRegistry,
) -> None:
    # "(or net loss)": a slip may report a loss, so the field is not declared non-negative.
    assert EI_EXCLUDED_SLIP_NET_INCOME.identifier == "ca/ei_excluded_slip_net_income"
    assert EI_EXCLUDED_SLIP_NET_INCOME.value_type is Decimal
    assert non_negative(EI_EXCLUDED_SLIP_NET_INCOME) is False
    assert registry.kind("ca/ei_excluded_slip_net_income") is EI_EXCLUDED_SLIP_NET_INCOME
    assert "ca/ei_excluded_slip_net_income" in SIGNED


def test_the_ei_excluded_slips_hold_a_loss_and_may_be_empty() -> None:
    rows = RecordList(
        EI_EXCLUDED_SLIPS.fields,
        [
            {EI_EXCLUDED_SLIP_NET_INCOME: Decimal("20000")},
            {EI_EXCLUDED_SLIP_NET_INCOME: Decimal("-1500")},
        ],
    )

    assert [record[EI_EXCLUDED_SLIP_NET_INCOME] for record in rows.records] == [
        Decimal("20000"),
        Decimal("-1500"),
    ]
    assert RecordList(EI_EXCLUDED_SLIPS.fields, []).records == ()


def test_an_excluded_slip_missing_its_net_income_is_refused_naming_the_row() -> None:
    with pytest.raises(InvalidRecordError, match="item 1.*ei_excluded_slip_net_income"):
        RecordList(EI_EXCLUDED_SLIPS.fields, [{}])


def test_schedule_13_line_1_before_the_slips_is_signed(registry: ArtifactRegistry) -> None:
    # Line 1 is "the total amount from line 12200 plus line 27": before the slips and the "(if
    # negative, enter "0")" floor of the finished line 1, so it is not declared non-negative.
    assert EI_SELF_EMPLOYMENT_BEFORE_SLIPS.identifier == "ca/ei_self_employment_before_slips"
    assert EI_SELF_EMPLOYMENT_BEFORE_SLIPS.value_type is Decimal
    assert non_negative(EI_SELF_EMPLOYMENT_BEFORE_SLIPS) is False
    assert registry.kind("ca/ei_self_employment_before_slips") is EI_SELF_EMPLOYMENT_BEFORE_SLIPS
    assert "ca/ei_self_employment_before_slips" in SIGNED


def test_the_net_income_of_all_the_excluded_slips_is_signed(registry: ArtifactRegistry) -> None:
    # The total of the slips' net income (or net loss) may be a loss.
    assert EI_EXCLUDED_SLIPS_NET_INCOME.identifier == "ca/ei_excluded_slips_net_income"
    assert EI_EXCLUDED_SLIPS_NET_INCOME.value_type is Decimal
    assert non_negative(EI_EXCLUDED_SLIPS_NET_INCOME) is False
    assert registry.kind("ca/ei_excluded_slips_net_income") is EI_EXCLUDED_SLIPS_NET_INCOME
    assert "ca/ei_excluded_slips_net_income" in SIGNED


def test_schedule_13_line_1_stays_non_negative_after_the_slips(registry: ArtifactRegistry) -> None:
    # "(if negative, enter "0")" is on the finished line 1, ca/ei_self_employment_earnings.
    assert EI_SELF_EMPLOYMENT_EARNINGS is not EI_SELF_EMPLOYMENT_BEFORE_SLIPS
    assert non_negative(EI_SELF_EMPLOYMENT_EARNINGS) is True
    assert "ca/ei_self_employment_earnings" not in SIGNED


# Schedule 8 Part 3 the box 16 and 16A totals the filer enters, and the lines
# that compare them with the required contributions. The kinds are reached through the module
# so that the rest of this file runs before they are declared.
def test_the_cpp_t4_box_totals_are_non_negative_money_the_filer_enters(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 8 Part 3 line 8 and line 50340 "Total actual base and first additional
    # contributions on CPP pensionable earnings from box 16 of all of your T4 slips", and line 21
    # and line 50341 "Total actual second additional contributions on CPP pensionable earnings
    # from box 16A of all of your T4 slips": amounts the filer enters, never below zero.
    for identifier in (
        "ca/cpp_t4_base_and_first_additional_contributions",
        "ca/cpp_t4_second_additional_contributions",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
    assert (
        registry.kind("ca/cpp_t4_base_and_first_additional_contributions")
        is CPP_T4_BASE_AND_FIRST_ADDITIONAL_CONTRIBUTIONS
    )
    assert (
        registry.kind("ca/cpp_t4_second_additional_contributions")
        is CPP_T4_SECOND_ADDITIONAL_CONTRIBUTIONS
    )
    assert registry.kind("ca/rc381_instances") is RC381_INSTANCES
    assert registry.kind("ca/t929_instances") is T929_INSTANCES


def test_the_cpp_part_3_lines_that_print_no_brackets_are_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Line 9 is "amount from line 8 multiplied by 83.1933%", line 10 is "Line 8 minus line 9" (the
    # factor is below 100%, so it is never below zero) and line 13 is "Line 11 plus line 12": none
    # can be negative, and none prints "(if negative, show in brackets)".
    for identifier in (
        "ca/cpp_actual_base_contributions",
        "ca/cpp_actual_first_additional_contributions",
        "ca/cpp_required_base_and_first_additional_contributions",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
    assert registry.kind("ca/cpp_actual_base_contributions") is CPP_ACTUAL_BASE_CONTRIBUTIONS


def test_the_cpp_part_3_difference_lines_are_signed_as_their_brackets_say(
    registry: ArtifactRegistry,
) -> None:
    # Lines 16, 19, 20, 23 and 24 each print "(if negative, show in brackets)", so each is a
    # signed Decimal, a loss of contributions over the required ones included.
    for identifier in (
        "ca/cpp_first_additional_contributions_difference",
        "ca/cpp_base_and_first_additional_contributions_difference",
        "ca/cpp_second_additional_contributions_difference",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is False, identifier
        assert identifier in SIGNED, identifier


def test_the_cpp_part_3b_lines_and_the_three_return_lines_are_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    # The zero of "enter "0"", lines 30 to 48 of Part 3b (each is a chosen non-negative amount, a
    # sum of them, or a difference that cannot go below zero) and T1 line 30800, line 22215 and
    # line 44800 as the form routes them: none prints brackets.
    for identifier in (
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
        "ca/cpp_base_contributions_on_return",
        "ca/cpp_enhanced_contributions_on_return",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
        assert identifier in REGISTERED, identifier


# Schedule 8 Part 5 lines 1 to 42 (self-employment income and other earnings when the filer also
# has employment income): the T4 CPT20 input, Part 3 line 2 and the lines of Part 5. The kinds are
# reached through the registry so that the rest of this file runs before they are declared.
def test_the_cpt20_earnings_shown_on_a_t4_slip_are_a_non_negative_input(
    registry: ArtifactRegistry,
) -> None:
    # Part 5 line 3 and line 50399 "Employment earnings shown on a T4 slip that you are electing
    # to pay additional CPP contributions on (complete Form CPT20)": an amount the filer enters,
    # never below zero, like line 2 (CPT20 earnings not shown on a T4 slip).
    kind = registry.kind("ca/cpt20_t4_earnings")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert "ca/cpt20_t4_earnings" not in SIGNED
    assert "ca/cpt20_t4_earnings" in REGISTERED
    assert kind is not CPT20_EARNINGS


def test_part_3_line_2_is_a_non_negative_amount_of_employment_earnings(
    registry: ArtifactRegistry,
) -> None:
    # Part 3 line 2 "Enter whichever is less: amount from line D of Part 2 or line 1": the lesser
    # of two non-negative amounts, read by Part 5 line 32 ("Amount from line 2 of Part 3").
    kind = registry.kind("ca/cpp_part_3_line_2")
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert "ca/cpp_part_3_line_2" not in SIGNED
    assert "ca/cpp_part_3_line_2" in REGISTERED


def test_the_lines_the_part_5_routing_reads_are_non_negative_money(
    registry: ArtifactRegistry,
) -> None:
    # The Part 3 route of lines 30800, 22215 and 44800 keeps the PR 2 steps under a name of its
    # own; the kinds the readers (ON428, Schedule 8's credit, the deductions, the refund total)
    # read keep their names and choose between the Part 3 route and Part 5 lines 57, 69 and 50 by
    # the Part 5 completed count. Lines 31000, 22200 and 42100 are the Part 4 route plus the Part
    # 5 route (Part 5 line 70, line 88 and line 49 if positive, once for each Part 5 completed).
    for identifier in (
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
        "ca/cpp_base_contributions_on_return",
        "ca/cpp_enhanced_contributions_on_return",
        "ca/cpp_part_5_base_contributions_on_self_employment",
        "ca/cpp_base_contributions_on_self_employment",
        "ca/cpp_base_contributions_on_self_employment_and_other_earnings",
        "ca/cpp_part_5_deduction_on_self_employment",
        "ca/cpp_deduction_on_self_employment",
        "ca/cpp_deduction_on_self_employment_and_other_earnings",
        "ca/cpp_part_5_payable_on_self_employment",
        "ca/cpp_payable_on_self_employment",
        "ca/cpp_payable_on_self_employment_and_other_earnings",
    ):
        kind = registry.kind(identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier
        assert identifier not in SIGNED, identifier
        assert identifier in REGISTERED, identifier


# Form T1223 Part C, 2025: the clergy residence deduction, T1 line 23100. The six inputs are the
# figures the form takes from the filer (Part C (A), lines 1, 3, 6 and 7, and the Part C (B)
# choice); the lines 2 to 10 and the totals are calculated from them and the datasets. Line 23100
# was a starting amount (an input) until it was calculated here.


def test_the_clergy_residence_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    assert registry.get("ca/clergy_employer_residence_benefit") is CLERGY_EMPLOYER_RESIDENCE_BENEFIT
    assert (
        registry.get("ca/clergy_qualifying_employment_income")
        is CLERGY_QUALIFYING_EMPLOYMENT_INCOME
    )
    assert (
        registry.get("ca/clergy_months_in_qualifying_employment")
        is CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT
    )
    assert registry.get("ca/clergy_accommodation_cost") is CLERGY_ACCOMMODATION_COST
    assert registry.get("ca/clergy_other_accommodation_claims") is CLERGY_OTHER_ACCOMMODATION_CLAIMS
    assert registry.get("ca/clergy_residence_part_b_completed") is CLERGY_RESIDENCE_PART_B_COMPLETED
    assert registry.get("ca/clergy_residence_line_2") is CLERGY_RESIDENCE_LINE_2
    assert registry.get("ca/clergy_residence_months_amount") is CLERGY_RESIDENCE_MONTHS_AMOUNT
    assert registry.get("ca/clergy_residence_line_4") is CLERGY_RESIDENCE_LINE_4
    assert registry.get("ca/clergy_residence_line_5") is CLERGY_RESIDENCE_LINE_5
    assert registry.get("ca/clergy_residence_line_8") is CLERGY_RESIDENCE_LINE_8
    assert registry.get("ca/clergy_residence_line_9") is CLERGY_RESIDENCE_LINE_9
    assert registry.get("ca/clergy_residence_line_10") is CLERGY_RESIDENCE_LINE_10
    assert registry.get("ca/clergy_residence_total") is CLERGY_RESIDENCE_TOTAL
    assert registry.get("ca/clergy_residence_total_limited") is CLERGY_RESIDENCE_TOTAL_LIMITED
    assert registry.get("ca/clergy_residence_deduction") is CLERGY_RESIDENCE_DEDUCTION


def test_the_clergy_residence_money_kinds_are_decimal(registry: ArtifactRegistry) -> None:
    for kind in (
        CLERGY_EMPLOYER_RESIDENCE_BENEFIT,
        CLERGY_QUALIFYING_EMPLOYMENT_INCOME,
        CLERGY_ACCOMMODATION_COST,
        CLERGY_OTHER_ACCOMMODATION_CLAIMS,
        CLERGY_RESIDENCE_LINE_2,
        CLERGY_RESIDENCE_MONTHS_AMOUNT,
        CLERGY_RESIDENCE_LINE_4,
        CLERGY_RESIDENCE_LINE_5,
        CLERGY_RESIDENCE_LINE_8,
        CLERGY_RESIDENCE_LINE_9,
        CLERGY_RESIDENCE_LINE_10,
        CLERGY_RESIDENCE_TOTAL,
        CLERGY_RESIDENCE_TOTAL_LIMITED,
        CLERGY_RESIDENCE_DEDUCTION,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_checked_clergy_employer_residence_benefit_is_a_registered_decimal(
    registry: ArtifactRegistry,
) -> None:
    # The benefit as checked against line 10400 (`core/at_most`), the amount the sum reads.
    assert (
        registry.get("ca/clergy_employer_residence_benefit_checked")
        is CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED
    )
    assert CLERGY_EMPLOYER_RESIDENCE_BENEFIT_CHECKED.value_type is Decimal


def test_the_checked_clergy_other_accommodation_claims_is_a_registered_non_negative_decimal(
    registry: ArtifactRegistry,
) -> None:
    # Line 7 as checked against line 6 (`core/at_most`), the amount line 8 subtracts. A claim is
    # never negative, so the kind is non-negative like the raw line 7 it checks.
    identifier = "ca/clergy_other_accommodation_claims_checked"
    assert registry.get(identifier) is CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED
    assert CLERGY_OTHER_ACCOMMODATION_CLAIMS_CHECKED.value_type is Decimal
    assert non_negative(kind_of(registry, identifier)) is True


def test_the_clergy_residence_counts_are_int_kinds(registry: ArtifactRegistry) -> None:
    # T1223 Part C line 3 "Number of months in qualifying employment" is a count of months, and
    # (B) being completed is a 0 or 1 the filer states.
    assert CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT.value_type is int
    assert CLERGY_RESIDENCE_PART_B_COMPLETED.value_type is int
    assert registry.get("ca/clergy_months_in_qualifying_employment") is (
        CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT
    )
    assert registry.get("ca/clergy_residence_part_b_completed") is CLERGY_RESIDENCE_PART_B_COMPLETED


def test_the_clergy_residence_amounts_on_lines_2_to_5_and_the_inputs_are_not_below_zero() -> None:
    # Each is a dollars-and-cents line that cannot be negative on the form as modelled: the
    # fraction of the income, the months amount, its cap, the greater of lines 2 and 4, and the
    # figures the filer enters.
    for kind in (
        CLERGY_EMPLOYER_RESIDENCE_BENEFIT,
        CLERGY_QUALIFYING_EMPLOYMENT_INCOME,
        CLERGY_MONTHS_IN_QUALIFYING_EMPLOYMENT,
        CLERGY_ACCOMMODATION_COST,
        CLERGY_OTHER_ACCOMMODATION_CLAIMS,
        CLERGY_RESIDENCE_PART_B_COMPLETED,
        CLERGY_RESIDENCE_LINE_2,
        CLERGY_RESIDENCE_MONTHS_AMOUNT,
        CLERGY_RESIDENCE_LINE_4,
        CLERGY_RESIDENCE_LINE_5,
        CLERGY_RESIDENCE_DEDUCTION,
    ):
        assert non_negative(kind) is True, kind.identifier


def test_the_clergy_residence_lines_8_to_10_and_the_totals_are_signed() -> None:
    # Form T1223 Part C line 8 "Line 6 minus line 7 =", line 9 "Enter whichever is less: Line 5 or
    # line 8." and line 10 "Enter whichever is less: Line 1 or line 9." print no floor, so a
    # negative line 8 passes through; the (A) and (B) total and its limit are not floored either.
    for kind in (
        CLERGY_RESIDENCE_LINE_8,
        CLERGY_RESIDENCE_LINE_9,
        CLERGY_RESIDENCE_LINE_10,
        CLERGY_RESIDENCE_TOTAL,
        CLERGY_RESIDENCE_TOTAL_LIMITED,
    ):
        assert non_negative(kind) is False, kind.identifier


T929_COMPUTED_NON_NEGATIVE = (
    T929_NET_BUSINESS_INCOME,
    T929_NET_FARMING_INCOME,
    T929_NET_FISHING_INCOME,
    T929_NET_PROFESSIONAL_INCOME,
    T929_NET_COMMISSION_INCOME,
    T929_LINE_4,
    T929_LINE_7,
    T929_LINE_9,
    T929_LINE_10,
    T929_LINE_11,
)


def test_the_disability_supports_deduction_is_computed_and_registered_here(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/disability_supports_deduction") is DISABILITY_SUPPORTS_DEDUCTION
    assert DISABILITY_SUPPORTS_DEDUCTION.value_type is Decimal
    assert non_negative(DISABILITY_SUPPORTS_DEDUCTION) is True


def test_the_t929_computed_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for kind in (*T929_COMPUTED_NON_NEGATIVE, T929_LINE_3):
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t929_computed_amounts_are_non_negative_decimals() -> None:
    for kind in T929_COMPUTED_NON_NEGATIVE:
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier


def test_t929_line_3_is_signed_as_the_form_does_not_floor_it() -> None:
    assert T929_LINE_3.value_type is Decimal
    assert non_negative(T929_LINE_3) is False


def test_the_t929_instances_is_a_record_list_of_no_fields() -> None:
    assert isinstance(T929_INSTANCES, RecordListKind)
    assert T929_INSTANCES.fields == ()


# --- moving expenses, Form T1-M (T1 line 21900) -----------------------------------------------

# The 19 caller inputs of one move, the fields of `ca/t1_m_moves`, in the form's line order: lines
# 1, 2, 4, 5, 6, 7, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 22, 25 and 28.
MOVING_INPUTS = (
    "ca/moving_old_home_distance",
    "ca/moving_new_home_distance",
    "ca/moving_transportation_and_storage",
    "ca/moving_travel_expenses",
    "ca/moving_accommodation_expenses",
    "ca/moving_meal_expenses",
    "ca/moving_temporary_lodging",
    "ca/moving_temporary_meals",
    "ca/moving_lease_cancellation",
    "ca/moving_incidental_costs",
    "ca/moving_old_home_maintenance",
    "ca/moving_selling_commission",
    "ca/moving_selling_legal_fees",
    "ca/moving_selling_advertising",
    "ca/moving_selling_other_costs",
    "ca/moving_buying_legal_fees",
    "ca/moving_buying_taxes",
    "ca/moving_reimbursement",
    "ca/moving_net_eligible_income",
)

# The computed lines of one move, the exports and T1 line 21900: line 3 (signed, the form prints no
# floor), line 8, 11, 14 (capped), 15, 20, 23, 24, 26, 27, the lesser of 27 and 28, line 29 (gated
# by the 40 kilometre test), line 30 and the total of line 21900.
MOVING_COMPUTED = (
    "ca/moving_distance_difference",
    "ca/moving_travel_expenses_subtotal",
    "ca/moving_temporary_living_subtotal",
    "ca/moving_old_home_maintenance_cap",
    "ca/moving_old_home_maintenance_checked",
    "ca/moving_lease_and_incidental_subtotal",
    "ca/moving_selling_subtotal",
    "ca/moving_buying_subtotal",
    "ca/moving_total_expenses",
    "ca/moving_net_expenses",
    "ca/moving_net_expenses_carried",
    "ca/moving_lesser_of_expenses_and_income",
    "ca/moving_expenses_claim",
    "ca/moving_unused_expenses_before_test",
    "ca/moving_unused_expenses",
    "ca/moving_expenses_deduction",
)


def kind_of(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    """The registered kind `identifier`; the registry raises for a kind it does not hold."""
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind


def test_the_moving_expenses_kinds_are_the_registered_ones(registry: ArtifactRegistry) -> None:
    for identifier in ("ca/t1_m_moves", *MOVING_INPUTS, *MOVING_COMPUTED):
        assert kind_of(registry, identifier).identifier == identifier, identifier


def test_the_t1_m_moves_list_the_19_inputs_of_one_move_in_the_form_line_order(
    registry: ArtifactRegistry,
) -> None:
    moves = registry.get("ca/t1_m_moves")

    assert isinstance(moves, RecordListKind)
    assert tuple(field.identifier for field in moves.fields) == MOVING_INPUTS
    assert len(moves.fields) == 19


def test_the_moving_inputs_are_decimals_that_cannot_be_negative(registry: ArtifactRegistry) -> None:
    # Distances are whole kilometres, but they are Decimals: `core/subtract` takes Decimals only,
    # and a kind of another value type cannot be wired to it.
    for identifier in MOVING_INPUTS:
        kind = kind_of(registry, identifier)
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier


def test_the_moving_amounts_are_decimals(registry: ArtifactRegistry) -> None:
    for identifier in MOVING_COMPUTED:
        assert kind_of(registry, identifier).value_type is Decimal, identifier


def test_only_the_distance_difference_of_the_moving_lines_may_be_negative(
    registry: ArtifactRegistry,
) -> None:
    # Line 3, "Line 1 minus line 2", prints no floor; every other computed line of the form is a
    # sum, a lesser amount or a floor at 0 ("if negative, enter "0"").
    assert non_negative(kind_of(registry, "ca/moving_distance_difference")) is False
    for identifier in MOVING_COMPUTED[1:]:
        assert non_negative(kind_of(registry, identifier)) is True, identifier


def test_the_amt_moving_expenses_stand_in_is_no_longer_a_kind(registry: ArtifactRegistry) -> None:
    # Form T691 Part 1 line 56 is "Moving expenses deduction from line 21900": the alternative
    # minimum tax reads the computed line 21900, so the caller's stand-in is removed.
    assert "ca/amt_moving_expenses_deduction" not in registry.identifiers()


# The income bound of line 28, Form T1-M Part 4: the positive net of each self-employment line, the
# income lines added, and the checked line 28 that lines 29 and 30 read.
MOVING_ELIGIBLE_INCOME_BOUND = (
    "ca/moving_business_income",
    "ca/moving_professional_income",
    "ca/moving_commission_income",
    "ca/moving_farming_income",
    "ca/moving_fishing_income",
    "ca/moving_eligible_income_lines",
    "ca/moving_net_eligible_income_checked",
)


def test_the_moving_income_bound_kinds_are_registered_decimals_that_cannot_be_negative(
    registry: ArtifactRegistry,
) -> None:
    # Each self-employment amount is a positive net (a loss counts 0), and the bound and the checked
    # line 28 are amounts of the form: none of them is a signed amount.
    for identifier in MOVING_ELIGIBLE_INCOME_BOUND:
        kind = kind_of(registry, identifier)
        assert kind.identifier == identifier, identifier
        assert kind.value_type is Decimal, identifier
        assert non_negative(kind) is True, identifier


def test_the_checked_line_28_is_a_kind_of_its_own_beside_the_input(
    registry: ArtifactRegistry,
) -> None:
    # The caller's line 28 stays the input kind; the checked amount is the one lines 29 and 30 read.
    checked = kind_of(registry, "ca/moving_net_eligible_income_checked")
    entered = kind_of(registry, "ca/moving_net_eligible_income")

    assert checked is not entered
    assert "ca/moving_net_eligible_income" in MOVING_INPUTS
    assert "ca/moving_net_eligible_income_checked" not in MOVING_INPUTS


# T1 line 21999 "Total" under "Line 45: Support payments made": a caller's input, and a declared
# output that the line 22000 check reads (it is the bound of `core/at_most`).
def test_the_support_payments_made_total_is_the_registered_money_kind(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/support_payments_made_total") is SUPPORT_PAYMENTS_MADE_TOTAL
    assert SUPPORT_PAYMENTS_MADE_TOTAL.value_type is Decimal
    assert non_negative(SUPPORT_PAYMENTS_MADE_TOTAL) is True


# T1 line 22000 "Enter on line 22000 of your return the deductible part of the support payments that
# you made.": the deductible part is a part of the total paid, so the amount the sum reads is the
# checked amount, which `core/at_most` produces from the deduction against line 21999.
def test_the_support_payments_deduction_checked_is_a_registered_money_kind(
    registry: ArtifactRegistry,
) -> None:
    kind = registry.kind("ca/support_payments_deduction_checked")
    assert kind.identifier == "ca/support_payments_deduction_checked"
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
    assert kind is not SUPPORT_PAYMENTS_DEDUCTION


YES_OR_NO_CHECKED = ((EI_SPECIAL_BENEFITS_AGREEMENT, EI_SPECIAL_BENEFITS_AGREEMENT_CHECKED),)


@pytest.mark.parametrize(("raw", "checked"), YES_OR_NO_CHECKED, ids=lambda kind: kind.identifier)
def test_each_yes_or_no_checked_kind_is_a_non_negative_count_named_after_its_input(
    raw: ArtifactKind[int], checked: ArtifactKind[int], registry: ArtifactRegistry
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the steps that read it; a count of 2 or
    # more is refused, not capped.
    assert checked.identifier == f"{raw.identifier}_checked"
    assert registry.get(checked.identifier) is checked
    assert checked.value_type is int
    assert non_negative(checked) is True


def test_the_t4_security_options_box_totals_are_registered_and_non_negative(
    registry: ArtifactRegistry,
) -> None:
    # Form T691 Part 1 line 28 "Total of all amounts in boxes 39 and 91 of your T4 slips" and
    # line 35 "total of all amounts in boxes 41 and 92 of your T4 slips": each is the total of the
    # T4 box amounts entered on the return, a record total over the form's export.
    assert (
        registry.get("ca/t4_security_options_boxes_39_and_91_total")
        is T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL
    )
    assert (
        registry.get("ca/t4_security_options_boxes_41_and_92_total")
        is T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL
    )
    for kind in (
        T4_SECURITY_OPTIONS_BOXES_39_AND_91_TOTAL,
        T4_SECURITY_OPTIONS_BOXES_41_AND_92_TOTAL,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert non_negative(kind) is True, kind.identifier


def test_the_t4_security_options_boxes_are_not_declared_under_the_amt_names(
    registry: ArtifactRegistry,
) -> None:
    # The T4 boxes 39, 41, 91 and 92 are entered once, as the facts of the forms
    # `ca/security_options_boxes_39_and_91` and `ca/security_options_boxes_41_and_92`, and the
    # alternative minimum tax reads the totals of those facts; the `amt_` names are gone.
    identifiers = registry.identifiers()

    assert "ca/amt_t4_security_options_boxes_39_and_91" not in identifiers
    assert "ca/amt_t4_security_options_boxes_41_and_92" not in identifiers
    assert "ca/t4_security_options_boxes_39_and_91" in identifiers
    assert "ca/t4_security_options_boxes_41_and_92" in identifiers


T4_SLIP_COUNT_AMOUNTS: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/t4_cpp_pensionable_earnings_slip_limit", T4_CPP_PENSIONABLE_EARNINGS_SLIP_LIMIT),
    ("ca/t4_cpp_pensionable_earnings_slip_checked", T4_CPP_PENSIONABLE_EARNINGS_SLIP_CHECKED),
    ("ca/t4_qpp_pensionable_earnings_slip_limit", T4_QPP_PENSIONABLE_EARNINGS_SLIP_LIMIT),
    ("ca/t4_qpp_pensionable_earnings_slip_checked", T4_QPP_PENSIONABLE_EARNINGS_SLIP_CHECKED),
)


@pytest.mark.parametrize(("identifier", "kind"), T4_SLIP_COUNT_AMOUNTS)
def test_the_t4_slip_count_limit_and_checked_kinds_are_registered_and_not_negative(
    registry: ArtifactRegistry, identifier: str, kind: ArtifactKind[Decimal]
) -> None:
    # The maximum of one slip times the count of slips (Schedule 8 Part 3, Form RC381 Part 3).
    assert registry.get(identifier) is kind
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
