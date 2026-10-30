"""Registered kinds of Form T1139 "Reconciliation of 2025 Business Income for Tax Purposes", in the
federal catalog family `t1139` (`tax_engine/jurisdictions/ca/catalog/t1139.py`).

The row form `ca/t1139` is the form for one business (the record list `ca/t1139_businesses`); the
summary form `ca/t1139_return` runs once and gives the net income of each of the lines 13500, 13700,
13900, 14100 and 14300 of the return. The statements of amounts A, H and I are record lists of the
positions of the statements.
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
    T1139_A_STATEMENTS,
    T1139_AMOUNT_2A,
    T1139_AMOUNT_2B,
    T1139_AMOUNT_2C,
    T1139_AMOUNT_2D,
    T1139_AMOUNT_2E,
    T1139_AMOUNT_2F,
    T1139_AMOUNT_2H,
    T1139_AMOUNT_2I,
    T1139_AMOUNT_2J,
    T1139_AMOUNT_2K,
    T1139_AMOUNT_2L,
    T1139_AMOUNT_2M,
    T1139_AMOUNT_2N,
    T1139_AMOUNT_3A,
    T1139_AMOUNT_3B,
    T1139_AMOUNT_3C,
    T1139_AMOUNT_3D,
    T1139_AMOUNT_3E,
    T1139_AMOUNT_3F,
    T1139_AMOUNT_3H,
    T1139_AMOUNT_3H_CHOSEN,
    T1139_AMOUNT_A,
    T1139_AMOUNT_B,
    T1139_AMOUNT_B_CHOSEN,
    T1139_AMOUNT_C,
    T1139_AMOUNT_C_CHOSEN,
    T1139_AMOUNT_D,
    T1139_AMOUNT_E,
    T1139_AMOUNT_G,
    T1139_AMOUNT_H,
    T1139_AMOUNT_I,
    T1139_AMOUNT_J,
    T1139_AMOUNT_L,
    T1139_BUSINESS_INCOME_ON_RETURN,
    T1139_BUSINESS_PROFIT_ON_RETURN,
    T1139_BUSINESSES,
    T1139_CANCELLING_ELECTION,
    T1139_CANCELLING_ELECTION_CHECKED,
    T1139_COMMISSION_INCOME_ON_RETURN,
    T1139_COMMISSION_PROFIT_ON_RETURN,
    T1139_DESIGNATED_AMOUNT,
    T1139_DESIGNATED_OR_FORMULA_AMOUNT,
    T1139_DESIGNATES_AMOUNT,
    T1139_DESIGNATES_AMOUNT_CHECKED,
    T1139_FARMING_INCOME_ON_RETURN,
    T1139_FARMING_PROFIT_ON_RETURN,
    T1139_FISHING_INCOME_ON_RETURN,
    T1139_FISHING_PROFIT_ON_RETURN,
    T1139_FORMULA,
    T1139_FORMULA_AMOUNT_FOR_C,
    T1139_FORMULA_CHECKED,
    T1139_FORMULA_IS_3H,
    T1139_FORMULA_IS_B,
    T1139_FORMULA_IS_C,
    T1139_H_STATEMENTS,
    T1139_I_STATEMENTS,
    T1139_KEPT_ON_BUSINESS_LINE,
    T1139_KEPT_ON_COMMISSION_LINE,
    T1139_KEPT_ON_FARMING_LINE,
    T1139_KEPT_ON_FISHING_LINE,
    T1139_KEPT_ON_PROFESSIONAL_LINE,
    T1139_KEPT_PROFITS_ON_BUSINESS_LINE,
    T1139_KEPT_PROFITS_ON_COMMISSION_LINE,
    T1139_KEPT_PROFITS_ON_FARMING_LINE,
    T1139_KEPT_PROFITS_ON_FISHING_LINE,
    T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_LAST_YEARS_ADDITIONAL_INCOME,
    T1139_LINE,
    T1139_LINE_CHECKED,
    T1139_NET_INCOME_REPLACED,
    T1139_NET_INCOME_REPORTED,
    T1139_ON_BUSINESS_LINE,
    T1139_ON_COMMISSION_LINE,
    T1139_ON_FARMING_LINE,
    T1139_ON_FISHING_LINE,
    T1139_ON_PROFESSIONAL_LINE,
    T1139_PROFESSIONAL_INCOME_ON_RETURN,
    T1139_PROFESSIONAL_PROFIT_ON_RETURN,
    T1139_PROFIT_A,
    T1139_PROFIT_H,
    T1139_PROFIT_HI,
    T1139_PROFIT_I,
    T1139_PROFIT_REPLACED,
    T1139_PROFIT_REPLACED_ON_BUSINESS_LINE,
    T1139_PROFIT_REPLACED_ON_COMMISSION_LINE,
    T1139_PROFIT_REPLACED_ON_FARMING_LINE,
    T1139_PROFIT_REPLACED_ON_FISHING_LINE,
    T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_ON_BUSINESS_LINE,
    T1139_REPLACED_ON_COMMISSION_LINE,
    T1139_REPLACED_ON_FARMING_LINE,
    T1139_REPLACED_ON_FISHING_LINE,
    T1139_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_TOTAL_ON_BUSINESS_LINE,
    T1139_REPLACED_TOTAL_ON_COMMISSION_LINE,
    T1139_REPLACED_TOTAL_ON_FARMING_LINE,
    T1139_REPLACED_TOTAL_ON_FISHING_LINE,
    T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_ON_BUSINESS_LINE,
    T1139_REPORTED_ON_COMMISSION_LINE,
    T1139_REPORTED_ON_FARMING_LINE,
    T1139_REPORTED_ON_FISHING_LINE,
    T1139_REPORTED_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_STATEMENT_NUMBER,
    T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE,
    T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE,
    T1139_STATEMENT_PROFITS_ON_FARMING_LINE,
    T1139_STATEMENT_PROFITS_ON_FISHING_LINE,
    T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_STATEMENTS_ON_BUSINESS_LINE,
    T1139_STATEMENTS_ON_COMMISSION_LINE,
    T1139_STATEMENTS_ON_FARMING_LINE,
    T1139_STATEMENTS_ON_FISHING_LINE,
    T1139_STATEMENTS_ON_PROFESSIONAL_LINE,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The amounts that are never below 0 on the form: figures the filer enters, the lines the form
# bounds at 0 and the lines the form shows no negative for.
NON_NEGATIVE: tuple[ArtifactKind[Decimal], ...] = (
    T1139_AMOUNT_2A,
    T1139_AMOUNT_2B,
    T1139_AMOUNT_2E,
    T1139_AMOUNT_2F,
    T1139_AMOUNT_2I,
    T1139_AMOUNT_2J,
    T1139_AMOUNT_2M,
    T1139_AMOUNT_2N,
    T1139_DESIGNATED_AMOUNT,
    T1139_AMOUNT_3A,
    T1139_AMOUNT_3B,
    T1139_AMOUNT_3E,
    T1139_AMOUNT_3F,
    T1139_LAST_YEARS_ADDITIONAL_INCOME,
    T1139_AMOUNT_2C,
    T1139_AMOUNT_2K,
    T1139_AMOUNT_3C,
    T1139_AMOUNT_D,
    T1139_PROFIT_A,
    T1139_PROFIT_H,
    T1139_PROFIT_I,
    T1139_PROFIT_HI,
    T1139_PROFIT_REPLACED,
    T1139_PROFIT_REPLACED_ON_BUSINESS_LINE,
    T1139_STATEMENT_PROFITS_ON_BUSINESS_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_BUSINESS_LINE,
    T1139_PROFIT_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_STATEMENT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_PROFIT_REPLACED_ON_COMMISSION_LINE,
    T1139_STATEMENT_PROFITS_ON_COMMISSION_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_COMMISSION_LINE,
    T1139_PROFIT_REPLACED_ON_FARMING_LINE,
    T1139_STATEMENT_PROFITS_ON_FARMING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FARMING_LINE,
    T1139_PROFIT_REPLACED_ON_FISHING_LINE,
    T1139_STATEMENT_PROFITS_ON_FISHING_LINE,
    T1139_REPLACED_PROFITS_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_PROFITS_TOTAL_ON_FISHING_LINE,
)
# The amounts the form shows as possibly a loss: kept signed as printed.
SIGNED_AMOUNTS: tuple[ArtifactKind[Decimal], ...] = (
    T1139_AMOUNT_2H,
    T1139_AMOUNT_A,
    T1139_AMOUNT_H,
    T1139_AMOUNT_I,
    T1139_AMOUNT_2D,
    T1139_AMOUNT_B,
    T1139_AMOUNT_B_CHOSEN,
    T1139_AMOUNT_C_CHOSEN,
    T1139_AMOUNT_3H_CHOSEN,
    T1139_AMOUNT_2L,
    T1139_FORMULA_AMOUNT_FOR_C,
    T1139_DESIGNATED_OR_FORMULA_AMOUNT,
    T1139_AMOUNT_C,
    T1139_AMOUNT_3D,
    T1139_AMOUNT_3H,
    T1139_AMOUNT_E,
    T1139_AMOUNT_G,
    T1139_AMOUNT_J,
    T1139_AMOUNT_L,
    T1139_NET_INCOME_REPORTED,
    T1139_NET_INCOME_REPLACED,
    T1139_REPORTED_ON_BUSINESS_LINE,
    T1139_REPORTED_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_ON_COMMISSION_LINE,
    T1139_REPORTED_ON_FARMING_LINE,
    T1139_REPORTED_ON_FISHING_LINE,
    T1139_REPLACED_ON_BUSINESS_LINE,
    T1139_REPLACED_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_ON_COMMISSION_LINE,
    T1139_REPLACED_ON_FARMING_LINE,
    T1139_REPLACED_ON_FISHING_LINE,
    T1139_STATEMENTS_ON_BUSINESS_LINE,
    T1139_REPLACED_TOTAL_ON_BUSINESS_LINE,
    T1139_REPORTED_TOTAL_ON_BUSINESS_LINE,
    T1139_KEPT_ON_BUSINESS_LINE,
    T1139_BUSINESS_INCOME_ON_RETURN,
    T1139_STATEMENTS_ON_PROFESSIONAL_LINE,
    T1139_REPLACED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_REPORTED_TOTAL_ON_PROFESSIONAL_LINE,
    T1139_KEPT_ON_PROFESSIONAL_LINE,
    T1139_PROFESSIONAL_INCOME_ON_RETURN,
    T1139_STATEMENTS_ON_COMMISSION_LINE,
    T1139_REPLACED_TOTAL_ON_COMMISSION_LINE,
    T1139_REPORTED_TOTAL_ON_COMMISSION_LINE,
    T1139_KEPT_ON_COMMISSION_LINE,
    T1139_COMMISSION_INCOME_ON_RETURN,
    T1139_STATEMENTS_ON_FARMING_LINE,
    T1139_REPLACED_TOTAL_ON_FARMING_LINE,
    T1139_REPORTED_TOTAL_ON_FARMING_LINE,
    T1139_KEPT_ON_FARMING_LINE,
    T1139_FARMING_INCOME_ON_RETURN,
    T1139_STATEMENTS_ON_FISHING_LINE,
    T1139_REPLACED_TOTAL_ON_FISHING_LINE,
    T1139_REPORTED_TOTAL_ON_FISHING_LINE,
    T1139_KEPT_ON_FISHING_LINE,
    T1139_FISHING_INCOME_ON_RETURN,
    T1139_KEPT_PROFITS_ON_BUSINESS_LINE,
    T1139_BUSINESS_PROFIT_ON_RETURN,
    T1139_KEPT_PROFITS_ON_PROFESSIONAL_LINE,
    T1139_PROFESSIONAL_PROFIT_ON_RETURN,
    T1139_KEPT_PROFITS_ON_COMMISSION_LINE,
    T1139_COMMISSION_PROFIT_ON_RETURN,
    T1139_KEPT_PROFITS_ON_FARMING_LINE,
    T1139_FARMING_PROFIT_ON_RETURN,
    T1139_KEPT_PROFITS_ON_FISHING_LINE,
    T1139_FISHING_PROFIT_ON_RETURN,
)
# The counts: the line, the positions of the statements, the box ticked, the answer to designating
# an amount and the flags of the five lines.
COUNT_KINDS: tuple[ArtifactKind[int], ...] = (
    T1139_LINE,
    T1139_STATEMENT_NUMBER,
    T1139_CANCELLING_ELECTION,
    T1139_DESIGNATES_AMOUNT,
    T1139_CANCELLING_ELECTION_CHECKED,
    T1139_DESIGNATES_AMOUNT_CHECKED,
    T1139_ON_BUSINESS_LINE,
    T1139_ON_PROFESSIONAL_LINE,
    T1139_ON_COMMISSION_LINE,
    T1139_ON_FARMING_LINE,
    T1139_ON_FISHING_LINE,
    T1139_FORMULA,
    T1139_LINE_CHECKED,
    T1139_FORMULA_CHECKED,
    T1139_FORMULA_IS_B,
    T1139_FORMULA_IS_C,
    T1139_FORMULA_IS_3H,
)
LISTS: tuple[RecordListKind, ...] = (
    T1139_A_STATEMENTS,
    T1139_H_STATEMENTS,
    T1139_I_STATEMENTS,
    T1139_BUSINESSES,
)
ALL_KINDS: tuple[ArtifactKind[Any], ...] = (
    *NON_NEGATIVE,
    *SIGNED_AMOUNTS,
    *COUNT_KINDS,
    *LISTS,
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


def test_the_t1139_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t1139_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_non_negative_amounts_are_non_negative_decimals() -> None:
    for kind in NON_NEGATIVE:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_amounts_the_form_may_show_as_a_loss_are_signed_decimals() -> None:
    for kind in SIGNED_AMOUNTS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is False, kind.identifier
        assert kind.identifier in SIGNED, kind.identifier


def test_the_counts_are_non_negative_whole_numbers_in_the_snapshot() -> None:
    for kind in COUNT_KINDS:
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier in COUNTS, kind.identifier


def test_the_lists_are_record_lists_in_the_snapshot() -> None:
    for kind in LISTS:
        assert isinstance(kind, RecordListKind)
        assert kind.identifier in RECORD_LISTS, kind.identifier
        assert kind.identifier not in COUNTS | SIGNED, kind.identifier


def test_the_amounts_are_neither_counts_nor_record_lists() -> None:
    for amount in (*NON_NEGATIVE, *SIGNED_AMOUNTS):
        assert amount.identifier not in COUNTS | RECORD_LISTS, amount.identifier


def test_each_statements_list_holds_the_position_of_a_statement() -> None:
    for kind in (T1139_A_STATEMENTS, T1139_H_STATEMENTS, T1139_I_STATEMENTS):
        assert kind.fields == (T1139_STATEMENT_NUMBER,)


def test_the_businesses_list_holds_the_lines_the_row_form_reads() -> None:
    assert T1139_BUSINESSES.identifier == "ca/t1139_businesses"
    assert T1139_BUSINESSES.fields == (
        T1139_LINE,
        T1139_FORMULA,
        T1139_A_STATEMENTS,
        T1139_H_STATEMENTS,
        T1139_I_STATEMENTS,
        T1139_CANCELLING_ELECTION,
        T1139_AMOUNT_2A,
        T1139_AMOUNT_2B,
        T1139_AMOUNT_2E,
        T1139_AMOUNT_2F,
        T1139_AMOUNT_2H,
        T1139_AMOUNT_2I,
        T1139_AMOUNT_2J,
        T1139_AMOUNT_2M,
        T1139_AMOUNT_2N,
        T1139_DESIGNATES_AMOUNT,
        T1139_DESIGNATED_AMOUNT,
        T1139_AMOUNT_3A,
        T1139_AMOUNT_3B,
        T1139_AMOUNT_3E,
        T1139_AMOUNT_3F,
        T1139_LAST_YEARS_ADDITIONAL_INCOME,
    )


def test_the_identifiers_are_the_stable_names_of_the_lines() -> None:
    assert {kind.identifier for kind in ALL_KINDS} == {
        "ca/t1139_amount_2a",
        "ca/t1139_amount_2b",
        "ca/t1139_amount_2c",
        "ca/t1139_amount_2d",
        "ca/t1139_amount_2e",
        "ca/t1139_amount_2f",
        "ca/t1139_amount_2h",
        "ca/t1139_amount_2i",
        "ca/t1139_amount_2j",
        "ca/t1139_amount_2k",
        "ca/t1139_amount_2l",
        "ca/t1139_amount_2m",
        "ca/t1139_amount_2n",
        "ca/t1139_amount_3a",
        "ca/t1139_amount_3b",
        "ca/t1139_amount_3c",
        "ca/t1139_amount_3d",
        "ca/t1139_amount_3e",
        "ca/t1139_amount_3f",
        "ca/t1139_amount_3h",
        "ca/t1139_amount_a",
        "ca/t1139_amount_b",
        "ca/t1139_amount_c",
        "ca/t1139_amount_d",
        "ca/t1139_amount_e",
        "ca/t1139_amount_g",
        "ca/t1139_amount_h",
        "ca/t1139_amount_i",
        "ca/t1139_amount_j",
        "ca/t1139_amount_l",
        "ca/t1139_business_income_on_return",
        "ca/t1139_cancelling_election",
        "ca/t1139_cancelling_election_checked",
        "ca/t1139_commission_income_on_return",
        "ca/t1139_designated_amount",
        "ca/t1139_designated_or_formula_amount",
        "ca/t1139_designates_amount",
        "ca/t1139_designates_amount_checked",
        "ca/t1139_formula",
        "ca/t1139_line_checked",
        "ca/t1139_formula_checked",
        "ca/t1139_formula_is_b",
        "ca/t1139_formula_is_c",
        "ca/t1139_formula_is_3h",
        "ca/t1139_amount_b_chosen",
        "ca/t1139_amount_c_chosen",
        "ca/t1139_amount_3h_chosen",
        "ca/t1139_farming_income_on_return",
        "ca/t1139_fishing_income_on_return",
        "ca/t1139_formula_amount_for_c",
        "ca/t1139_kept_on_business_line",
        "ca/t1139_kept_on_commission_line",
        "ca/t1139_kept_on_farming_line",
        "ca/t1139_kept_on_fishing_line",
        "ca/t1139_kept_on_professional_line",
        "ca/t1139_last_years_additional_income",
        "ca/t1139_line",
        "ca/t1139_net_income_replaced",
        "ca/t1139_net_income_reported",
        "ca/t1139_on_business_line",
        "ca/t1139_on_commission_line",
        "ca/t1139_on_farming_line",
        "ca/t1139_on_fishing_line",
        "ca/t1139_on_professional_line",
        "ca/t1139_professional_income_on_return",
        "ca/t1139_replaced_on_business_line",
        "ca/t1139_replaced_on_commission_line",
        "ca/t1139_replaced_on_farming_line",
        "ca/t1139_replaced_on_fishing_line",
        "ca/t1139_replaced_on_professional_line",
        "ca/t1139_replaced_total_on_business_line",
        "ca/t1139_replaced_total_on_commission_line",
        "ca/t1139_replaced_total_on_farming_line",
        "ca/t1139_replaced_total_on_fishing_line",
        "ca/t1139_replaced_total_on_professional_line",
        "ca/t1139_reported_on_business_line",
        "ca/t1139_reported_on_commission_line",
        "ca/t1139_reported_on_farming_line",
        "ca/t1139_reported_on_fishing_line",
        "ca/t1139_reported_on_professional_line",
        "ca/t1139_reported_total_on_business_line",
        "ca/t1139_reported_total_on_commission_line",
        "ca/t1139_reported_total_on_farming_line",
        "ca/t1139_reported_total_on_fishing_line",
        "ca/t1139_reported_total_on_professional_line",
        "ca/t1139_statement_number",
        "ca/t1139_statements_on_business_line",
        "ca/t1139_statements_on_commission_line",
        "ca/t1139_statements_on_farming_line",
        "ca/t1139_statements_on_fishing_line",
        "ca/t1139_statements_on_professional_line",
        "ca/t1139_a_statements",
        "ca/t1139_h_statements",
        "ca/t1139_i_statements",
        "ca/t1139_businesses",
        "ca/t1139_business_profit_on_return",
        "ca/t1139_commission_profit_on_return",
        "ca/t1139_farming_profit_on_return",
        "ca/t1139_fishing_profit_on_return",
        "ca/t1139_kept_profits_on_business_line",
        "ca/t1139_kept_profits_on_commission_line",
        "ca/t1139_kept_profits_on_farming_line",
        "ca/t1139_kept_profits_on_fishing_line",
        "ca/t1139_kept_profits_on_professional_line",
        "ca/t1139_professional_profit_on_return",
        "ca/t1139_profit_a",
        "ca/t1139_profit_h",
        "ca/t1139_profit_hi",
        "ca/t1139_profit_i",
        "ca/t1139_profit_replaced",
        "ca/t1139_profit_replaced_on_business_line",
        "ca/t1139_profit_replaced_on_commission_line",
        "ca/t1139_profit_replaced_on_farming_line",
        "ca/t1139_profit_replaced_on_fishing_line",
        "ca/t1139_profit_replaced_on_professional_line",
        "ca/t1139_replaced_profits_total_on_business_line",
        "ca/t1139_replaced_profits_total_on_commission_line",
        "ca/t1139_replaced_profits_total_on_farming_line",
        "ca/t1139_replaced_profits_total_on_fishing_line",
        "ca/t1139_replaced_profits_total_on_professional_line",
        "ca/t1139_reported_profits_total_on_business_line",
        "ca/t1139_reported_profits_total_on_commission_line",
        "ca/t1139_reported_profits_total_on_farming_line",
        "ca/t1139_reported_profits_total_on_fishing_line",
        "ca/t1139_reported_profits_total_on_professional_line",
        "ca/t1139_statement_profits_on_business_line",
        "ca/t1139_statement_profits_on_commission_line",
        "ca/t1139_statement_profits_on_farming_line",
        "ca/t1139_statement_profits_on_fishing_line",
        "ca/t1139_statement_profits_on_professional_line",
    }


def test_each_t1139_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T1139" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_lines_quote_their_printed_words() -> None:
    quotes: dict[ArtifactKind[Any], str] = {
        T1139_LINE: "enter it at line 13500",
        T1139_STATEMENT_NUMBER: "net income (loss) amount you need to enter at amount A",
        T1139_CANCELLING_ELECTION: "I am cancelling my previous election",
        T1139_AMOUNT_2A: "Total of amount A considered to be a taxable capital gain",
        T1139_AMOUNT_2B: "Your total capital gains deduction for 2025",
        T1139_AMOUNT_2E: "carried on the business after your fiscal period ending in 2025",
        T1139_AMOUNT_2F: "Number of days that you carried on the business in your fiscal period",
        T1139_AMOUNT_2H: "Net income for the fiscal period ending in 2026",
        T1139_AMOUNT_2J: "Your total capital gains deduction for 2026",
        T1139_AMOUNT_2M: "Number of days in 2025 that you carried on the business",
        T1139_AMOUNT_2N: "carried on the business in your fiscal period ending in 2026",
        T1139_DESIGNATES_AMOUNT: "any amount you designate as your additional business income",
        T1139_AMOUNT_3E: "up to and including the date of death",
        T1139_AMOUNT_3F: "regular fiscal period ending in 2025",
        T1139_LAST_YEARS_ADDITIONAL_INCOME: "Enter amount D from last year's Form T1139",
        T1139_AMOUNT_A: "amount A is the total of the net income (loss) of these fiscal periods",
        T1139_AMOUNT_H: "between January 1, 2025, and December 30, 2025",
        T1139_AMOUNT_I: "You need a separate income and expense statement for each fiscal period",
        T1139_AMOUNT_2C: "Amount 2A or 2B, whichever is less",
        T1139_AMOUNT_2D: "Amount A minus amount 2C",
        T1139_AMOUNT_B: "Amount 2D multiplied by amount 2G",
        T1139_AMOUNT_2K: "Amount 2I or 2J, whichever is less",
        T1139_AMOUNT_2L: "Amount 2H minus amount 2K",
        T1139_FORMULA_AMOUNT_FOR_C: "Amount 2L multiplied by amount 2O",
        T1139_AMOUNT_C: "Enter at amount C the lesser of any amount you designate",
        T1139_AMOUNT_3C: "Amounts 3A or 3B, whichever is less",
        T1139_AMOUNT_3D: "Amount A minus amount 3C",
        T1139_AMOUNT_3H: "Amount 3D multiplied by amount 3G",
        T1139_AMOUNT_D: "Enter either amount B, C, or 3H based on the formula you used above",
        T1139_AMOUNT_E: "Subtotal: Amount A plus amount D",
        T1139_AMOUNT_G: "Amount E minus amount F",
        T1139_AMOUNT_J: "Subtotal: Amount H plus amount I",
        T1139_AMOUNT_L: "Amount J minus amount K",
        T1139_NET_INCOME_REPORTED: "Report amount G as self-employment income on your return",
        T1139_ON_BUSINESS_LINE: "For business income, enter it at line 13500",
        T1139_ON_FISHING_LINE: "For fishing income, enter it at line 14300",
        T1139_FORMULA: "Use only one of the formulas below",
        T1139_AMOUNT_B_CHOSEN: "Enter either amount B, C, or 3H",
        T1139_REPORTED_ON_FARMING_LINE: "For farming income, enter it at line 14100",
        T1139_BUSINESS_INCOME_ON_RETURN: "For business income, enter it at line 13500",
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier
