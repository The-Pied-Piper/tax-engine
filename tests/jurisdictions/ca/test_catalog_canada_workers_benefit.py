"""Registered and money kinds of the federal catalog family `canada_workers_benefit`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    ACWB_LINE_46_APPLIES,
    ACWB_LINES_44_AND_45,
    ADJUSTED_FAMILY_NET_INCOME,
    CANADA_WORKERS_BENEFIT,
    CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS,
    CANADA_WORKERS_BENEFIT_LINE_28,
    CANADA_WORKERS_BENEFIT_LINE_41,
    CANADA_WORKERS_BENEFIT_LINE_42,
    CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
    CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
    CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
    CWB_CLAIMING_BASIC,
    CWB_CLAIMING_BASIC_CHECKED,
    CWB_DISABILITY_REDUCTION,
    CWB_DISABILITY_REDUCTION_BY_SPOUSE,
    CWB_DISABILITY_REDUCTION_BY_STATUS,
    CWB_DISABILITY_REDUCTION_WITH_DEPENDANT,
    CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE,
    CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT,
    CWB_DISABILITY_SUPPLEMENT,
    CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION,
    CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
    CWB_ELIGIBLE_DEPENDANTS,
    CWB_ELIGIBLE_DEPENDANTS_CHECKED,
    CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC,
    CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED,
    CWB_ELIGIBLE_SPOUSES,
    CWB_ELIGIBLE_SPOUSES_CHECKED,
    CWB_EMPLOYMENT_INCOME,
    CWB_FAMILY_NET_INCOME_LINE_10,
    CWB_FAMILY_NET_INCOME_LINE_12,
    CWB_FAMILY_NET_INCOME_LINE_13,
    CWB_FAMILY_WORKING_INCOME,
    CWB_INCLUDE_TAX_EXEMPT_INCOME,
    CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED,
    CWB_LINE_28_BY_SPOUSE,
    CWB_REDUCTION_WITH_DEPENDANT,
    CWB_REDUCTION_WITHOUT_DEPENDANT,
    CWB_SECONDARY_EARNER_EXEMPTION,
    CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM,
    CWB_SECONDARY_EARNER_SPOUSES,
    CWB_SECONDARY_EARNER_YOURS,
    CWB_SPOUSE_CLAIMING_BASIC,
    CWB_SPOUSE_CLAIMING_BASIC_CHECKED,
    CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED,
    CWB_SPOUSE_EMPLOYMENT_INCOME,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12,
    CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY,
    CWB_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
    CWB_SPOUSE_NET_EXEMPT_INCOME,
    CWB_SPOUSE_SELF_EMPLOYMENT_INCOME,
    CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED,
    CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME,
    CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED,
    CWB_SPOUSE_TAXABLE_SCHOLARSHIPS,
    CWB_SPOUSE_UCCB_AND_RDSP_INCOME,
    CWB_SPOUSE_WORKING_INCOME,
    CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY,
    CWB_TAX_EXEMPT_NET_INCOME,
    CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION,
    CWB_TAX_EXEMPT_WORKING_INCOME,
    CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION,
    CWB_WORKING_INCOME_LESS_SPOUSE,
    WORKING_INCOME,
)


def test_the_canada_workers_benefit_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    assert registry.get("ca/cwb_eligible_dependants") is CWB_ELIGIBLE_DEPENDANTS
    assert registry.get("ca/cwb_employment_income") is CWB_EMPLOYMENT_INCOME
    assert registry.get("ca/working_income") is WORKING_INCOME
    assert registry.get("ca/cwb_family_net_income_line_10") is CWB_FAMILY_NET_INCOME_LINE_10
    assert registry.get("ca/cwb_family_net_income_line_12") is CWB_FAMILY_NET_INCOME_LINE_12
    assert registry.get("ca/adjusted_family_net_income") is ADJUSTED_FAMILY_NET_INCOME
    assert (
        registry.get("ca/cwb_before_reduction_without_dependant")
        is CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT
    )
    assert registry.get("ca/cwb_reduction_without_dependant") is CWB_REDUCTION_WITHOUT_DEPENDANT
    assert (
        registry.get("ca/canada_workers_benefit_without_dependant")
        is CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT
    )
    assert (
        registry.get("ca/cwb_before_reduction_with_dependant")
        is CWB_BEFORE_REDUCTION_WITH_DEPENDANT
    )
    assert registry.get("ca/cwb_reduction_with_dependant") is CWB_REDUCTION_WITH_DEPENDANT
    assert (
        registry.get("ca/canada_workers_benefit_with_dependant")
        is CANADA_WORKERS_BENEFIT_WITH_DEPENDANT
    )
    assert registry.get("ca/canada_workers_benefit") is CANADA_WORKERS_BENEFIT


def test_the_spouse_inputs_of_schedule_6_are_registered_under_their_form_names(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 38101 "Do you have an eligible spouse? 1 Yes or 2 No", the filer's own
    # answer, and the column 2 ("Your eligible spouse") lines 1, 2 and 3 as caller inputs.
    assert registry.get("ca/cwb_eligible_spouses") is CWB_ELIGIBLE_SPOUSES
    assert registry.get("ca/cwb_spouse_employment_income") is CWB_SPOUSE_EMPLOYMENT_INCOME
    assert registry.get("ca/cwb_spouse_taxable_scholarships") is CWB_SPOUSE_TAXABLE_SCHOLARSHIPS
    assert registry.get("ca/cwb_spouse_self_employment_income") is CWB_SPOUSE_SELF_EMPLOYMENT_INCOME


def test_the_spouse_column_and_secondary_earner_kinds_are_registered(
    registry: ArtifactRegistry,
) -> None:
    assert (
        registry.get("ca/cwb_spouse_working_income_before_eligibility")
        is CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY
    )
    assert registry.get("ca/cwb_spouse_working_income") is CWB_SPOUSE_WORKING_INCOME
    assert (
        registry.get("ca/cwb_spouse_family_net_income_line_10")
        is CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10
    )
    assert registry.get("ca/cwb_spouse_uccb_and_rdsp_income") is CWB_SPOUSE_UCCB_AND_RDSP_INCOME
    assert (
        registry.get("ca/cwb_spouse_family_net_income_line_12_before_eligibility")
        is CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12_BEFORE_ELIGIBILITY
    )
    assert (
        registry.get("ca/cwb_spouse_family_net_income_line_12")
        is CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12
    )
    assert registry.get("ca/cwb_family_working_income") is CWB_FAMILY_WORKING_INCOME
    assert registry.get("ca/cwb_family_net_income_line_13") is CWB_FAMILY_NET_INCOME_LINE_13
    assert registry.get("ca/cwb_working_income_less_spouse") is CWB_WORKING_INCOME_LESS_SPOUSE
    assert registry.get("ca/cwb_secondary_earner_yours") is CWB_SECONDARY_EARNER_YOURS
    assert registry.get("ca/cwb_secondary_earner_spouses") is CWB_SECONDARY_EARNER_SPOUSES
    assert (
        registry.get("ca/cwb_secondary_earner_exemption_before_maximum")
        is CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM
    )
    assert registry.get("ca/cwb_secondary_earner_exemption") is CWB_SECONDARY_EARNER_EXEMPTION


def test_the_line_28_by_spouse_is_registered_and_money(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 28 for the spouse status alone (lines 21 and 24 "eligible spouse"), the
    # first of two choices; the dependant choice then nests over it.
    assert CWB_LINE_28_BY_SPOUSE.value_type is Decimal
    assert CWB_LINE_28_BY_SPOUSE.non_negative is True
    assert registry.get("ca/cwb_line_28_by_spouse") is CWB_LINE_28_BY_SPOUSE
    assert registry.get("ca/canada_workers_benefit_line_28") is CANADA_WORKERS_BENEFIT_LINE_28


def test_the_canada_workers_benefit_kinds_are_money() -> None:
    for kind in (
        CWB_EMPLOYMENT_INCOME,
        WORKING_INCOME,
        CWB_FAMILY_NET_INCOME_LINE_10,
        CWB_FAMILY_NET_INCOME_LINE_12,
        ADJUSTED_FAMILY_NET_INCOME,
        CWB_BEFORE_REDUCTION_WITHOUT_DEPENDANT,
        CWB_REDUCTION_WITHOUT_DEPENDANT,
        CANADA_WORKERS_BENEFIT_WITHOUT_DEPENDANT,
        CWB_BEFORE_REDUCTION_WITH_DEPENDANT,
        CWB_REDUCTION_WITH_DEPENDANT,
        CANADA_WORKERS_BENEFIT_WITH_DEPENDANT,
        CANADA_WORKERS_BENEFIT,
    ):
        assert kind.value_type is Decimal, kind.identifier


def test_the_cwb_eligible_dependants_checked_is_a_non_negative_count(
    registry: ArtifactRegistry,
) -> None:
    # `ca/yes_or_no_count` checks the caller's 0 or 1 before the Canada workers benefit reads it;
    # the raw answer stays beside it.
    assert registry.get("ca/cwb_eligible_dependants_checked") is CWB_ELIGIBLE_DEPENDANTS_CHECKED
    assert registry.get("ca/cwb_eligible_dependants") is CWB_ELIGIBLE_DEPENDANTS
    assert CWB_ELIGIBLE_DEPENDANTS_CHECKED.value_type is int
    assert CWB_ELIGIBLE_DEPENDANTS_CHECKED.non_negative is True


def _kind(registry: ArtifactRegistry, identifier: str) -> ArtifactKind[Any]:
    kind = registry.get(identifier)
    assert isinstance(kind, ArtifactKind), identifier
    return kind


def test_the_eligibility_answers_and_their_checked_kinds_are_non_negative_counts(
    registry: ArtifactRegistry,
) -> None:
    for name in (
        "aged_19_or_older_at_end_of_2025",
        "resided_with_spouse_or_child_at_end_of_2025",
        "full_time_student_for_more_than_13_weeks",
        "confined_to_prison_for_90_days",
        "exempt_as_foreign_officer_or_family",
    ):
        for identifier in (f"ca/{name}", f"ca/{name}_checked"):
            kind = _kind(registry, identifier)
            assert kind.value_type is int, identifier
            assert kind.non_negative is True, identifier
    assert _kind(registry, "ca/cwb_eligible").value_type is int


def test_the_spouse_and_secondary_earner_kinds_have_the_form_types(
    registry: ArtifactRegistry,
) -> None:
    # Money kinds: the spouse's three income lines and the secondary earner exemption (line 14).
    for kind in (
        CWB_SPOUSE_EMPLOYMENT_INCOME,
        CWB_SPOUSE_TAXABLE_SCHOLARSHIPS,
        CWB_SPOUSE_SELF_EMPLOYMENT_INCOME,
        CWB_SPOUSE_WORKING_INCOME_BEFORE_ELIGIBILITY,
        CWB_SPOUSE_WORKING_INCOME,
        CWB_SPOUSE_FAMILY_NET_INCOME_LINE_12,
        CWB_FAMILY_WORKING_INCOME,
        CWB_FAMILY_NET_INCOME_LINE_13,
        CWB_SECONDARY_EARNER_YOURS,
        CWB_SECONDARY_EARNER_SPOUSES,
        CWB_SECONDARY_EARNER_EXEMPTION_BEFORE_MAXIMUM,
        CWB_SECONDARY_EARNER_EXEMPTION,
    ):
        assert kind.value_type is Decimal, kind.identifier
    # Counts: the spouse answer and its checked forms, which the spouse column reads.
    for count in (
        CWB_ELIGIBLE_SPOUSES,
        CWB_ELIGIBLE_SPOUSES_CHECKED,
        CWB_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
    ):
        assert count.value_type is int, count.identifier
        assert count.non_negative is True, count.identifier
    # Signed: the spouse's line 10 and the working income less the spouse's (line 14's sign).
    assert CWB_SPOUSE_FAMILY_NET_INCOME_LINE_10.non_negative is False
    assert CWB_WORKING_INCOME_LESS_SPOUSE.non_negative is False
    assert CWB_WORKING_INCOME_LESS_SPOUSE.value_type is Decimal


def test_the_schedule_6_step_4_lines_are_non_negative_money(registry: ArtifactRegistry) -> None:
    for name in (
        "acwb_paid_to_you",
        "acwb_paid_to_spouse",
        "acwb_disability_supplement_paid",
        "acwb_lines_44_and_45",
        "acwb_basic_paid",
        "acwb_paid",
        "cwb_claimed",
        "canada_workers_benefit_line_28",
    ):
        kind = _kind(registry, f"ca/{name}")
        assert kind.value_type is Decimal, name
        assert kind.non_negative is True, name


def test_the_tax_exempt_income_election_and_its_amounts_are_registered(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 38105, the election, and the amounts of lines 4 and 8 of both columns.
    assert registry.get("ca/cwb_include_tax_exempt_income") is CWB_INCLUDE_TAX_EXEMPT_INCOME
    assert (
        registry.get("ca/cwb_include_tax_exempt_income_checked")
        is CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED
    )
    assert registry.get("ca/cwb_spouse_tax_exempt_working_income") is (
        CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME
    )
    assert registry.get("ca/cwb_spouse_net_exempt_income") is CWB_SPOUSE_NET_EXEMPT_INCOME
    assert registry.get("ca/cwb_tax_exempt_working_income") is CWB_TAX_EXEMPT_WORKING_INCOME
    assert (
        registry.get("ca/cwb_tax_exempt_working_income_before_election")
        is CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION
    )
    assert registry.get("ca/cwb_tax_exempt_net_income") is CWB_TAX_EXEMPT_NET_INCOME
    assert (
        registry.get("ca/cwb_tax_exempt_net_income_before_election")
        is CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION
    )
    assert (
        registry.get("ca/cwb_spouse_tax_exempt_working_income_elected")
        is CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED
    )
    assert (
        registry.get("ca/cwb_spouse_tax_exempt_net_income_elected")
        is CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED
    )


def test_the_election_and_its_check_are_int_counts_and_the_amounts_are_decimals(
    registry: ArtifactRegistry,
) -> None:
    for kind in (CWB_INCLUDE_TAX_EXEMPT_INCOME, CWB_INCLUDE_TAX_EXEMPT_INCOME_CHECKED):
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
    for amount in (
        CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME,
        CWB_TAX_EXEMPT_WORKING_INCOME,
        CWB_TAX_EXEMPT_WORKING_INCOME_BEFORE_ELECTION,
        CWB_SPOUSE_TAX_EXEMPT_WORKING_INCOME_ELECTED,
    ):
        assert amount.value_type is Decimal, amount.identifier
        assert amount.non_negative is True, amount.identifier


def test_the_net_exempt_income_amounts_are_signed_as_the_form_prints_them(
    registry: ArtifactRegistry,
) -> None:
    # Schedule 6 line 8 is the net exempt income, which can be negative (T90 line 20 "show in
    # brackets"), so every amount of line 8 is declared signed.
    for amount in (
        CWB_SPOUSE_NET_EXEMPT_INCOME,
        CWB_TAX_EXEMPT_NET_INCOME,
        CWB_TAX_EXEMPT_NET_INCOME_BEFORE_ELECTION,
        CWB_SPOUSE_TAX_EXEMPT_NET_INCOME_ELECTED,
    ):
        assert amount.value_type is Decimal, amount.identifier
        assert amount.non_negative is False, amount.identifier


def test_the_disability_supplement_kinds_are_the_registered_ones(
    registry: ArtifactRegistry,
) -> None:
    for kind in (
        CANADA_WORKERS_BENEFIT_BEFORE_CONDITIONS,
        CANADA_WORKERS_BENEFIT_LINE_42,
        CWB_DISABILITY_REDUCTION,
        CWB_DISABILITY_REDUCTION_BY_SPOUSE,
        CWB_DISABILITY_REDUCTION_BY_STATUS,
        CWB_DISABILITY_REDUCTION_WITH_DEPENDANT,
        CWB_DISABILITY_REDUCTION_WITH_DTC_SPOUSE,
        CWB_DISABILITY_REDUCTION_WITHOUT_DEPENDANT,
        CWB_DISABILITY_SUPPLEMENT,
        CWB_DISABILITY_SUPPLEMENT_BEFORE_REDUCTION,
        CWB_DTC_SPOUSE_FOR_ELIGIBLE_SPOUSE_CHECKED,
        CWB_CLAIMING_BASIC,
        CWB_CLAIMING_BASIC_CHECKED,
        CWB_SPOUSE_CLAIMING_BASIC,
        CWB_SPOUSE_CLAIMING_BASIC_CHECKED,
        CWB_SPOUSE_CLAIMING_BASIC_WITH_SPOUSE_CHECKED,
        ACWB_LINE_46_APPLIES,
        ACWB_LINES_44_AND_45,
        CANADA_WORKERS_BENEFIT_LINE_41,
        CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC,
        CWB_ELIGIBLE_SPOUSE_ELIGIBLE_FOR_DTC_CHECKED,
    ):
        assert registry.get(kind.identifier) is kind


def test_the_adjusted_family_net_income_is_signed(registry: ArtifactRegistry) -> None:
    # Schedule 6 line 15 "Line 13 minus line 14" prints no "if negative, enter "0"", unlike lines
    # 12, 18 and 25.
    assert ADJUSTED_FAMILY_NET_INCOME.non_negative is False
    assert registry.kind("ca/adjusted_family_net_income").non_negative is False
