"""Registered kinds of Form T746 "Calculating Your Deduction for Refund of Unused RRSP, PRPP, and
SPP Contributions", in the federal catalog family `t746`
(`tax_engine/jurisdictions/ca/catalog/t746.py`).

The row form `ca/t746_year` is lines 1 to 4 for one year (the record list `ca/t746_years`); the
summary form `ca/t746` runs once and gives line 13. The kinds of line 12 and of the deduction on
the return are registered beside them.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca.catalog
from tax_engine.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_engine.domain.record_list import RecordListKind
from tax_engine.jurisdictions.ca.catalog import (
    T746_CONDITIONS_MET,
    T746_CONTRIBUTION_YEAR,
    T746_CONTRIBUTIONS,
    T746_CONTRIBUTIONS_DEDUCTED,
    T746_CONTRIBUTIONS_DEDUCTED_CHECKED,
    T746_DEDUCTION,
    T746_DEDUCTION_ON_RETURN,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED,
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS,
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED,
    T746_LINE_13,
    T746_T4A_BOX_18_SPP,
    T746_T4A_BOX_194,
    T746_T4RIF_BOX_24,
    T746_T4RSP_BOX_20,
    T746_T4RSP_BOX_22,
    T746_UNUSED_CONTRIBUTIONS,
    T746_UNUSED_CONTRIBUTIONS_OF_YEAR,
    T746_WITHDRAWAL_YEAR,
    T746_WITHDRAWALS,
    T746_YEARS,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The amounts the filer enters: lines 2 and 3 of each year and lines 6 to 10, non-negative.
AMOUNT_INPUTS: tuple[ArtifactKind[Decimal], ...] = (
    T746_CONTRIBUTIONS,
    T746_CONTRIBUTIONS_DEDUCTED,
    T746_T4RSP_BOX_20,
    T746_T4RSP_BOX_22,
    T746_T4RIF_BOX_24,
    T746_T4A_BOX_194,
    T746_T4A_BOX_18_SPP,
)
# The years of lines 1 and 5, entered as whole numbers.
YEAR_INPUTS: tuple[ArtifactKind[int], ...] = (T746_CONTRIBUTION_YEAR, T746_WITHDRAWAL_YEAR)
# The filer's yes or no answers to the two conditions, and the counts computed from them (1 or 0).
ANSWER_INPUTS: tuple[ArtifactKind[int], ...] = (
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW,
)
ANSWER_COUNTS: tuple[ArtifactKind[int], ...] = (
    *ANSWER_INPUTS,
    T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS_CHECKED,
    T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW_CHECKED,
    T746_CONDITIONS_MET,
)
# The computed amounts, none of them signed: no line of the form shows a negative.
COMPUTED: tuple[ArtifactKind[Decimal], ...] = (
    T746_CONTRIBUTIONS_DEDUCTED_CHECKED,
    T746_UNUSED_CONTRIBUTIONS_OF_YEAR,
    T746_UNUSED_CONTRIBUTIONS,
    T746_WITHDRAWALS,
    T746_LINE_13,
    T746_DEDUCTION,
    T746_DEDUCTION_ON_RETURN,
)
ALL_KINDS: tuple[ArtifactKind[Any], ...] = (
    *AMOUNT_INPUTS,
    *YEAR_INPUTS,
    *ANSWER_COUNTS,
    *COMPUTED,
    T746_YEARS,
)


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


def test_the_t746_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t746_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_amounts_are_non_negative_decimals() -> None:
    for kind in (*AMOUNT_INPUTS, *COMPUTED):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_years_are_non_negative_whole_numbers() -> None:
    for kind in YEAR_INPUTS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_years_list_holds_lines_1_to_3_of_the_row_form() -> None:
    assert isinstance(T746_YEARS, RecordListKind)
    assert T746_YEARS.identifier == "ca/t746_years"
    assert T746_YEARS.fields == (
        T746_CONTRIBUTION_YEAR,
        T746_CONTRIBUTIONS,
        T746_CONTRIBUTIONS_DEDUCTED,
    )
    assert T746_YEARS.identifier in RECORD_LISTS


def test_the_two_years_are_counts_and_the_amounts_are_neither_counts_nor_record_lists() -> None:
    for year in YEAR_INPUTS:
        assert year.identifier in COUNTS, year.identifier
    for amount in (*AMOUNT_INPUTS, *COMPUTED):
        assert amount.identifier not in COUNTS | RECORD_LISTS, amount.identifier


def test_the_conditions_are_counts_of_1_or_0() -> None:
    for kind in ANSWER_COUNTS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier


def test_the_identifiers_are_the_stable_names_of_the_lines() -> None:
    assert {kind.identifier for kind in ALL_KINDS} == {
        "ca/t746_contribution_year",
        "ca/t746_contributions",
        "ca/t746_contributions_deducted",
        "ca/t746_contributions_deducted_checked",
        "ca/t746_unused_contributions_of_year",
        "ca/t746_years",
        "ca/t746_unused_contributions",
        "ca/t746_withdrawal_year",
        "ca/t746_t4rsp_box_20",
        "ca/t746_t4rsp_box_22",
        "ca/t746_t4rif_box_24",
        "ca/t746_t4a_box_194",
        "ca/t746_t4a_box_18_spp",
        "ca/t746_withdrawals",
        "ca/t746_expected_to_fully_deduct_contributions",
        "ca/t746_did_not_make_contributions_intending_to_withdraw",
        "ca/t746_expected_to_fully_deduct_contributions_checked",
        "ca/t746_did_not_make_contributions_intending_to_withdraw_checked",
        "ca/t746_conditions_met",
        "ca/t746_line_13",
        "ca/t746_deduction",
        "ca/t746_deduction_on_return",
    }


def test_each_t746_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T746" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_lines_quote_their_printed_words() -> None:
    quotes: dict[ArtifactKind[Any], str] = {
        T746_CONTRIBUTION_YEAR: "Enter the year you made the unused RRSP, PRPP, and SPP",
        T746_CONTRIBUTIONS: "Enter the total contributions you made to your RRSPs, PRPPs, or SPP",
        T746_CONTRIBUTIONS_DEDUCTED: "Enter the part of the amount from line 2 that you deducted",
        T746_UNUSED_CONTRIBUTIONS_OF_YEAR: "Line 2 minus line 3",
        T746_UNUSED_CONTRIBUTIONS: "enter the total of the amounts from line 4 for all years",
        T746_WITHDRAWAL_YEAR: "Enter the year you or your spouse or common-law partner withdrew",
        T746_T4RSP_BOX_20: "Enter the amount shown in box 20 of your T4RSP slips",
        T746_T4RSP_BOX_22: "Enter the amount shown in box 22 of your T4RSP slips",
        T746_T4RIF_BOX_24: "Enter the amount shown in box 24 of your T4RIF slips",
        T746_T4A_BOX_194: "lump sum PRPP withdrawals included in box 194 of your T4A slips",
        T746_T4A_BOX_18_SPP: "box 18 of your T4A slips only if this amount is a withdrawal",
        T746_WITHDRAWALS: "Add lines 6 to 11",
        T746_LINE_13: "whichever is less",
        T746_DEDUCTION: "This is your deduction",
        T746_EXPECTED_TO_FULLY_DEDUCT_CONTRIBUTIONS: (
            "you expected to be able to fully deduct your RRSP, PRPP, or SPP contributions"
        ),
        T746_DID_NOT_MAKE_CONTRIBUTIONS_INTENDING_TO_WITHDRAW: (
            "you did not make the contributions intending to withdraw them later"
        ),
        T746_DEDUCTION_ON_RETURN: "line 23200",
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier
