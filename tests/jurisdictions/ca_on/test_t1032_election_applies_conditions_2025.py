"""The 2025 condition that the Form T1032 election applies, checked against Form T1032.

Form T1032 E (25), Step 3, "Line 22: Enter the amount that you and your spouse or common-law
partner decide to jointly elect to be your split-pension amount for the year." The form is filed
only when a split-pension amount is elected, so the condition "line 22 is above 0" is a count of 1
when line 22 is more than 0 and 0 otherwise. It switches T1 line 43700 and line 31400 to the
amounts of the form. The count is a whole number, so nothing is rounded.
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
FAMILY = "ca/t1032_election_applies_conditions"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"

# Made up for this test and not registered: the amount tested, and the count it gives.
LINE_22 = ArtifactKind("ex/t1032_line_22", Decimal)
APPLIES = ArtifactKind("ex/t1032_election_applies", int)


def test_2025_line_22_above_0_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "line 22 is above 0",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset()
    assert data.values.amount_positions_read == frozenset({1})
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T1032_TXT in data.sources


@pytest.mark.parametrize(
    ("line_22", "count"),
    [
        ("10000.00", 1),
        ("0.01", 1),
        # No elected amount: no election, the T1032 is not filed.
        ("0", 0),
        ("0.00", 0),
    ],
)
def test_counts_1_when_line_22_is_above_0_and_0_otherwise(line_22: str, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (), (LINE_22,), APPLIES)

    result = capability.compute((Artifact(LINE_22, D(line_22)),)).outputs

    assert result == (Artifact(APPLIES, count),)
