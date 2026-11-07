"""ON428 (2025) line 9, the basic personal amount, as the Ontario take-home manifest part wires it.

Form text (Form ON428, CRA 5006-c-25e.txt): "Line 9 and line 58040: Basic personal amount
Claim $12,747". The amount is the `ca-on/basic_personal_amount` dataset, claimed whole through
core/credit_amount, so it is the same at every salary. Line 9 reads nothing. Line 18 (#269)
reads it later.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. The one exception is the test that the real form header
`on428/on428.yaml` loads: its text is the form declaration of that service build.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_on.catalog import BASIC_PERSONAL_AMOUNT
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
PART = "on428_line_9.yaml"

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
      name: ca-on/on428
      required: true
      exports:
        - ca-on/basic_personal_amount
    """)


def line_9(take_home_service: TakeHomeService, salary: str, form: str = FORM) -> Decimal:
    worksheets = take_home_service(HEADER, form, PART).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-on/on428"]
    return sheet.get(BASIC_PERSONAL_AMOUNT).value


@pytest.mark.parametrize("salary", ["20000", "70000", "150000"])
def test_line_9_is_the_basic_personal_amount_at_every_salary(
    take_home_service: TakeHomeService, salary: str
) -> None:
    assert line_9(take_home_service, salary) == D("12747.00")


def test_the_form_header_declares_on428_and_exports_line_9() -> None:
    header = yaml.safe_load((TAKE_HOME / "on428" / "on428.yaml").read_text(encoding="utf-8"))
    assert header["form"] == {
        "name": "ca-on/on428",
        "required": True,
        "exports": ["ca-on/basic_personal_amount"],
    }
    assert header["capabilities"] == []


def test_the_real_form_header_builds_with_line_9(take_home_service: TakeHomeService) -> None:
    header = (TAKE_HOME / "on428" / "on428.yaml").read_text(encoding="utf-8")
    assert line_9(take_home_service, "70000", header) == D("12747.00")
