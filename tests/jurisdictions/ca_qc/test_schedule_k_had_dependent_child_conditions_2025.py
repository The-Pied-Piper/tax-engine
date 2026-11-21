"""The 2025 `ca-qc/schedule_k_had_dependent_child_conditions` dataset (Schedule K, Part A, line 44).

Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A, line 44: "If you did not have a spouse on
December 31, 2025, but you had a dependent child (see line 447 in the guide for the definition),
enter $12,350. If you had more than one dependent child, enter $16,570." The dataset holds one
condition, the number of dependent children (the first count) is more than 0. The count is 1 when
it applies and 0 when it does not. It is a count, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import CountKind
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
FAMILY = "ca-qc/schedule_k_had_dependent_child_conditions"
SOURCE_FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part A"

# Made up for this test and not registered: the number of children and the count it gives.
CHILDREN = CountKind("ex/children")
APPLIES = CountKind("ex/applies")


def test_2025_condition_is_at_least_one_dependent_child() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "At least one dependent child",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(0), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_2025_condition_cites_the_form_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.sources == (SOURCE_FORM,)
    assert data.rounding == NO_ROUNDING


def test_2025_condition_reads_one_count_and_no_amount() -> None:
    values = SOURCE.get(FAMILY, 2025, CONDITIONS).values

    assert values.count_positions_read == frozenset({1})
    assert values.amount_positions_read == frozenset()


@pytest.mark.parametrize(("children", "count"), [(0, 0), (1, 1), (2, 1), (3, 1), (10, 1)])
def test_the_count_is_1_when_the_condition_applies_and_0_otherwise(
    children: int, count: int
) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (CHILDREN,), (), APPLIES)

    result = capability.compute((Artifact(CHILDREN, children),)).outputs

    assert result == (Artifact(APPLIES, count),)
