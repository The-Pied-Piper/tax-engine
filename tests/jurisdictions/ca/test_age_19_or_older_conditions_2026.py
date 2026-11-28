"""The 2026 conditions of the "aged 19 or older" count, checked against the BC and Manitoba guides.

BC guide 5010-PC (Form BC479, Sales tax credit): "You were 19 years of age or older". Manitoba
guide 5007-PC (Form MB479, Personal tax credit): "If you were under 19 years of age at the end
of the year, you can only claim this credit if one of the following applies to you". The dataset
`ca/age_19_or_older_conditions` has one condition on the year of birth (count 1), turned round
because conditions only test "more than": born after 2007 (under 19 on 31 December 2026) gives the
count 0, anything else 1.
The dataset is provisional (no 2026 guide yet): the 2025 year moves on by one.
It is a count, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
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

D = Decimal
SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
FAMILY = "ca/age_19_or_older_conditions"
YEAR = 2026
SOURCES = (
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5010-pc/5010-pc-25e.txt",
    "https://www.canada.ca/content/dam/cra-arc/formspubs/pub/5007-pc/5007-pc-25e.txt",
)

# Made up for this test and not registered: the year of birth and the count it gives.
BIRTH_YEAR = CountKind("ex/birth_year")
AGED_19 = CountKind("ex/aged_19_or_older")


def test_the_condition_is_a_birth_year_after_2007_and_gives_0() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "You were born after 2007",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(2007), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_the_dataset_cites_the_guides_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.sources == SOURCES
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(
    ("year", "count"), [(1925, 1), (2007 - 1, 1), (2007, 1), (2007 + 1, 0), (2007 + 4, 0)]
)
def test_the_count_by_birth_year(year: int, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, YEAR, CONDITIONS), (BIRTH_YEAR,), (), AGED_19)

    (output,) = capability.compute((Artifact(BIRTH_YEAR, year),)).outputs

    assert output.kind is AGED_19
    assert output.value == count
