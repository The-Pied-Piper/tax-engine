"""The T1 employment income form (5006-R, 2025, lines 10100 and 10400) as the Ontario take-home
manifest parts wire it.

The form is its own, apart from the taxable income form, so that Schedule 8 line 1 can read line
10100 from it while the taxable income form reads Schedule 8 (line 22215): had both lived in one
form, the two forms would need each other. The part names the form and exports both lines.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import (
    EMPLOYMENT_INCOME,
    EMPLOYMENT_INCOME_LINE_10100,
    OTHER_EMPLOYMENT_INCOME,
    OTHER_EMPLOYMENT_INCOME_LINE_10400,
)
from tests.jurisdictions.ca_on.conftest import TakeHomeService

D = Decimal
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
PARTS = (
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10100_inputs.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)


def test_the_form_exports_lines_10100_and_10400_and_holds_them_at_70000(
    take_home_service: TakeHomeService,
) -> None:
    service = take_home_service(HEADER, "{}\n", *PARTS)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == "ca/t1_employment_income")
    assert form.exports == (EMPLOYMENT_INCOME_LINE_10100, OTHER_EMPLOYMENT_INCOME_LINE_10400)

    worksheets = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    (sheet,) = worksheets["ca/t1_employment_income"]

    assert [sheet.get(kind).value for kind in form.exports] == [D("70000.00"), D("0.00")]


def test_line_10400_is_the_amount_given(take_home_service: TakeHomeService) -> None:
    service = take_home_service(HEADER, "{}\n", *PARTS)

    worksheets = service.compute(
        JurisdictionCode("CA-ON"),
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(OTHER_EMPLOYMENT_INCOME, D("1500")),
    )
    (sheet,) = worksheets["ca/t1_employment_income"]

    assert sheet.get(OTHER_EMPLOYMENT_INCOME_LINE_10400).value == D("1500.00")
