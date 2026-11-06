"""T2204 (2025) line 1, the total EI insurable earnings, as the Ontario take-home manifest part
wires it: the salary, entered as "0" under $2,000 when the note (1) applies.

T2204 line 1: "Total EI insurable earnings (box 24 or, if blank, box 14 of your T4 slips) (1)". Note
(1): "If you have no self-employment earnings and your total EI insurable earnings on your T4 slips
are less than $2,000, enter "0"." The manifest part is loaded from the package. The header, the
salary input and the form's export are made up here, because the shared scaffold owns them. The
caller has no T4, so line 1 reads the salary typed once (T1 line 10100) in place of box 24 or
box 14.

Line 2 is an optional input, read as blank when left out, and a blank line 2 is read as 0 by the
part. The $2,000 of line 7 (`ca/t2204_exemption`) is produced by another ticket (#209), so the test
header declares it as a required starting input, as the Schedule 8 line D test does.
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
    T2204_LINE_1,
    T2204_LINE_1_COUNT,
    T2204_SELF_EMPLOYMENT_EARNINGS,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "t2204_line_1.yaml"
)

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
        - ca/t2204_line_1
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "c_line_1.yaml")
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
    ("salary", "expected"),
    [
        # Under $2,000 the note applies, so line 1 is "0"; see the count test below.
        ("1500", "0.00"),
        # $2,000 is not less than $2,000, so the note does not apply and line 1 is the salary.
        ("2000", "2000.00"),
        ("2010", "2010.00"),
        ("70000", "70000.00"),
        # Not capped on this line: the salary is entered as it is.
        ("90000", "90000.00"),
    ],
)
def test_line_1_is_the_salary_unless_the_note_applies(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert t2204(tmp_path, salary).get(T2204_LINE_1).value == D(expected)


@pytest.mark.parametrize(
    ("salary", "count"),
    [
        # The note's count is 0 when it applies (under $2,000) and 1 otherwise.
        ("1500", "0"),
        ("2000", "1"),
        ("2010", "1"),
        ("70000", "1"),
        ("90000", "1"),
    ],
)
def test_the_note_count_is_0_under_2000_and_1_from_2000(
    tmp_path: Path, salary: str, count: str
) -> None:
    assert t2204(tmp_path, salary).get(T2204_LINE_1_COUNT).value == int(count)


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 2 left out is read as its blank, which the part reads as 0: the note applies.
        ("1500", "0.00"),
        # And from $2,000 up the note does not apply, so line 1 is the salary.
        ("2000", "2000.00"),
    ],
)
def test_a_blank_line_2_is_read_as_0(tmp_path: Path, salary: str, expected: str) -> None:
    assert t2204(tmp_path, salary).get(T2204_LINE_1).value == D(expected)


def test_self_employment_earnings_switch_the_note_off(tmp_path: Path) -> None:
    # Line 2 is 100, so the caller has self-employment earnings and note (1) does not apply: line 1
    # is the salary of $1,500, though it is under $2,000, and the count is 1.
    sheet = t2204(tmp_path, "1500", self_employment="100")

    assert sheet.get(T2204_LINE_1).value == D("1500.00")
    assert sheet.get(T2204_LINE_1_COUNT).value == 1
