"""T2204 (2025) line 3, the insurable earnings, as the Ontario take-home manifest part wires it:
line 1 plus line 2, capped at the maximum.

T2204 line 3: "Line 1 plus line 2 (maximum $65,700)". The manifest part is loaded from the package,
together with the line 1 part, because line 3 reads line 1. The header, the salary input and the
form's export are made up here, because the shared scaffold owns them. The caller has no T4, so
line 1 reads the salary typed once (T1 line 10100), as the line 1 test describes.

Line 2 is an optional input, read as blank when left out, and a blank line 2 counts as 0. The
$2,000 of line 7 (`ca/t2204_exemption`) is produced by another ticket (#209), so the test header
declares it as a required starting input, as the line 1 test does.
"""

from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_on
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_EXEMPTION,
    T2204_LINE_1_PLUS_2,
    T2204_LINE_3,
    T2204_SELF_EMPLOYMENT_EARNINGS,
)

D = Decimal
TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"
PART = TAKE_HOME / "t2204_line_3.yaml"
LINE_1_PART = TAKE_HOME / "t2204_line_1.yaml"

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca/t2204_exemption
        required: true
      - name: ca/t2204_self_employment_earnings
        required: false
        default: null
        basis: "Total self-employment and other earnings eligible for the EI program
          for access to EI special benefits"
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_3
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(LINE_1_PART, parts / "c_line_1.yaml")
    shutil.copy(PART, parts / "d_line_3.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def t2204(tmp_path: Path, salary: str, self_employment: str | None = None) -> Worksheet:
    """The T2204 worksheet for a salary; line 2 is left out unless it is given."""
    starting = [
        Artifact(EMPLOYMENT_INCOME, D(salary)),
        Artifact(T2204_EXEMPTION, D("2000.00")),
    ]
    if self_employment is not None:
        starting.append(Artifact(T2204_SELF_EMPLOYMENT_EARNINGS, D(self_employment)))
    (sheet,) = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *starting)["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "self_employment", "expected"),
    [
        # Line 2 left out: line 1 is 70,000, above the maximum, so line 3 is the maximum.
        ("70000", None, "65700.00"),
        # Line 2 given: line 1 plus line 2 is still above the maximum.
        ("70000", "1148", "65700.00"),
        # Under the maximum, line 3 is the salary.
        ("30000", None, "30000.00"),
        ("2010", None, "2010.00"),
        # Under $2,000 with line 2 left out, note (1) makes line 1 "0", so line 3 is 0.
        ("1500", None, "0.00"),
        # Line 2 of 100 switches note (1) off: line 1 is 1,500, and line 3 is 1,500 plus 100.
        ("1500", "100", "1600.00"),
    ],
)
def test_line_3_is_line_1_plus_line_2_up_to_the_maximum(
    tmp_path: Path, salary: str, self_employment: str | None, expected: str
) -> None:
    sheet = t2204(tmp_path, salary, self_employment)

    assert sheet.get(T2204_LINE_3).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "self_employment", "expected"),
    [
        # Before the cap: line 1 is the salary, and the sum is not limited to 65,700.
        ("70000", None, "70000.00"),
        # Line 2 of 100 switches note (1) off, so line 1 is 1,500 and the sum is 1,600.
        ("1500", "100", "1600.00"),
    ],
)
def test_line_1_plus_line_2_is_the_sum_before_the_cap(
    tmp_path: Path, salary: str, self_employment: str | None, expected: str
) -> None:
    sheet = t2204(tmp_path, salary, self_employment)

    assert sheet.get(T2204_LINE_1_PLUS_2).value == D(expected)


@pytest.mark.parametrize("self_employment", [None, "0"], ids=["left_out", "given_as_0"])
def test_a_blank_line_2_counts_as_0(tmp_path: Path, self_employment: str | None) -> None:
    # Left out, line 2 is read as blank, and the part reads that blank as 0: the same sums as
    # an explicit 0.
    sheet = t2204(tmp_path, "70000", self_employment)

    assert sheet.get(T2204_LINE_1_PLUS_2).value == D("70000.00")
    assert sheet.get(T2204_LINE_3).value == D("65700.00")
