"""Kinds of the restricted farm loss on the T2042 net farm loss (Guide T4002, line 14100).

Guide T4002 (docs/cra-forms-2025/t4002-25e.pdf, "Restricted farm losses (partly deductible)",
pp. 95-96; confirmed from the PDF, no .txt published): "However, if farming was neither your main
source of income (...) nor was it your main source of income in addition to some other subordinate
source of income (...) you may only be able to deduct a part of your net farm loss." The answer is
the filer's, one yes or no for each T2042 statement, a count of 0 or 1 checked before it is read.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_calculator.domain.artifact import ArtifactKind, ArtifactRegistry
from tax_calculator.jurisdictions.ca.catalog import (
    FARM_LOSS_DEDUCTIBLE,
    FARM_NET_INCOME_LINE_9946,
    FARM_NET_LOSS,
    FARM_NET_LOSS_LESS_BASE_AMOUNT,
    FARM_NET_LOSS_LESS_FULL_THRESHOLD,
    FARM_NOT_MAIN_SOURCE_OF_INCOME,
    FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED,
    FARM_RESTRICTED_LOSS,
    FARM_RESTRICTED_LOSS_ADDED_BACK,
    FARM_RESTRICTED_LOSS_AMOUNT_B,
    FARM_RESTRICTED_LOSS_ANNUAL_MAXIMUM,
    FARM_RESTRICTED_LOSS_BASE_AMOUNT,
    FARM_RESTRICTED_LOSS_FULL_THRESHOLD,
    FARM_RESTRICTED_LOSS_HALF_OF_EXCESS,
    FARM_RESTRICTED_LOSS_LESSER_OF_A_AND_B,
    FARM_RESTRICTED_LOSS_PERCENTAGE,
    FARMING_INCOME,
    T2042_STATEMENTS,
)

# (identifier, constant, value type, non-negative): the signed ones are the lines the form's
# arithmetic leaves below zero (the net on line 9946, a loss; a difference with a printed figure
# when the loss is smaller than the figure; 50% of such a difference).
KINDS: tuple[tuple[str, ArtifactKind[Any], type, bool], ...] = (
    ("ca/farm_not_main_source_of_income", FARM_NOT_MAIN_SOURCE_OF_INCOME, int, True),
    (
        "ca/farm_not_main_source_of_income_checked",
        FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED,
        int,
        True,
    ),
    ("ca/farm_net_income_line_9946", FARM_NET_INCOME_LINE_9946, Decimal, False),
    ("ca/farm_net_loss", FARM_NET_LOSS, Decimal, True),
    ("ca/farm_restricted_loss_base_amount", FARM_RESTRICTED_LOSS_BASE_AMOUNT, Decimal, True),
    (
        "ca/farm_restricted_loss_full_threshold",
        FARM_RESTRICTED_LOSS_FULL_THRESHOLD,
        Decimal,
        True,
    ),
    (
        "ca/farm_restricted_loss_annual_maximum",
        FARM_RESTRICTED_LOSS_ANNUAL_MAXIMUM,
        Decimal,
        True,
    ),
    ("ca/farm_restricted_loss_percentage", FARM_RESTRICTED_LOSS_PERCENTAGE, Decimal, True),
    ("ca/farm_net_loss_less_base_amount", FARM_NET_LOSS_LESS_BASE_AMOUNT, Decimal, False),
    ("ca/farm_restricted_loss_half_of_excess", FARM_RESTRICTED_LOSS_HALF_OF_EXCESS, Decimal, False),
    ("ca/farm_restricted_loss_amount_b", FARM_RESTRICTED_LOSS_AMOUNT_B, Decimal, True),
    (
        "ca/farm_restricted_loss_lesser_of_a_and_b",
        FARM_RESTRICTED_LOSS_LESSER_OF_A_AND_B,
        Decimal,
        True,
    ),
    ("ca/farm_net_loss_less_full_threshold", FARM_NET_LOSS_LESS_FULL_THRESHOLD, Decimal, False),
    ("ca/farm_loss_deductible", FARM_LOSS_DEDUCTIBLE, Decimal, True),
    ("ca/farm_restricted_loss", FARM_RESTRICTED_LOSS, Decimal, True),
    ("ca/farm_restricted_loss_added_back", FARM_RESTRICTED_LOSS_ADDED_BACK, Decimal, True),
)


@pytest.mark.parametrize(("identifier", "constant", "value_type", "non_negative"), KINDS)
def test_each_restricted_farm_loss_kind_is_registered_under_its_name(
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


def test_the_answer_is_the_returns_not_a_field_of_a_t2042_statement() -> None:
    # Asked once for the return, so no statement carries it, and neither does its check.
    assert FARM_NOT_MAIN_SOURCE_OF_INCOME not in T2042_STATEMENTS.fields
    assert FARM_NOT_MAIN_SOURCE_OF_INCOME_CHECKED not in T2042_STATEMENTS.fields


def test_the_line_9946_net_is_a_new_signed_kind_beside_the_farming_income_the_return_reads(
    registry: ArtifactRegistry,
) -> None:
    # `ca/farm_net_income_line_9946` is the net of all the statements' line 9946;
    # `ca/farming_income` (T1 line 14100, "Net") is the amount after the restricted part is added
    # back, still signed.
    assert FARM_NET_INCOME_LINE_9946 is not FARMING_INCOME
    assert registry.get("ca/farming_income") is FARMING_INCOME
    assert FARMING_INCOME.value_type is Decimal
    assert FARMING_INCOME.non_negative is False
