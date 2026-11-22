"""The 2025 `ca-bc/renters_credit_conditions` dataset: the six-month minimum of the renter's tax
credit, checked against the British Columbia Tax Information for 2025 (CRA 5010-PC).

The guide's section "British Columbia renter's tax credit": "You rented and occupied a rental unit
for at least six months in the calendar year in British Columbia" and "You must be an eligible
renter for at least six months in 2025." The dataset holds one condition on the first count (the
months of BC479 line 37): more than 5, that is at least six whole months. The count is 1 when it
applies and 0 when it does not. It is a count, so nothing is rounded.
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
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
)

D = Decimal
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(), british_columbia_parameter_parsers()
)
FAMILY = "ca-bc/renters_credit_conditions"
GUIDE = "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5010-pc/5010-pc-25e.txt"

# Made up for this test and not registered: the months and the count they give.
MONTHS = CountKind("ex/months")
ENOUGH = CountKind("ex/months_enough")


def test_2025_condition_is_at_least_six_months_of_rent() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "Rented and occupied a rental unit for at least six months",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(5), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_2025_condition_cites_the_guide_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.sources == (GUIDE,)
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(("months", "count"), [(0, 0), (1, 0), (5, 0), (6, 1), (7, 1), (12, 1)])
def test_the_count_is_1_for_at_least_six_months_and_0_for_fewer(months: int, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (MONTHS,), (), ENOUGH)

    result = capability.compute((Artifact(MONTHS, months),)).outputs

    assert result == (Artifact(ENOUGH, count),)
