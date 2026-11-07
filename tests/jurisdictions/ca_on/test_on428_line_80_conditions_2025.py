"""The 2025 condition of ON428 line 80's count, checked against CRA's ON428 text.

2025 ON428 (form 5006-C), line 80: "Enter "0" on line 80 if any of the following applies to you:"
followed by the printed conditions, one of which is "There is an amount on line 72". The dataset
`ca-on/on428_line_80_conditions` copies that one condition in the form's wording. The count of the
list is 0 when the condition applies and 1 when it does not: line 72 is an amount other than 0 gives
0, and line 72 left out (read as blank, then as "0" by the take-home part) gives 1. The other
printed conditions are not in this dataset.

The count is a whole number, not a dollars-and-cents box, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind, CountKind
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
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca-on/on428_line_80_conditions"
ON428_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5006-c/5006-c-25e.txt"

# Made up for this test and not registered: the amount on line 72 and the count it gives.
LINE_72 = AmountKind("ex/on428_line_72")
LINE_80_COUNT = CountKind("ex/on428_line_80_count")


def test_2025_line_80_conditions_is_one_condition_on_line_72_and_counts_0_when_it_applies() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "There is an amount on line 72",
                (ConditionPart((ConditionTest("amount", 1, "not_equal_to", D(0), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_2025_line_80_conditions_reads_one_amount_and_no_count() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.amount_positions_read == frozenset({1})
    assert values.count_positions_read == frozenset()


def test_2025_line_80_conditions_cite_only_the_on428_text() -> None:
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).sources == (ON428_TEXT,)


def test_2025_line_80_conditions_do_not_round() -> None:
    # A count, not the amount of a line: nothing is rounded.
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("line_72", "count"),
    [
        # Line 72 is 0 or 0.00: not an amount, so the condition does not apply and the count is 1.
        ("0", 1),
        ("0.00", 1),
        # Line 72 is one cent or more: the condition applies, so the count is 0.
        ("0.01", 0),
        ("100.00", 0),
        ("300.14", 0),
    ],
)
def test_line_80_count_is_0_when_line_72_is_an_amount_and_1_otherwise(
    line_72: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS),
        (),
        (LINE_72,),
        LINE_80_COUNT,
    )

    result = capability.compute((Artifact(LINE_72, D(line_72)),)).outputs

    assert result == (Artifact(LINE_80_COUNT, count),)
