"""Kinds of the fishing boat used mainly for personal use (Form T2121, Guide T4002 page 51).

Guide T4002 2025 (https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t4002/t4002-25e.pdf,
"Use of a fishing boat mainly for personal use", page 51; confirmed from the PDF, no .txt
published): "You may have used a fishing boat mainly for personal use, but sometimes caught a small
amount of fish to sell. In this case, you can deduct expenses and CCA. However, the amount you
deduct cannot be more than your income from the catch." Form T2121 prints no line for the limit.
The answer is the filer's, one yes or no for each T2121 statement, a count of 0 or 1 checked before
it is read.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    FISH_BOAT_MAINLY_PERSONAL,
    FISH_BOAT_MAINLY_PERSONAL_CHECKED,
    FISH_EXPENSES_LIMITED_TO_CATCH_INCOME,
    FISH_NET_INCOME_BEFORE_BOAT_LIMIT,
    FISH_TOTAL_EXPENSES,
    FISH_TOTAL_EXPENSES_DEDUCTIBLE,
    T2121_STATEMENTS,
)

# (identifier, constant, value type, non-negative): the two amounts are signed like line 9368, which
# they are the lesser of or a choice of.
KINDS: tuple[tuple[str, ArtifactKind[Any], type, bool], ...] = (
    ("ca/fish_boat_mainly_personal", FISH_BOAT_MAINLY_PERSONAL, int, True),
    ("ca/fish_boat_mainly_personal_checked", FISH_BOAT_MAINLY_PERSONAL_CHECKED, int, True),
    (
        "ca/fish_expenses_limited_to_catch_income",
        FISH_EXPENSES_LIMITED_TO_CATCH_INCOME,
        Decimal,
        False,
    ),
    ("ca/fish_net_income_before_boat_limit", FISH_NET_INCOME_BEFORE_BOAT_LIMIT, Decimal, False),
    ("ca/fish_total_expenses_deductible", FISH_TOTAL_EXPENSES_DEDUCTIBLE, Decimal, False),
)


@pytest.mark.parametrize(("identifier", "constant", "value_type", "non_negative"), KINDS)
def test_each_fishing_boat_kind_is_registered_under_its_name(
    identifier: str,
    constant: ArtifactKind[Any],
    value_type: type,
    non_negative: bool,
    registry: ArtifactRegistry,
) -> None:
    assert constant.identifier == identifier
    assert registry.get(identifier) is constant
    assert constant.value_type is value_type
    assert constant.non_negative is non_negative


def test_the_answer_is_the_last_field_of_each_t2121_statement_and_its_check_is_not_a_field() -> (
    None
):
    assert T2121_STATEMENTS.fields[-1] is FISH_BOAT_MAINLY_PERSONAL
    assert FISH_BOAT_MAINLY_PERSONAL_CHECKED not in T2121_STATEMENTS.fields


def test_the_deductible_total_is_a_new_kind_beside_line_9368() -> None:
    # Line 9368 stays the total of the expenses and the CCA; the deductible total is its own kind.
    assert FISH_TOTAL_EXPENSES_DEDUCTIBLE is not FISH_TOTAL_EXPENSES
    assert FISH_EXPENSES_LIMITED_TO_CATCH_INCOME is not FISH_TOTAL_EXPENSES
