"""Worksheet AB428 (2025) line 6, the base amount, as the Alberta manifest part wires it.

Form text (CRA 5009-d-25e.txt): "Line 6: Base amount 4,800.00". The amount is the
`ca-ab/supplemental_credit_base` dataset, claimed whole through core/credit_amount, so it is the
same at every salary. Line 6 reads nothing.

The manifest part is loaded from the package. The header and the manifest's outputs are made up
here, because the end-to-end scaffold owns them.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_ab
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.trace import CreditAmountLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_service

D = Decimal
LINE_6 = alberta_kinds().kind("ca-ab/worksheet_ab428_line_6")
# The part is the whole of this manifest, so its worksheet is the default form's.
RETURN_FORM = "ca-ab/return"
PART = (
    Path(tax_engine.jurisdictions.ca_ab.__file__).parent
    / "manifests"
    / "2025"
    / "worksheet_ab428_line_6.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    inputs:
      - name: ca/employment_income
        required: true
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
      - ca-ab/worksheet_ab428_line_6
    """)


def manifest() -> str:
    """The test header and form, then the real part's capabilities."""
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    return HEADER + yaml.safe_dump({"capabilities": part["capabilities"]}, sort_keys=False)


def line_6(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = alberta_service(tmp_path, manifest()).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[RETURN_FORM]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_6_is_the_base_amount_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_6(tmp_path, salary).get(LINE_6).value == D("4800.00")


def test_line_6_is_one_credit_amount_trace_line(tmp_path: Path) -> None:
    (line,) = line_6(tmp_path, "70000").trace

    assert isinstance(line, CreditAmountLine)
    assert line.value == D("4800.00")
