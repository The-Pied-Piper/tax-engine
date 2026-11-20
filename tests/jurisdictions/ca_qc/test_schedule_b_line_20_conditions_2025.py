"""The 2025 condition of Schedule B line 20's count, checked against the printed form.

Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part A: "You are not entitled to any of these
amounts if you had a spouse on December 31, 2025, and the amount on line 18 is more than $90,027,
or if you did not have a spouse on December 31, 2025, and the amount on line 18 is more than
$64,699." The dataset `ca-qc/schedule_b_line_20_conditions` copies the second condition, the one the
single-filer take-home reads. The count is 0 when the condition applies (the amount on line 18 is
more than 64,699) and 1 when it does not. The spouse condition is not in this dataset.

The count is a whole number, not a dollars-and-cents box, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

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
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/schedule_b_line_20_conditions"
SOURCE_FORM = "Revenu Quebec TP-1.D.B-V (2025-12), Schedule B, Part A"

# Made up for this test and not registered: the amount on line 18 and the count it gives.
LINE_18 = AmountKind("ex/schedule_b_line_18")
GATE_COUNT = CountKind("ex/schedule_b_gate_count")


def test_2025_line_20_conditions_is_one_condition_on_line_18_and_counts_0_when_it_applies() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "You did not have a spouse on December 31, 2025, and the amount on line 18 is "
                "more than $64,699",
                (ConditionPart((ConditionTest("amount", 1, "more_than", D("64699"), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_2025_line_20_conditions_reads_one_amount_and_no_count() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.amount_positions_read == frozenset({1})
    assert values.count_positions_read == frozenset()


def test_2025_line_20_conditions_cite_the_form() -> None:
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).sources == (SOURCE_FORM,)


def test_2025_line_20_conditions_do_not_round() -> None:
    # A count, not the amount of a line: nothing is rounded.
    assert SOURCE.get(FAMILY, 2025, CONDITIONS).rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("line_18", "count"),
    [
        ("0", 1),
        ("25825", 1),
        # Exactly $64,699 is not "more than $64,699": the gate does not apply.
        ("64699", 1),
        ("64699.00", 1),
        ("64699.01", 0),
        ("155416", 0),
    ],
)
def test_2025_line_20_conditions_count_by_the_amount_on_line_18(line_18: str, count: int) -> None:
    capability = CountByConditions(
        SOURCE.get(FAMILY, 2025, CONDITIONS),
        (),
        (LINE_18,),
        GATE_COUNT,
    )

    result = capability.compute((Artifact(LINE_18, D(line_18)),)).outputs

    assert result == (Artifact(GATE_COUNT, count),)
