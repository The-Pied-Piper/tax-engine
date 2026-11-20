"""T1 (5006-R, 2025) line 10400, other employment income, as the Ontario manifest parts wire it.

The step is one core/sum over its one input, so the line prints the figure once, with the printed
title and reference, and exports it for the forms that import it.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME_LINE_10400,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
PART = "t1_taxable_income_line_10400.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca/t1_taxable_income
      required: true
      exports:
        - ca/other_employment_income_line_10400
    """)


def line_10400(take_home_service: TakeHomeService, salary: str, other: str | None) -> Decimal:
    artifacts = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if other is not None:
        artifacts.append(Artifact(OTHER_EMPLOYMENT_INCOME, D(other)))
    worksheets = take_home_service(
        HEADER, FORM, "t1_taxable_income_line_10400_inputs.yaml", PART
    ).compute(JurisdictionCode("CA-ON"), 2025, *artifacts)
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet.get(OTHER_EMPLOYMENT_INCOME_LINE_10400).value


@pytest.mark.parametrize(
    ("other", "expected"), [(None, "0"), ("0", "0"), ("1500", "1500.00"), ("300.505", "300.51")]
)
def test_line_10400_is_the_other_income_and_zero_when_none_is_given(
    take_home_service: TakeHomeService, other: str | None, expected: str
) -> None:
    assert line_10400(take_home_service, "70000", other) == D(expected)


def test_line_10400_is_listed_once_with_its_title_and_reference(
    take_home_service: TakeHomeService,
) -> None:
    worksheets = take_home_service(
        HEADER, FORM, "t1_taxable_income_line_10400_inputs.yaml", PART
    ).compute(JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    (sheet,) = worksheets["ca/t1_taxable_income"]
    assert sheet.reference("other_employment_income_line_10400") == "10400"
    assert sheet.reference("other_employment_income") is None
