"""The 2025 condition of Form T2017 (2025) page 3, "How do you calculate a reserve", checked against
the printed form.

Form T2017 (2025), page 3: "You do not have to claim the maximum reserve in a tax year (Year A).
However, the amount you claim in a later year (Year B) cannot be more than the amount you claimed
for that property in the previous year (Year A)." The condition "a later year (Year B)" is the
count of years after the disposition being more than 0: a count of 1 for a disposition in any year
after the year of disposition, and 0 for the year of disposition itself. The count is a whole
number, so nothing is rounded. The condition reads the years after the disposition, the count
`ca/t2017_reserve_years_after_disposition`.
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
FAMILY = "ca/t2017_later_year_conditions"
T2017_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2017/t2017-25e.pdf"

# Made up for this test and not registered: the years after the disposition, and the count the
# condition gives.
YEARS = ArtifactKind("ex/years_after_disposition", int)
LATER_YEAR = ArtifactKind("ex/later_year", int)


def test_2025_a_later_year_is_the_one_condition_and_its_count_is_1_when_it_applies() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert data.values == ConditionList(
        1,
        (
            Condition(
                "a later year (Year B)",
                (ConditionPart((ConditionTest("count", 1, "more_than", D("0"), None),)),),
            ),
        ),
    )
    # The count is 1 when the condition applies and 0 when it does not.
    assert data.values.count_when_none_applies == 0
    assert data.values.count_positions_read == frozenset({1})
    assert data.values.amount_positions_read == frozenset()
    # A count, not the amount of a line: nothing is rounded.
    assert data.rounding == NO_ROUNDING


def test_2025_the_condition_cites_the_form_it_is_printed_on() -> None:
    data = SOURCE.get(FAMILY, 2025, CONDITIONS)

    assert T2017_PDF in data.sources


@pytest.mark.parametrize(
    ("years", "count"),
    [
        # The year of disposition (Year A) is not a later year: count 0.
        (0, 0),
        # Every year after it is a later year (Year B): count 1, through the 9th year.
        (1, 1),
        (2, 1),
        (4, 1),
        (9, 1),
    ],
)
def test_counts_1_for_a_later_year_and_0_for_the_year_of_disposition(
    years: int, count: int
) -> None:
    capability = CountByConditions(SOURCE.get(FAMILY, 2025, CONDITIONS), (YEARS,), (), LATER_YEAR)

    result = capability.compute((Artifact(YEARS, years),)).outputs

    assert result == (Artifact(LATER_YEAR, count),)
