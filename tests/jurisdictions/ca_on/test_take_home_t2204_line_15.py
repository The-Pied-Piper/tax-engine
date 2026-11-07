"""T2204 (2025) line 15, the EI overpayment, as the Ontario take-home manifest part wires it.

T2204 line 15: "Employment insurance overpayment: Enter whichever is less: amount from line 9 or
line 14. If this amount is more than $1, enter it on line 45000 of your return." Line 9 is a pure
copy of line 4, so the part reads line 4. The part has three steps: the lesser of line 4 and
line 14 (`ca/t2204_line_15`), the count of the "more than $1" condition
(`ca/t2204_line_15_count`, 1 when it applies, else 0), and line 15 times that count, the T1 line
45000 amount (`ca/ei_overpayment`).

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Line 4 (`ca/t2204_premiums_deducted`) and line 14
(`ca/t2204_line_14`) are produced by other tickets, so the test header declares both as required
starting inputs. `ca/ei_overpayment` is not a form export; it is read from the worksheet.
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
from tax_engine.jurisdictions.ca.catalog.refund import (
    EI_OVERPAYMENT,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_15_COUNT,
    T2204_PREMIUMS_DEDUCTED,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "t2204_line_15.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_premiums_deducted
        required: true
      - name: ca/t2204_line_14
        required: true
    outputs:
      - ca/t2204_premiums_deducted
      - ca/t2204_line_14
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_15
        - ca/t2204_line_15_count
        - ca/ei_overpayment
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "c_line_15.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def t2204(tmp_path: Path, line_4: str, line_14: str) -> Worksheet:
    """The T2204 worksheet for a line 4 and a line 14."""
    starting = [
        Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4)),
        Artifact(T2204_LINE_14, D(line_14)),
    ]
    (sheet,) = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *starting)["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_4", "line_14", "line_15", "count", "overpayment"),
    [
        # Salary 2,010 refund case: line 4 is 32.96, line 14 is 22.96.
        ("32.96", "22.96", "22.96", 1, "22.96"),
        # Salary 1,500 and salary 30,000: both lines are 0.
        ("0", "0", "0", 0, "0"),
        # Return DD oracle (salary 70,000, line 4 given 1,148.00): overpayment 70.52.
        ("1148.00", "70.52", "70.52", 1, "70.52"),
        # Line 4 is the lesser, so line 4 wins.
        ("10.00", "22.96", "10.00", 1, "10.00"),
        # Salary 2,033 case: line 15 is 0.34, not more than $1, so the amount is 0.
        ("33.34", "0.34", "0.34", 0, "0"),
        # Exactly $1.00 is not more than $1: count 0, amount 0.
        ("5.00", "1.00", "1.00", 0, "0"),
        # $1.01 is more than $1: count 1, amount 1.01.
        ("5.00", "1.01", "1.01", 1, "1.01"),
        # Tie: line 4 equals line 14, the value is kept.
        ("22.96", "22.96", "22.96", 1, "22.96"),
        # Salary-only $70,000 take-home case: line 4 is 1,077.48, line 14 is 0.
        ("1077.48", "0", "0", 0, "0"),
    ],
)
def test_line_15_count_and_ei_overpayment(
    tmp_path: Path, line_4: str, line_14: str, line_15: str, count: int, overpayment: str
) -> None:
    sheet = t2204(tmp_path, line_4, line_14)
    assert sheet.get(T2204_LINE_15).value == D(line_15)
    assert sheet.get(T2204_LINE_15_COUNT).value == count
    assert sheet.get(EI_OVERPAYMENT).value == D(overpayment)
