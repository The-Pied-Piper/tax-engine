"""Registered kinds of Form T1212 "Statement of Deferred Security Options Benefits", in the federal
catalog family `t1212` (`tax_calculator/jurisdictions/ca/catalog/t1212.py`).

The form `ca/t1212` runs once. Its two starting amounts are the printed line 1 and line 2; the steps
compute line 3 and the 50% of line 2 that footnote (1) says to enter on line 24900.
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import tax_calculator.jurisdictions.ca.catalog
from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    T1212_LINE_1_OPENING_BALANCE,
    T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED,
    T1212_LINE_3_CLOSING_BALANCE,
    T1212_LINE_24900_AMOUNT,
)
from tests.jurisdictions.ca.catalog_snapshot import COUNTS, RECORD_LISTS, REGISTERED, SIGNED

INPUTS = (T1212_LINE_1_OPENING_BALANCE, T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED)
COMPUTED = (T1212_LINE_3_CLOSING_BALANCE, T1212_LINE_24900_AMOUNT)
ALL_KINDS = (*INPUTS, *COMPUTED)


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module."""
    folder = Path(tax_calculator.jurisdictions.ca.catalog.__file__).parent
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


def test_the_t1212_kinds_are_registered_under_their_identifiers(
    registry: ArtifactRegistry,
) -> None:
    for kind in ALL_KINDS:
        assert registry.get(kind.identifier) is kind, kind.identifier


def test_the_t1212_kinds_are_in_the_snapshot() -> None:
    assert {kind.identifier for kind in ALL_KINDS} <= REGISTERED


def test_the_identifiers_are_the_form_lines() -> None:
    assert {kind.identifier for kind in ALL_KINDS} == {
        "ca/t1212_line_1_opening_balance",
        "ca/t1212_line_2_benefits_no_longer_deferred",
        "ca/t1212_line_3_closing_balance",
        "ca/t1212_line_24900_amount",
    }


def test_every_kind_is_a_non_negative_decimal_that_is_not_signed() -> None:
    for kind in ALL_KINDS:
        assert kind.value_type is Decimal, kind.identifier
        assert kind.non_negative is True, kind.identifier
        assert kind.identifier not in SIGNED, kind.identifier


def test_the_t1212_kinds_are_not_counts_or_record_lists() -> None:
    for kind in ALL_KINDS:
        assert kind.identifier not in COUNTS | RECORD_LISTS, kind.identifier


def test_each_docstring_names_the_form() -> None:
    for kind in ALL_KINDS:
        assert "T1212" in squashed(docstring_of(kind.identifier)), kind.identifier


def test_the_docstrings_quote_the_printed_lines() -> None:
    quotes = {
        T1212_LINE_1_OPENING_BALANCE: "Opening balance of deferred security options benefits",
        T1212_LINE_2_BENEFITS_NO_LONGER_DEFERRED: (
            "Benefits that can no longer be deferred. Enter this amount on line 10100 of your "
            "return"
        ),
        T1212_LINE_3_CLOSING_BALANCE: (
            "Closing balance of deferred security options benefits: line 1 minus line 2"
        ),
        T1212_LINE_24900_AMOUNT: (
            "To claim your security options deduction on this amount, enter 50% of the amount "
            "from line 2 on line 24900 of your return"
        ),
    }
    for kind, quote in quotes.items():
        assert quote in squashed(docstring_of(kind.identifier)), kind.identifier
