"""The 2025 condition under which Form T1032 recalculates lines 18 to 31, checked against Note 1.

Form T1032 E (25), Step 4 Part B, page 3, Note 1: "If the result is $4,000 or more, enter on line 33
the amount from line 30. If the result is less than $4,000, use that result as the amount for line
17 to recalculate lines 18 to 31." The count is 1 when Note 1 applies and the result is less than
$4,000, and 0 otherwise. The count is a whole number, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_calculator.domain.parameters.rounding import NO_ROUNDING
from tax_calculator.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
FAMILY = "ca/t1032_note_1_recalculation_conditions"
T1032_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.pdf"

# Made up for this test and not registered: the count tested, the $4,000, the result and the count.
APPLIES = ArtifactKind("ex/t1032_note_1_applies", int)
LIMIT = ArtifactKind("ex/t1032_note_1_result_figure", Decimal)
RESULT = ArtifactKind("ex/t1032_note_1_result", Decimal)
RECALCULATION = ArtifactKind("ex/t1032_note_1_recalculation", int)


def test_2025_note_1_applying_with_a_result_below_4000_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "Note 1 applies and the result is less than $4,000",
                (
                    ConditionPart((ConditionTest("count", 1, "more_than", D("0"), None),)),
                    ConditionPart((ConditionTest("amount", 1, "more_than", None, 2),)),
                ),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T1032_PDF in data.sources


@pytest.mark.parametrize(
    ("applies", "result", "count"),
    [
        (1, "0.00", 1),
        (1, "3999.99", 1),
        # "$4,000 or more": line 33 is line 30.
        (1, "4000.00", 0),
        (1, "30000.00", 0),
        # Note 1 does not apply: nothing is recalculated whatever the result.
        (0, "0.00", 0),
        (0, "3999.99", 0),
    ],
)
def test_counts_1_when_note_1_applies_and_the_result_is_below_4000(
    applies: int, result: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS), (APPLIES,), (LIMIT, RESULT), RECALCULATION
    )

    outputs = capability.compute(
        (Artifact(APPLIES, applies), Artifact(LIMIT, D("4000.00")), Artifact(RESULT, D(result)))
    ).outputs

    assert outputs == (Artifact(RECALCULATION, count),)
