"""Schedule 8 (5000-S8, 2025) Part 2 line A, the number of months that CPP applied, from the
typed months and the optional year of birth (`ca/birth_year`, the T1's input).

Form text: "Enter "12" on line A below unless any of the following conditions apply: ... g) You were
70 years of age or older for all of 2025. Enter "0" on line A". "If more than one condition above
applies to you, calculate the number of months based on the combined conditions". The year of birth
gives only the whole-year cases (born in 1954 or earlier, born in 2008 or later: 0); the months of
every other filer stay as typed, 12 when left out. The manifest part is loaded from the package;
the header, the form's export and the typed months input are made up here.
"""

from __future__ import annotations

from textwrap import dedent

import pytest

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.deductions import CPP_MONTHS, CPP_MONTHS_LINE_A
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService

PART = "schedule_8_line_a.yaml"
PARTS = (*form_part_names("t1_lines_copied_by_provinces"), PART)
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    """)
FORM = dedent("""\
    form:
      name: ca/schedule_8
      required: true
      exports:
        - ca/cpp_months_line_a
    inputs:
      - name: ca/cpp_months
        required: false
        default: "12"
        basis: 'Enter "12" on line A below unless any of the following conditions apply'
    """)


def line_a(
    take_home_service: TakeHomeService, months: int | None = None, birth_year: int | None = None
) -> int:
    given: list[Artifact[int]] = []
    if months is not None:
        given.append(Artifact(CPP_MONTHS, months))
    if birth_year is not None:
        given.append(Artifact(BIRTH_YEAR, birth_year))
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        TaxCalculationRequest(JurisdictionCode("CA-ON"), 2025, tuple(given))
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(CPP_MONTHS_LINE_A).value


def test_line_a_is_12_when_nothing_is_given(take_home_service: TakeHomeService) -> None:
    assert line_a(take_home_service) == 12


def test_line_a_is_the_typed_months_without_a_year(take_home_service: TakeHomeService) -> None:
    assert line_a(take_home_service, months=5) == 5


@pytest.mark.parametrize("year", [1954, 1930, 2008, 2015])
def test_line_a_is_0_for_70_or_older_or_under_18_all_year(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert line_a(take_home_service, birth_year=year) == 0


@pytest.mark.parametrize("year", [1955, 1956, 1990, 2007])
def test_line_a_keeps_the_typed_months_for_every_other_year_of_birth(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert line_a(take_home_service, months=5, birth_year=year) == 5


@pytest.mark.parametrize("year", [1955, 1956, 1990, 2007])
def test_line_a_is_12_for_every_other_year_of_birth_with_no_months_typed(
    take_home_service: TakeHomeService, year: int
) -> None:
    assert line_a(take_home_service, birth_year=year) == 12


def test_the_combined_conditions_a_zero_from_the_year_wins_over_typed_months(
    take_home_service: TakeHomeService,
) -> None:
    assert line_a(take_home_service, months=12, birth_year=1950) == 0
