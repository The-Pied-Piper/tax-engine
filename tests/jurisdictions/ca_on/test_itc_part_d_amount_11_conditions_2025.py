"""The 2025 condition of Form T2038(IND) Part D amount 11, checked against Form T2038(IND).

Form T2038(IND) (2025) Part D: "If you have to complete Form T691, Alternative Minimum Tax and the
amount you calculate on line 7 of Part 5 in Form T691 is greater than "0", continue at amount 11."
and "If alternative minimum tax (AMT) does not apply to you, continue at amount 15." The condition
"T691 Part 5 line 7 is greater than 0" is a count of 1 when that line is more than 0 and 0
otherwise. It chooses the limit of the claim: the lesser of G and H (amount I) when it is 0, and
the lesser of G and J (amount K) when it is 1. The count is a whole number, so nothing is rounded.
The line 7 amount is `ca/amt_minimum_tax_after_regular_tax`.
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
FAMILY = "ca/itc_part_d_amount_11_conditions"
T2038_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2038-ind/t2038-ind-25e.pdf"

# Made up for this test and not registered: the amount tested, and the count it gives.
PART_5_LINE_7 = ArtifactKind("ex/amt_part_5_line_7", Decimal)
APPLIES = ArtifactKind("ex/itc_part_d_amount_11_applies", int)


def test_2025_t691_part_5_line_7_is_greater_than_0_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "T691 Part 5 line 7 is greater than 0",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    # The count is 1 when the condition applies and 0 when it does not.
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T2038_PDF in data.sources


@pytest.mark.parametrize(
    ("part_5_line_7", "count"),
    [
        # Part 5 line 7 is positive: the condition applies, so the count is 1 and the claim is
        # limited by amount K, not amount I.
        ("28904.25", 1),
        ("0.01", 1),
        # Part 5 line 7 is 0 (AMT does not apply): the count is 0 and the claim is limited by I.
        ("0", 0),
    ],
)
def test_counts_1_when_part_5_line_7_is_greater_than_0_and_0_otherwise(
    part_5_line_7: str, count: int
) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS), (), (PART_5_LINE_7,), APPLIES
    )

    result = capability.compute((Artifact(PART_5_LINE_7, D(part_5_line_7)),)).outputs

    assert result == (Artifact(APPLIES, count),)
