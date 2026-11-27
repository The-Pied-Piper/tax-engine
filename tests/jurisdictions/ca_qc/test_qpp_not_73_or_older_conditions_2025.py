"""Schedule 8 (5005-S8) Part 1 line A condition c), 2025: 73 or older at the end of 2025 gives 0.

The dataset `ca-qc/qpp_not_73_or_older_conditions` has one condition on the year of birth: born
after 1952 gives the count 1 (months kept), anything else 0. It is a count, so nothing is rounded.
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
FAMILY = "ca-qc/qpp_not_73_or_older_conditions"
YEAR = 2025
CRA_FORM_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5005-s8/5005-s8-25e.txt"

# Made up for this test and not registered: the year of birth and the count it gives.
BIRTH_YEAR = CountKind("ex/birth_year")
KEPT = CountKind("ex/months_kept")


def test_the_condition_is_a_birth_year_after_1952_and_gives_1() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "You were born after 1952",
                (ConditionPart((ConditionTest("count", 1, "more_than", D(1952), None),)),),
            ),
        ),
    )
    assert data.values.count_when_none_applies == 0


def test_the_dataset_cites_the_form_and_does_not_round() -> None:
    data = SOURCE.get(FAMILY, YEAR, CONDITIONS)

    assert data.sources == (CRA_FORM_TEXT,)
    assert data.rounding == NO_ROUNDING


@pytest.mark.parametrize(("year", "count"), [(1922, 0), (1952, 0), (1953, 1), (1982, 1)])
def test_the_count_by_birth_year(year: int, count: int) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, YEAR, CONDITIONS), (BIRTH_YEAR,), (), KEPT)

    (output,) = capability.compute((Artifact(BIRTH_YEAR, year),)).outputs

    assert output.kind is KEPT
    assert output.value == count
