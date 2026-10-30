"""The 2025 conditions dataset of Form T746's eligibility, against the form.

Form T746 (2025): "For you to claim the deduction, it has to be reasonable for the CRA to consider
that one or both of the following conditions apply: you expected to be able to fully deduct your
RRSP, PRPP, or SPP contributions in the year you made them or the year before; you did not make the
contributions intending to withdraw them later and claim the deduction".

The count (`ca/t746_conditions`) is 1 when at least one of the filer's two yes or no answers is yes
(the two tests of one part: either holds), else 0. It is tested with made-up kinds.
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
T746_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t746/t746-25e.pdf"
FAMILY = "ca/t746_conditions"

TEXT = (
    "it has to be reasonable for the CRA to consider that one or both of the following conditions "
    "apply: you expected to be able to fully deduct your RRSP, PRPP, or SPP contributions in the "
    "year you made them or the year before; you did not make the contributions intending to "
    "withdraw them later and claim the deduction"
)

# Made up for this test and not registered: the two answers and the count.
EXPECTED = ArtifactKind("ex/expected_to_fully_deduct", int)
NOT_INTENDING = ArtifactKind("ex/did_not_intend_to_withdraw", int)
MET = ArtifactKind("ex/conditions_met", int)


def met(expected: int, not_intending: int) -> int:
    """The count of the two answers."""
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS), (EXPECTED, NOT_INTENDING), (), MET
    )
    (count,) = capability.compute(
        (Artifact(EXPECTED, expected), Artifact(NOT_INTENDING, not_intending))
    ).outputs
    return int(count.value)


def test_2025_either_answer_above_0_meets_the_conditions() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                TEXT,
                (
                    ConditionPart(
                        (
                            ConditionTest("count", 1, "more_than", D("0"), None),
                            ConditionTest("count", 2, "more_than", D("0"), None),
                        )
                    ),
                ),
            ),
        ),
    )
    assert data.values.count_positions_read == frozenset({1, 2})
    assert data.values.amount_positions_read == frozenset()


def test_2025_the_count_is_not_rounded_and_cites_form_t746() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.rounding == NO_ROUNDING
    assert T746_PDF in data.sources


@pytest.mark.parametrize(
    ("expected", "not_intending", "count"),
    [(0, 0, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)],
)
def test_the_count_is_1_when_one_or_both_answers_are_yes(
    expected: int, not_intending: int, count: int
) -> None:
    assert met(expected, not_intending) == count
