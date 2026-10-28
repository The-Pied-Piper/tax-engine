"""The 2025 condition under which Form T1032 line 27 divides by 0.

Form T1032 E (25), Step 4 Part A, page 3: "Line 27: Line 25 divided by line 26 =" with Note 1
"use that result as the amount for line 17" (line 26). The count is 1 when the amount from line 26
is 0 and 0 otherwise. The count is a whole number, so nothing is rounded.
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
FAMILY = "ca/t1032_note_1_line_17_is_zero_conditions"
T1032_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.pdf"

# Made up for this test and not registered: the amount tested and the count given.
LINE_26 = ArtifactKind("ex/t1032_note_1_line_26", Decimal)
APPLIES = ArtifactKind("ex/t1032_note_1_line_17_is_zero", int)


def test_2025_an_amount_on_line_26_of_0_is_the_one_condition() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "the amount from line 26 is 0",
                (ConditionPart((ConditionTest("amount", 1, "equal_to", D("0"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T1032_PDF in data.sources


@pytest.mark.parametrize(
    ("line_26", "count"), [("0.00", 1), ("0.01", 0), ("-500.00", 0), ("1600.00", 0)]
)
def test_counts_1_only_when_line_26_is_0(line_26: str, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (), (LINE_26,), APPLIES)

    outputs = capability.compute((Artifact(LINE_26, D(line_26)),)).outputs

    assert outputs == (Artifact(APPLIES, count),)
