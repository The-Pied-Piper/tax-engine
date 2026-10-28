"""The 2025 condition under which Form T1032 line 29 has an amount to multiply.

Form T1032 E (25), Step 4 Part A, page 3: "Line 29: Line 27 multiplied by line 28 =" with line 28
"Amount from line 24" (line 22). The count is 1 when the amount from line 22 is above 0 and 0
otherwise. The count is a whole number, so nothing is rounded.
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
FAMILY = "ca/t1032_note_1_line_29_applies_conditions"
T1032_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.pdf"

# Made up for this test and not registered: the amount tested and the count given.
LINE_22 = ArtifactKind("ex/t1032_note_1_line_22", Decimal)
APPLIES = ArtifactKind("ex/t1032_note_1_line_29_applies", int)


def test_2025_an_amount_on_line_22_above_0_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "the amount from line 22 is above 0",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T1032_PDF in data.sources


@pytest.mark.parametrize(("line_22", "count"), [("0.00", 0), ("0.01", 1), ("1600.00", 1)])
def test_counts_1_when_line_22_is_above_0(line_22: str, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (), (LINE_22,), APPLIES)

    outputs = capability.compute((Artifact(LINE_22, D(line_22)),)).outputs

    assert outputs == (Artifact(APPLIES, count),)
