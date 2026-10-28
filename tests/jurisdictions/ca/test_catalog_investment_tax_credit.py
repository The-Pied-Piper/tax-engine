"""Registered and money kinds of the federal catalog family `investment_tax_credit`.

Form T2038(IND) Parts A, B, D and E: the caller's lines (67120, 67130, 67135, 67140, 67170, 67175,
the T3 box 40 amount of line 67180, lines 67184 and 67185, and the Part D amounts 1 and 6 and the
claim on amount 15), the credit each one produces, the totals of Parts A and B that Part D reads,
the amounts of Part D that give line 41200, and the amounts of Part E that give line 45400: the
carryback designations (lines 67200, 67210 and 67220), the refund the filer designates (amount 17),
and the refund itself (amount O). The apprentices and their total are the kinds of
`credits_against_federal_tax`, which the family reads.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_calculator.domain.artifact import Artifact, ArtifactKind, ArtifactRegistry
from tax_calculator.domain.errors import NegativeArtifactError
from tax_calculator.jurisdictions.ca.catalog import (
    INVESTMENT_TAX_CREDIT,
    INVESTMENT_TAX_CREDIT_REFUND,
    ITC_AGRICULTURAL_SRED_CONTRIBUTIONS,
    ITC_AGRICULTURAL_SRED_CREDIT,
    ITC_AMOUNT_H,
    ITC_AMOUNT_I,
    ITC_AMOUNT_J,
    ITC_AMOUNT_K,
    ITC_AMOUNT_L,
    ITC_AMOUNT_M,
    ITC_AMOUNT_N,
    ITC_APPRENTICESHIP_CREDIT,
    ITC_APPRENTICESHIP_T3_BOX_40,
    ITC_APPRENTICESHIP_WAGES_WITH_T3,
    ITC_AVAILABLE,
    ITC_CARRYBACK_FIRST_PREVIOUS_YEAR,
    ITC_CARRYBACK_REQUESTED,
    ITC_CARRYBACK_SECOND_PREVIOUS_YEAR,
    ITC_CARRYBACK_THIRD_PREVIOUS_YEAR,
    ITC_CLAIM,
    ITC_CLAIM_LIMIT,
    ITC_CRITICAL_MINERAL_CREDIT,
    ITC_CRITICAL_MINERAL_EXPENDITURES,
    ITC_GRADUATED_RATE_ESTATE_ALLOCATION,
    ITC_MINERAL_EXPLORATION_CREDIT,
    ITC_MINERAL_EXPLORATION_EXPENDITURES,
    ITC_NONREFUNDABLE_CREDITS,
    ITC_OPENING_BALANCE,
    ITC_PART_D_AMOUNT_5,
    ITC_PART_D_AMOUNT_9,
    ITC_PART_D_AMOUNT_11_APPLIES,
    ITC_PART_D_AMOUNT_13,
    ITC_PART_D_SUBTOTAL,
    ITC_PART_E_AMOUNT_3,
    ITC_PART_E_AMOUNT_6,
    ITC_PART_E_AMOUNT_9,
    ITC_PART_E_AMOUNT_12,
    ITC_PART_E_AMOUNT_14,
    ITC_PART_E_AMOUNT_16,
    ITC_PART_E_AMOUNT_17,
    ITC_QUALIFIED_PROPERTY,
    ITC_QUALIFIED_PROPERTY_CREDIT,
    ITC_REFUND_DESIGNATION,
    ITC_REFUNDABLE_CREDITS,
    ITC_SRED_CREDIT,
    ITC_SRED_EXPENDITURES,
    ITC_SRED_PARTNERSHIP_ALLOCATION,
    ITC_SRED_REPAYMENT_2014_AND_PRIOR,
    ITC_SRED_REPAYMENT_2015_AND_AFTER,
    ITC_SRED_REPAYMENT_CREDIT,
    ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR,
    ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER,
)

# The caller's lines, as the form takes them: line 67120 (Part A, amount 1), 67130 (amount 2),
# 67135 (amount 3), 67140 (amount 4), 67170 (Part B, amount B), 67175 (amount C), the T3 box 40
# amount of line 67180 (amount D), and lines 67184 and 67185 (Part B repayments 1 and 2).
CALLER_LINES: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_sred_expenditures", ITC_SRED_EXPENDITURES),
    ("ca/itc_agricultural_sred_contributions", ITC_AGRICULTURAL_SRED_CONTRIBUTIONS),
    ("ca/itc_sred_partnership_allocation", ITC_SRED_PARTNERSHIP_ALLOCATION),
    ("ca/itc_qualified_property", ITC_QUALIFIED_PROPERTY),
    ("ca/itc_mineral_exploration_expenditures", ITC_MINERAL_EXPLORATION_EXPENDITURES),
    ("ca/itc_critical_mineral_expenditures", ITC_CRITICAL_MINERAL_EXPENDITURES),
    ("ca/itc_apprenticeship_t3_box_40", ITC_APPRENTICESHIP_T3_BOX_40),
    ("ca/itc_sred_repayment_2014_and_prior", ITC_SRED_REPAYMENT_2014_AND_PRIOR),
    ("ca/itc_sred_repayment_2015_and_after", ITC_SRED_REPAYMENT_2015_AND_AFTER),
)

# The credits each line produces at its rate (amounts 1, 2, 4, B, C, D, the two repayments and
# E), and the sums that are not outputs (the total of line 67180 with the T3 box 40 amount, and E).
CREDITS: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_sred_credit", ITC_SRED_CREDIT),
    ("ca/itc_agricultural_sred_credit", ITC_AGRICULTURAL_SRED_CREDIT),
    ("ca/itc_qualified_property_credit", ITC_QUALIFIED_PROPERTY_CREDIT),
    ("ca/itc_mineral_exploration_credit", ITC_MINERAL_EXPLORATION_CREDIT),
    ("ca/itc_critical_mineral_credit", ITC_CRITICAL_MINERAL_CREDIT),
    ("ca/itc_apprenticeship_wages_with_t3", ITC_APPRENTICESHIP_WAGES_WITH_T3),
    ("ca/itc_apprenticeship_credit", ITC_APPRENTICESHIP_CREDIT),
    ("ca/itc_sred_repayment_credit_2014_and_prior", ITC_SRED_REPAYMENT_CREDIT_2014_AND_PRIOR),
    ("ca/itc_sred_repayment_credit_2015_and_after", ITC_SRED_REPAYMENT_CREDIT_2015_AND_AFTER),
    ("ca/itc_sred_repayment_credit", ITC_SRED_REPAYMENT_CREDIT),
)

# The two totals of Parts A and B: Part A amount A "Total current-year refundable credits (add
# amounts 1 to 4)" and Part B amount F "Total current-year non-refundable tax credits (add amounts
# B, C, D and E)". They are not declared outputs: Part D reads them ("Current-year refundable tax
# credit (amount A in Part A)" at amount 2, and "Current-year non-refundable tax credit (amount F in
# Part B)" at amount 3).
TOTALS: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_refundable_credits", ITC_REFUNDABLE_CREDITS),
    ("ca/itc_nonrefundable_credits", ITC_NONREFUNDABLE_CREDITS),
)

# The Part D caller's lines, from Form T2038(IND) Part D (`docs/cra-forms-2025/t2038-ind-25e.pdf`,
# confirmed from the PDF; no .txt published): amount 1, "ITC opening balance and carry forward
# from prior years (net of expired amounts)"; amount 6, "Adjustment for a graduated rate estate,
# enter the amount of ITC allocated to beneficiaries from box 40 of your T3 slip."; and amount 15,
# "Enter your claim on this line:", the claim the filer chooses (an election, never negative).
PART_D_CALLER_LINES: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_opening_balance", ITC_OPENING_BALANCE),
    ("ca/itc_graduated_rate_estate_allocation", ITC_GRADUATED_RATE_ESTATE_ALLOCATION),
    ("ca/itc_claim", ITC_CLAIM),
)

# The Part D amounts that are never negative: amount 4 "Subtotal (add amounts 2 and 3)", amount 5
# "Amount 1 plus amount 4", amount 9 and H (each "Subtotal ... if negative, enter "0""), amount 13
# "Subtotal (add amounts 11 and 12)", amount J ("if negative, enter "0""), and amount 15, the
# claim up to the limit, which is the line 41200 figure of the return.
PART_D_AMOUNTS: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_part_d_subtotal", ITC_PART_D_SUBTOTAL),
    ("ca/itc_part_d_amount_5", ITC_PART_D_AMOUNT_5),
    ("ca/itc_part_d_amount_9", ITC_PART_D_AMOUNT_9),
    ("ca/itc_amount_h", ITC_AMOUNT_H),
    ("ca/itc_part_d_amount_13", ITC_PART_D_AMOUNT_13),
    ("ca/itc_amount_j", ITC_AMOUNT_J),
    ("ca/investment_tax_credit", INVESTMENT_TAX_CREDIT),
)

# The Part D amounts that take the sign of their inputs: G, "Total available investment tax credit
# (amount 5 minus amount 6)", has no floor printed on the form; I and K are the lesser of G and
# another amount, and the claim limit is one of them, so they take its sign too.
PART_D_SIGNED: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_available", ITC_AVAILABLE),
    ("ca/itc_amount_i", ITC_AMOUNT_I),
    ("ca/itc_amount_k", ITC_AMOUNT_K),
    ("ca/itc_claim_limit", ITC_CLAIM_LIMIT),
)

# The count of the condition "T691 Part 5 line 7 is greater than 0", which decides whether Part D
# continues at amount 11 (1) or at amount 15 (0).
PART_D_COUNT: tuple[tuple[str, ArtifactKind[int]], ...] = (
    ("ca/itc_part_d_amount_11_applies", ITC_PART_D_AMOUNT_11_APPLIES),
)


def test_the_caller_lines_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in CALLER_LINES:
        assert registry.get(identifier) is kind, identifier


def test_the_credits_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in CREDITS:
        assert registry.get(identifier) is kind, identifier


def test_the_totals_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in TOTALS:
        assert registry.get(identifier) is kind, identifier


def test_the_part_d_caller_lines_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_D_CALLER_LINES:
        assert registry.get(identifier) is kind, identifier


def test_the_part_d_amounts_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_D_AMOUNTS:
        assert registry.get(identifier) is kind, identifier


def test_the_part_d_signed_amounts_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_D_SIGNED:
        assert registry.get(identifier) is kind, identifier


def test_the_part_d_count_is_the_registered_int_kind(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_D_COUNT:
        assert registry.get(identifier) is kind, identifier
        assert kind.value_type is int, identifier
        assert kind.non_negative is True, identifier


def test_the_investment_tax_credit_is_the_line_136_kind() -> None:
    # T1 line 136 (line 41200) "Investment tax credit (complete Form T2038(IND))": amount 15 of Part
    # D, the claim up to the limit, is the figure of the return's line 136.
    assert INVESTMENT_TAX_CREDIT.identifier == "ca/investment_tax_credit"
    assert INVESTMENT_TAX_CREDIT.value_type is Decimal


@pytest.mark.parametrize(
    ("identifier", "kind"),
    CALLER_LINES + CREDITS + TOTALS + PART_D_CALLER_LINES + PART_D_AMOUNTS,
    ids=[
        identifier
        for identifier, _ in CALLER_LINES + CREDITS + TOTALS + PART_D_CALLER_LINES + PART_D_AMOUNTS
    ],
)
def test_every_kind_is_a_non_negative_money_kind(
    identifier: str, kind: ArtifactKind[Decimal]
) -> None:
    # No line of Parts A, B and D can be negative on the form as modelled: each is an amount the
    # caller enters, a credit at a rate, a sum of such amounts, or a subtotal the form floors at 0.
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is True


@pytest.mark.parametrize(
    ("identifier", "kind"),
    PART_D_SIGNED,
    ids=[identifier for identifier, _ in PART_D_SIGNED],
)
def test_the_signed_part_d_amounts_are_money_not_declared_non_negative(
    identifier: str, kind: ArtifactKind[Decimal]
) -> None:
    # Amount G is "amount 5 minus amount 6" with no floor printed on the form, so it is not floored
    # and the kinds that take its sign (I, K and the claim limit) are not declared non-negative.
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is False


def test_the_total_available_credit_is_not_floored_at_zero(registry: ArtifactRegistry) -> None:
    # G "Total available investment tax credit (amount 5 minus amount 6)": a negative figure is held
    # as it is, not taken as 0.
    assert Artifact(ITC_AVAILABLE, Decimal("-1")).value == Decimal("-1")
    assert registry.get("ca/itc_available") is ITC_AVAILABLE


def test_a_negative_caller_line_is_refused() -> None:
    # Line 67120 "ITC for qualified expenditures for SR&ED": an amount, never negative.
    with pytest.raises(NegativeArtifactError):
        Artifact(ITC_SRED_EXPENDITURES, Decimal("-1"))


def test_a_negative_part_d_opening_balance_is_refused() -> None:
    # Part D amount 1, "ITC opening balance and carry forward from prior years (net of expired
    # amounts)": a balance carried forward, never negative.
    with pytest.raises(NegativeArtifactError, match="ca/itc_opening_balance cannot be negative"):
        Artifact(ITC_OPENING_BALANCE, Decimal("-1"))


def test_a_negative_claim_is_refused() -> None:
    # Part D amount 15, "Enter your claim on this line:": the credit the filer claims, never
    # negative, so a negative figure is an input error and not taken as 0.
    with pytest.raises(NegativeArtifactError, match="ca/itc_claim cannot be negative"):
        Artifact(ITC_CLAIM, Decimal("-1"))


def test_a_credit_holds_its_amount_to_the_cent() -> None:
    # Amount 4 of Part A, "ITC for total investments in qualified property" at 10%: 10,000.00 x
    # 0.10 is 1,000.00, and the credit holds that amount.
    assert Artifact(ITC_QUALIFIED_PROPERTY_CREDIT, Decimal("1000.00")).value == Decimal("1000.00")


# The Part E caller's lines, as the form takes them: lines 67200, 67210 and 67220, "Third previous
# year", "Second previous year" and "First previous year", the part of amount L to carry back to
# each of the three previous years, and amount 17, "Amount you designate as a refund of ITC (cannot
# be more than amount N)", the refund the filer chooses. They are elections, never negative.
PART_E_CALLER_LINES: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_carryback_third_previous_year", ITC_CARRYBACK_THIRD_PREVIOUS_YEAR),
    ("ca/itc_carryback_second_previous_year", ITC_CARRYBACK_SECOND_PREVIOUS_YEAR),
    ("ca/itc_carryback_first_previous_year", ITC_CARRYBACK_FIRST_PREVIOUS_YEAR),
    ("ca/itc_refund_designation", ITC_REFUND_DESIGNATION),
)

# The Part E amounts that are never negative: amount 6 "Subtotal (amount 4 minus amount 5, if
# negative enter "0")", amount M "Total credit designated for carryback" (the requested total, which
# cannot be more than amount L), amount 16 "Total (amount 14 minus amount 15, if negative, enter
# "0")", amount 17 (which cannot be more than amount N), and the refund of line 45400, amount O.
PART_E_AMOUNTS: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_part_e_amount_6", ITC_PART_E_AMOUNT_6),
    ("ca/itc_carryback_requested", ITC_CARRYBACK_REQUESTED),
    ("ca/itc_amount_m", ITC_AMOUNT_M),
    ("ca/itc_part_e_amount_16", ITC_PART_E_AMOUNT_16),
    ("ca/itc_part_e_amount_17", ITC_PART_E_AMOUNT_17),
    ("ca/investment_tax_credit_refund", INVESTMENT_TAX_CREDIT_REFUND),
)

# The Part E amounts that take the sign of their inputs. The form prints no floor on amount 3
# ("Subtotal (amount 1 minus amount 2)"), amount L ("amount 3 minus amount 6"), amount 9 ("amount 7
# minus amount 8"), amount 12 ("amount 10 minus amount 11"), amount 14 ("amount 12 plus amount 13")
# and amount N ("amount 9 minus amount 16"); each can be negative when its inputs are.
PART_E_SIGNED: tuple[tuple[str, ArtifactKind[Decimal]], ...] = (
    ("ca/itc_part_e_amount_3", ITC_PART_E_AMOUNT_3),
    ("ca/itc_amount_l", ITC_AMOUNT_L),
    ("ca/itc_part_e_amount_9", ITC_PART_E_AMOUNT_9),
    ("ca/itc_part_e_amount_12", ITC_PART_E_AMOUNT_12),
    ("ca/itc_part_e_amount_14", ITC_PART_E_AMOUNT_14),
    ("ca/itc_amount_n", ITC_AMOUNT_N),
)


def test_the_part_e_caller_lines_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_E_CALLER_LINES:
        assert registry.get(identifier) is kind, identifier


def test_the_part_e_amounts_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_E_AMOUNTS:
        assert registry.get(identifier) is kind, identifier


def test_the_part_e_signed_amounts_are_the_registered_kinds(registry: ArtifactRegistry) -> None:
    for identifier, kind in PART_E_SIGNED:
        assert registry.get(identifier) is kind, identifier


@pytest.mark.parametrize(
    ("identifier", "kind"),
    PART_E_CALLER_LINES + PART_E_AMOUNTS,
    ids=[identifier for identifier, _ in PART_E_CALLER_LINES + PART_E_AMOUNTS],
)
def test_every_part_e_non_negative_kind_is_a_non_negative_money_kind(
    identifier: str, kind: ArtifactKind[Decimal]
) -> None:
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is True


@pytest.mark.parametrize(
    ("identifier", "kind"),
    PART_E_SIGNED,
    ids=[identifier for identifier, _ in PART_E_SIGNED],
)
def test_the_signed_part_e_amounts_are_money_not_declared_non_negative(
    identifier: str, kind: ArtifactKind[Decimal]
) -> None:
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert kind.non_negative is False


def test_the_refund_is_the_line_45400_kind() -> None:
    # T1 line 45400 "Refund of investment tax credit (complete Form T2038(IND))": amount O of Part
    # E, "Refund of ITC (multiply amount 17 by amount 18)", is the return's figure on line 45400.
    assert INVESTMENT_TAX_CREDIT_REFUND.identifier == "ca/investment_tax_credit_refund"
    assert INVESTMENT_TAX_CREDIT_REFUND.value_type is Decimal


def test_a_negative_carryback_designation_is_refused() -> None:
    # Line 67200, "Third previous year", an amount of the part of amount L to carry back: never
    # negative, so a negative figure is an input error and not taken as 0.
    with pytest.raises(
        NegativeArtifactError, match="ca/itc_carryback_third_previous_year cannot be negative"
    ):
        Artifact(ITC_CARRYBACK_THIRD_PREVIOUS_YEAR, Decimal("-1"))


def test_a_negative_refund_designation_is_refused() -> None:
    # Part E amount 17, "Amount you designate as a refund of ITC (cannot be more than amount N)":
    # an election, never negative.
    with pytest.raises(NegativeArtifactError, match="ca/itc_refund_designation cannot be negative"):
        Artifact(ITC_REFUND_DESIGNATION, Decimal("-1"))


def test_part_e_amount_3_holds_a_negative_figure_as_the_form_prints_no_floor() -> None:
    # Amount 3, "Subtotal (amount 1 minus amount 2)": no "if negative, enter 0" is printed, so a
    # negative figure is held as it is.
    assert Artifact(ITC_PART_E_AMOUNT_3, Decimal("-1")).value == Decimal("-1")
