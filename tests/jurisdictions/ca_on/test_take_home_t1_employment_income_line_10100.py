"""T1 (5006-R, 2025) line 10100, employment income, as the Ontario take-home manifest parts wire it.

The step is one core/sum over its one input, carried as it is (the form prints no rounding on this
line), so the line prints the figure once, with the printed
title and reference, and exports it for the forms that import it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import SubCentAmountError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    EMPLOYMENT_INCOME_LINE_10100,
    OTHER_EMPLOYMENT_INCOME,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "t1_employment_income_line_10100.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca/t1_employment_income
      required: true
      exports:
        - ca/employment_income_line_10100
    inputs:
      - name: ca/employment_income
        required: true
    """)


def line_10100(take_home_service: TakeHomeService, salary: str, other: str | None) -> Decimal:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if other is not None:
        artifacts.append(Artifact(OTHER_EMPLOYMENT_INCOME, D(other)))
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, *artifacts
    )
    (sheet,) = worksheets["ca/t1_employment_income"]
    return sheet.get(EMPLOYMENT_INCOME_LINE_10100).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("70000", "70000.00"), ("0", "0"), ("1000.5", "1000.50"), ("70000.01", "70000.01")],
)
def test_line_10100_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    assert line_10100(take_home_service, salary, None) == D(expected)


@pytest.mark.parametrize("salary", ["70000.004", "70000.005", "1999.995"])
def test_a_salary_with_a_fraction_of_a_cent_is_refused(
    take_home_service: TakeHomeService, salary: str
) -> None:
    with pytest.raises(SubCentAmountError, match="ca/employment_income must be in whole cents"):
        line_10100(take_home_service, salary, None)


def test_line_10100_is_listed_once_with_its_title_and_reference(
    take_home_service: TakeHomeService,
) -> None:
    worksheets = take_home_service(HEADER, FORM, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000"))
    )
    (sheet,) = worksheets["ca/t1_employment_income"]
    assert sheet.reference("employment_income_line_10100") == "10100"
    assert sheet.title("employment_income_line_10100") == "Employment income"
