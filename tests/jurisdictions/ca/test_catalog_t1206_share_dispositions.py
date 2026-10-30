"""Registered kinds of the Form T1206 section "Dispositions of certain capital property - shares
subject to TOSI" (page 6), in the federal catalog family `t1206_share_dispositions`.

The section is two forms of its own: `ca/t1206_share_dispositions` (lines A to G, the under-18
dividend amount and the 18-or-older amount) and `ca/t1206_share_reserve` (the calculation of
reserve, one copy for each row of `ca/t1206_share_reserve_rows`). The starting inputs are lines A,
B and F and the row list; the age answer is the return's existing input.
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
    T1206_AGED_18_OR_OLDER_CHECKED,
    T1206_CAPITAL_GAIN_ON_DISPOSITIONS,
    T1206_LINE_C,
    T1206_LINE_C_CHECKED,
    T1206_LINE_D,
    T1206_LINE_E,
    T1206_LINE_G,
    T1206_LINES_A_AND_B,
    T1206_PART_1_LINE_3_AMOUNT,
    T1206_PART_1_LINE_3_PERCENT,
    T1206_RESERVE_2024,
    T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T1206_RESERVE_APPLICABLE_PERCENTAGE,
    T1206_RESERVE_BY_PAYMENT,
    T1206_RESERVE_BY_PERCENTAGE,
    T1206_RESERVE_CAPITAL_GAIN,
    T1206_RESERVE_CLAIMED,
    T1206_RESERVE_MAXIMUM,
    T1206_RESERVE_PAYABLE_CHECKED,
    T1206_RESERVE_PROCEEDS,
    T1206_RESERVE_YEARS_AFTER_SALE,
    T1206_ROW_RESERVE,
    T1206_SHARE_RESERVE_ROWS,
    T1206_T3_BOX_21_CAPITAL_GAINS,
    T1206_UNDER_18_DIVIDEND_AMOUNT,
    T1206_UNDER_18_PERCENT,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

# The money kinds: non-negative dollars and cents, one for each printed amount or step of the
# calculation of reserve (the percentages are the printed percentages as amounts).
MONEY = (
    T1206_CAPITAL_GAIN_ON_DISPOSITIONS,
    T1206_RESERVE_2024,
    T1206_T3_BOX_21_CAPITAL_GAINS,
    T1206_LINES_A_AND_B,
    T1206_LINE_C,
    T1206_LINE_C_CHECKED,
    T1206_LINE_E,
    T1206_LINE_G,
    T1206_UNDER_18_PERCENT,
    T1206_UNDER_18_DIVIDEND_AMOUNT,
    T1206_PART_1_LINE_3_PERCENT,
    T1206_PART_1_LINE_3_AMOUNT,
    T1206_RESERVE_MAXIMUM,
    T1206_ROW_RESERVE,
    T1206_RESERVE_PAYABLE_CHECKED,
    T1206_RESERVE_BY_PAYMENT,
    T1206_RESERVE_APPLICABLE_PERCENTAGE,
    T1206_RESERVE_BY_PERCENTAGE,
)
# The fields of one row of the reserve list (the reserve form's inputs), the claim last.
ROW_FIELDS = (
    T1206_RESERVE_CAPITAL_GAIN,
    T1206_RESERVE_AMOUNT_PAYABLE_AFTER_YEAR_END,
    T1206_RESERVE_PROCEEDS,
    T1206_RESERVE_YEARS_AFTER_SALE,
    T1206_RESERVE_CLAIMED,
)
# Line D is signed: "Line B minus line C (if negative, show in brackets)".
ALL_KINDS = (
    *MONEY,
    T1206_LINE_D,
    T1206_AGED_18_OR_OLDER_CHECKED,
    *ROW_FIELDS,
    T1206_SHARE_RESERVE_ROWS,
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


def test_the_t1206_kinds_are_registered_under_their_identifiers(registry: ArtifactRegistry) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t1206_kinds_are_in_the_snapshot_and_in_the_right_groups() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED
    assert T1206_SHARE_RESERVE_ROWS.identifier in RECORD_LISTS
    assert {
        T1206_AGED_18_OR_OLDER_CHECKED.identifier,
        T1206_RESERVE_YEARS_AFTER_SALE.identifier,
    } <= (COUNTS)
    assert T1206_LINE_D.identifier in SIGNED
    for amount in (*MONEY, *ROW_FIELDS[:3]):
        assert amount.identifier not in RECORD_LISTS | COUNTS, amount.identifier


def test_the_row_list_is_a_record_list_kind_of_the_five_reserve_fields_in_order() -> None:
    assert isinstance(T1206_SHARE_RESERVE_ROWS, RecordListKind)
    assert T1206_SHARE_RESERVE_ROWS.identifier == "ca/t1206_share_reserve_rows"
    assert T1206_SHARE_RESERVE_ROWS.fields == ROW_FIELDS


def test_the_row_fields_hold_the_figures_and_the_claim_of_each_disposition() -> None:
    assert [kind.identifier for kind in ROW_FIELDS] == [
        "ca/t1206_reserve_capital_gain",
        "ca/t1206_reserve_amount_payable_after_year_end",
        "ca/t1206_reserve_proceeds",
        "ca/t1206_reserve_years_after_sale",
        "ca/t1206_reserve_claimed",
    ]
    assert [kind.value_type for kind in (ROW_FIELDS[0], ROW_FIELDS[1], ROW_FIELDS[2])] == [
        Decimal,
        Decimal,
        Decimal,
    ]
    assert ROW_FIELDS[3].value_type is int
    assert ROW_FIELDS[4].value_type is Decimal
    assert ROW_FIELDS[4].non_negative is True


def test_the_money_kinds_are_non_negative_decimals() -> None:
    for kind in MONEY:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_line_d_is_a_signed_decimal_as_the_form_prints_no_floor() -> None:
    assert T1206_LINE_D.value_type is Decimal
    assert T1206_LINE_D.non_negative is False


def test_the_two_counts_are_non_negative_int_kinds() -> None:
    for kind in (T1206_AGED_18_OR_OLDER_CHECKED, T1206_RESERVE_YEARS_AFTER_SALE):
        assert kind.value_type is int, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_the_exports_of_the_two_forms_are_registered_money() -> None:
    for kind in (T1206_LINE_C, T1206_LINE_G, T1206_UNDER_18_DIVIDEND_AMOUNT):
        assert kind.value_type is Decimal, kind.identifier
    assert T1206_PART_1_LINE_3_AMOUNT.value_type is Decimal
    assert T1206_ROW_RESERVE.value_type is Decimal
    assert T1206_ROW_RESERVE.identifier == "ca/t1206_row_reserve"
    assert T1206_RESERVE_MAXIMUM.identifier == "ca/t1206_reserve_maximum"
    assert T1206_RESERVE_MAXIMUM.value_type is Decimal


def test_the_starting_inputs_are_the_registered_money_of_lines_a_b_and_f() -> None:
    for kind in (
        T1206_CAPITAL_GAIN_ON_DISPOSITIONS,
        T1206_RESERVE_2024,
        T1206_T3_BOX_21_CAPITAL_GAINS,
    ):
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier


def test_each_t1206_kind_has_a_docstring_that_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T1206" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_line_d_docstring_quotes_the_form_line_and_its_brackets() -> None:
    text = squashed(docstring_of(T1206_LINE_D.identifier))

    assert "Line B minus line C (if negative, show in brackets)" in text


def test_the_row_list_docstring_names_the_calculation_of_reserve() -> None:
    assert "Calculation of reserve" in squashed(docstring_of(T1206_SHARE_RESERVE_ROWS.identifier))


def test_the_claim_docstring_quotes_the_form_s_reserve_sentence() -> None:
    text = squashed(docstring_of(T1206_RESERVE_CLAIMED.identifier))

    assert (
        "Your reserve in each year cannot be more than whichever of the following two "
        "calculations is less" in text
    )
    assert "include the total amount of your 2025 reserve on line C above" in text


def test_the_reserve_intermediate_kinds_are_registered_beside_the_row_reserve(
    registry: ArtifactRegistry,
) -> None:
    intermediate: tuple[ArtifactKind[Any], ...] = (
        T1206_RESERVE_PAYABLE_CHECKED,
        T1206_RESERVE_BY_PAYMENT,
        T1206_RESERVE_APPLICABLE_PERCENTAGE,
        T1206_RESERVE_BY_PERCENTAGE,
    )
    for kind in intermediate:
        assert registry.get(kind.identifier) is kind, kind.identifier
        assert kind.identifier in REGISTERED, kind.identifier
