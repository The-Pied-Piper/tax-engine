"""The 2026 conditions of NS428's "born in 1960 or earlier" count, checked against CRA's NS428 text.

Form NS428 (5003-c-25e.txt) line 10 and line 98: "if you were born in 1960 or earlier". The dataset
`ca-ns/born_in_1960_or_earlier_conditions` has one condition on the year of birth (count 1), turned
round because conditions only test "more than": born after 1960 gives the count 0, anything else 1.
It is a count, so nothing is rounded.
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
from tests.jurisdictions.ca_ns.support import nova_scotia_packages, nova_scotia_parameter_parsers

D = Decimal
SOURCE = YamlParameterSource(nova_scotia_packages().roots(), nova_scotia_parameter_parsers())
FAMILY = "ca-ns/born_in_1960_or_earlier_conditions"
YEAR = 2026
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt"

# Made up for this test and not registered: the year of birth and the count it gives.
BIRTH_YEAR = CountKind("ex/birth_year")
BORN = CountKind("ex/born_in_1960_or_earlier")


def test_the_condition_is_a_birth_year_after_1960_and_gives_0() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "You were born after 1960",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(1960), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_the_dataset_cites_the_form_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.sources == (CRA_FORM_TEXT,)
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(("year", "count"), [(1925, 1), (1959, 1), (1960, 1), (1961, 0), (1990, 0)])
def test_the_count_by_birth_year(year: int, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, YEAR, CONDITIONS), (BIRTH_YEAR,), (), BORN)

    (output,) = capability.compute((Artifact(BIRTH_YEAR, year),)).outputs

    assert output.kind is BORN
    assert output.value == count
