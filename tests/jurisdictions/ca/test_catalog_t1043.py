"""Registered kinds of Form T1043 "Deduction for Excess Registered Pension Plan Transfers You
Withdrew from an RRSP, a PRPP, an SPP, or a RRIF", in the federal catalog family `t1043`
(`tax_engine/jurisdictions/ca/catalog/t1043.py`).

The form `ca/t1043` runs once: the six amounts the filer enters (lines 1, 2, 3, 6 and 7), the lines
it computes and the deduction on the return are registered together.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.jurisdictions.ca.catalog import (
    T1043_CLAIMED_AS_RRSP_DEDUCTION,
    T1043_DEDUCTED_USING_FORM,
    T1043_DEDUCTION,
    T1043_DEDUCTION_ON_RETURN,
    T1043_EXCESS_AMOUNT_ON_RECEIPT,
    T1043_EXCESS_TRANSFER_ON_T4A,
    T1043_EXCESS_TRANSFERRED,
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED,
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED,
    T1043_LINE_9,
    T1043_LINE_9_IF_EXCESS_INCLUDED,
    T1043_NOT_YET_CLAIMED,
    T1043_PART_DEDUCTIBLE_ELSEWHERE,
    T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED,
    T1043_PLAN_AMOUNTS_IN_INCOME,
    T1043_PLAN_AMOUNTS_REMAINING,
    T1043_PREVIOUSLY_CLAIMED,
    T1043_PREVIOUSLY_CLAIMED_CHECKED,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The amounts the filer enters, non-negative.
AMOUNT_INPUTS: tuple[ArtifactKind[Decimal], ...] = (
    T1043_EXCESS_TRANSFER_ON_T4A,
    T1043_EXCESS_AMOUNT_ON_RECEIPT,
    T1043_CLAIMED_AS_RRSP_DEDUCTION,
    T1043_DEDUCTED_USING_FORM,
    T1043_PLAN_AMOUNTS_IN_INCOME,
    T1043_PART_DEDUCTIBLE_ELSEWHERE,
)
# The yes or no answers the filer enters (counts of 1 or 0), and the same answers once checked.
ANSWER_INPUTS: tuple[ArtifactKind[int], ...] = (
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED,
)
CHECKED_ANSWERS: tuple[ArtifactKind[int], ...] = (
    T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED_CHECKED,
    T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED_CHECKED,
)
# The computed amounts, none of them signed: no line of the form shows a negative.
COMPUTED: tuple[ArtifactKind[Decimal], ...] = (
    T1043_EXCESS_TRANSFERRED,
    T1043_PREVIOUSLY_CLAIMED,
    T1043_PREVIOUSLY_CLAIMED_CHECKED,
    T1043_NOT_YET_CLAIMED,
    T1043_PART_DEDUCTIBLE_ELSEWHERE_CHECKED,
    T1043_PLAN_AMOUNTS_REMAINING,
    T1043_LINE_9,
    T1043_LINE_9_IF_EXCESS_INCLUDED,
    T1043_DEDUCTION,
    T1043_DEDUCTION_ON_RETURN,
)
ALL_KINDS: tuple[ArtifactKind[Decimal], ...] = (*AMOUNT_INPUTS, *COMPUTED)
ALL_ANSWERS: tuple[ArtifactKind[int], ...] = (*ANSWER_INPUTS, *CHECKED_ANSWERS)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            constants = [
                each.value for each in statement.value.args if isinstance(each, ast.Constant)
            ]
            if not (
                identifier.rpartition("/")[2] in constants
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def test_the_t1043_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t1043_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_amounts_are_non_negative_decimals() -> None:
    for kind in ALL_KINDS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_amounts_are_neither_counts_nor_record_lists() -> None:
    for kind in ALL_KINDS:
        assert kind.identifier not in COUNTS | RECORD_LISTS, kind.identifier


def test_the_identifiers_are_the_stable_names_of_the_lines() -> None:
    assert {kind.identifier for kind in ALL_KINDS} == {
        "ca/t1043_excess_transfer_on_t4a",
        "ca/t1043_excess_amount_on_receipt",
        "ca/t1043_excess_transferred",
        "ca/t1043_claimed_as_rrsp_deduction",
        "ca/t1043_deducted_using_form",
        "ca/t1043_previously_claimed",
        "ca/t1043_previously_claimed_checked",
        "ca/t1043_not_yet_claimed",
        "ca/t1043_plan_amounts_in_income",
        "ca/t1043_part_deductible_elsewhere",
        "ca/t1043_part_deductible_elsewhere_checked",
        "ca/t1043_plan_amounts_remaining",
        "ca/t1043_line_9",
        "ca/t1043_line_9_if_excess_included",
        "ca/t1043_deduction",
        "ca/t1043_deduction_on_return",
    }


def test_the_two_conditions_are_yes_or_no_counts_named_by_their_printed_sentences() -> None:
    assert {kind.identifier for kind in ALL_ANSWERS} == {
        "ca/t1043_included_excess_in_income_for_year_transferred",
        "ca/t1043_included_excess_in_income_for_year_transferred_checked",
        "ca/t1043_including_plan_amounts_in_income_for_year_claimed",
        "ca/t1043_including_plan_amounts_in_income_for_year_claimed_checked",
    }
    for kind in ALL_ANSWERS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
        assert "T1043" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_two_conditions_quote_the_sentences_the_form_prints() -> None:
    quotes = {
        T1043_INCLUDED_EXCESS_IN_INCOME_FOR_YEAR_TRANSFERRED: (
            "You included the excess amount that was transferred to your RRSP, PRPP, SPP, or "
            "RRIF in your income for the year it was transferred"
        ),
        T1043_INCLUDING_PLAN_AMOUNTS_IN_INCOME_FOR_YEAR_CLAIMED: (
            "You are including amounts received from your RRSPs, PRPPs, SPP, or RRIFs in your "
            "income for the year you are claiming this deduction"
        ),
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier


def test_each_t1043_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T1043" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_lines_quote_their_printed_words() -> None:
    quotes: dict[ArtifactKind[Decimal], str] = {
        T1043_EXCESS_TRANSFER_ON_T4A: "excess transfer shown on your T4A slip(s)",
        T1043_EXCESS_AMOUNT_ON_RECEIPT: "excess amount shown on your RRSP, PRPP, or SPP receipt",
        T1043_EXCESS_TRANSFERRED: "whichever is less",
        T1043_CLAIMED_AS_RRSP_DEDUCTION: "claimed as an RRSP deduction for any previous year",
        T1043_DEDUCTED_USING_FORM: "deducted using this form for any previous year",
        T1043_PREVIOUSLY_CLAIMED: "Line 2 plus line 3",
        T1043_NOT_YET_CLAIMED: "Line 1 minus line 4",
        T1043_PLAN_AMOUNTS_IN_INCOME: "included in your income for the current tax year",
        T1043_PART_DEDUCTIBLE_ELSEWHERE: "transfer after the maturity of an RRSP",
        T1043_PLAN_AMOUNTS_REMAINING: "Line 6 minus line 7",
        T1043_LINE_9: "whichever is less",
        T1043_LINE_9_IF_EXCESS_INCLUDED: "included the excess amount that was transferred",
        T1043_DEDUCTION: "both of the following conditions",
        T1043_DEDUCTION_ON_RETURN: "line 23200",
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier
