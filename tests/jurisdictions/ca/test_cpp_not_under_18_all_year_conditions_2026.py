"""Schedule 8 (5000-S8) Part 2 line A, 2026: not yet 18 in any month of 2026 gives 0 months.

Not a printed sentence: condition a) counts the months after the month a filer turned 18, so a
filer who turns 18 in a later year has none. The dataset `ca/cpp_not_under_18_all_year_conditions`
has one condition: born after 2008 gives the count 0, anything else 1. Nothing is rounded.

Provisional: the 2026 form is not published; the cutoff moves one year on from 2025.
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
FAMILY = "ca/cpp_not_under_18_all_year_conditions"
YEAR = 2026
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5000-s8/5000-s8-25e.txt"

# Made up for this test and not registered: the year of birth and the count it gives.
BIRTH_YEAR = CountKind("ex/birth_year")
KEPT = CountKind("ex/months_kept")


def test_the_condition_is_a_birth_year_after_2008_and_gives_0() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.values == ConditionList(
        0,
        (
            Condition(
                "You were born after 2008",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(2008), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 1


def test_the_dataset_cites_the_form_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.sources == (CRA_FORM_TEXT,)
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(("year", "count"), [(1978, 1), (2008, 1), (2009, 0), (2038, 0)])
def test_the_count_by_birth_year(year: int, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, YEAR, CONDITIONS), (BIRTH_YEAR,), (), KEPT)

    (output,) = capability.compute((Artifact(BIRTH_YEAR, year),)).outputs

    assert output.kind is KEPT
    assert output.value == count
