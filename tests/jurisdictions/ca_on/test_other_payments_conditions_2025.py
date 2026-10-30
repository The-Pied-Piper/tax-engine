"""The 2025 conditions of the Federal Worksheet "Line 25000 - Other payments deduction".

Form 5000-D1 (2025): "Complete the following calculation if you reported net federal supplements
on line 14600 of your return." and "If the amount on line 9 is more than $93,454, go to
canada.ca/line-25000 to find out how much you can deduct. Otherwise, enter the amount from line
14700 of your return on line 25000 of your return." Each condition is a count of 1 when it applies
and 0 when it does not; the counts are whole numbers, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
REQUIRED = "ca/other_payments_worksheet_required_conditions"
OVER_LIMIT = "ca/other_payments_line_9_over_limit_conditions"
D1_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-d1/5000-d1-25e.txt"

# Made up for this test and not registered: the amount tested, and the count it gives.
AMOUNT = ArtifactKind("ex/amount", Decimal)
COUNT = ArtifactKind("ex/count", int)


def test_2025_the_worksheet_is_required_when_an_amount_was_entered_on_line_14600() -> None:
    data = SOURCE.get(REQUIRED, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "you reported net federal supplements on line 14600 of your return",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING
    assert D1_TXT in data.sources


def test_2025_line_9_over_the_limit_is_more_than_93454() -> None:
    data = SOURCE.get(OVER_LIMIT, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "the amount on line 9 is more than $93,454",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("93454"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING
    assert D1_TXT in data.sources


def counted(family: str, amount: str) -> tuple[Artifact[int], ...]:
    capability = CountByConditions(SOURCE.get(family, 2025, CONDITIONS), (), (AMOUNT,), COUNT)
    return capability.compute((Artifact(AMOUNT, D(amount)),)).outputs


@pytest.mark.parametrize(
    ("line_14600", "expected"),
    [("5000", 1), ("0.01", 1), ("0", 0)],
)
def test_the_worksheet_is_required_only_when_line_14600_has_an_amount(
    line_14600: str, expected: int
) -> None:
    assert counted(REQUIRED, line_14600) == (Artifact(COUNT, expected),)


@pytest.mark.parametrize(
    ("line_9", "expected"),
    [
        ("93454.01", 1),
        ("115000", 1),
        # "more than $93,454": exactly $93,454 is not over the limit.
        ("93454", 0),
        ("93454.00", 0),
        ("54435", 0),
        # Line 9 is signed: a negative line 9 is not over the limit.
        ("-6000", 0),
    ],
)
def test_line_9_is_over_the_limit_only_when_it_is_more_than_93454(
    line_9: str, expected: int
) -> None:
    assert counted(OVER_LIMIT, line_9) == (Artifact(COUNT, expected),)
