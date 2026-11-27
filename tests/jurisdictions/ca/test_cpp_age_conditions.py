"""The two whole-year age conditions of Schedule 8 Part 2 line A, from the year of birth.

`ca/cpp_not_70_or_older_all_year_conditions` is 0 for a filer 70 or older for all of the year
(condition g), "Enter "0" on line A"); `ca/cpp_not_under_18_all_year_conditions` is 0 for a filer
not yet 18 in any month of the year. 2025: born in 1954 or earlier, born in 2008 or later. 2026:
born in 1955 or earlier, born in 2009 or later. The years that turn 70 or 18 during the year (born
1955 and 2007 in 2025) are the filer's typed months. Counts, so nothing is rounded.
"""

from __future__ import annotations

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import CountKind
from tax_engine.domain.parameters.conditions import CONDITIONS
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.jurisdictions.ca.capabilities.count_by_conditions import CountByConditions

SOURCE = YamlParameterSource(
    tax_engine.registrations.JURISDICTIONS.roots(), tax_engine.registrations.parameter_parsers()
)
YEAR_KIND = CountKind("ex/birth_year")
FLAG = CountKind("ex/flag")
OLD = "ca/cpp_not_70_or_older_all_year_conditions"
YOUNG = "ca/cpp_not_under_18_all_year_conditions"


def _count(family: str, tax_year: int, birth_year: int) -> int:
    data = SOURCE.get(family, tax_year, CONDITIONS)
    assert data.rounding == NO_ROUNDING
    capability = CountByConditions(data, (YEAR_KIND,), (), FLAG)
    (output,) = capability.compute((Artifact(YEAR_KIND, birth_year),)).outputs
    assert isinstance(output.value, int)
    return output.value


@pytest.mark.parametrize(
    ("tax_year", "birth_year", "expected"),
    [(2025, 1954, 0), (2025, 1930, 0), (2025, 1955, 1), (2026, 1955, 0), (2026, 1956, 1)],
)
def test_the_70_or_older_all_year_flag(tax_year: int, birth_year: int, expected: int) -> None:
    assert _count(OLD, tax_year, birth_year) == expected


@pytest.mark.parametrize(
    ("tax_year", "birth_year", "expected"),
    [(2025, 2007, 1), (2025, 2008, 0), (2026, 2008, 1), (2026, 2009, 0), (2026, 1990, 1)],
)
def test_the_not_yet_18_all_year_flag(tax_year: int, birth_year: int, expected: int) -> None:
    assert _count(YOUNG, tax_year, birth_year) == expected
