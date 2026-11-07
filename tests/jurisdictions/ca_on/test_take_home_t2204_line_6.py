"""T2204 (2025) line 6, the line 4 plus line 5, as the Ontario take-home manifest part wires it.

T2204 line 6: "Line 4 plus line 5 = 6". Line 4 (`ca/t2204_premiums_deducted`) is the premiums
deducted, produced by another ticket (#207), so the test header declares it as a required starting
input. Line 5 (`ca/t2204_line_5`, "Residents of other than Quebec (amount from line 9 of Schedule
13)") is the self-employed EI premium a salary-only caller never has: an optional input, read as
blank when left out, and a blank line 5 is read as 0 by the part, which the trace records as a
fallback. A blank line 4 is still refused.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them.
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
from tax_engine.domain.blank import BLANK
from tax_engine.domain.errors import BlankNotAllowedError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankFallbackLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_5,
    T2204_LINE_6,
    T2204_PREMIUMS_DEDUCTED,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "t2204_line_6.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_premiums_deducted
        required: true
      - name: ca/t2204_line_5
        required: false
        default: null
        basis: "Residents of other than Quebec (amount from line 9 of Schedule 13)"
    outputs:
      - ca/t2204_premiums_deducted
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_6
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "c_line_6.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def t2204(tmp_path: Path, starting: list[Artifact[Decimal]]) -> Worksheet:
    """The T2204 worksheet for the starting artifacts given; line 5 is left out unless given."""
    (sheet,) = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *starting)["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_4", "expected"),
    [
        ("1077.48", "1077.48"),
        ("1148.00", "1148.00"),
        ("32.96", "32.96"),
        ("0", "0.00"),
    ],
)
def test_line_6_is_line_4_when_line_5_is_left_blank(
    tmp_path: Path, line_4: str, expected: str
) -> None:
    sheet = t2204(tmp_path, [Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4))])

    assert sheet.get(T2204_LINE_6).value == D(expected)


@pytest.mark.parametrize(
    ("line_4", "line_5", "expected"),
    [
        ("32.96", "10.00", "42.96"),
        ("1077.48", "10.00", "1087.48"),
    ],
)
def test_line_6_adds_line_5_to_line_4_when_line_5_is_given(
    tmp_path: Path, line_4: str, line_5: str, expected: str
) -> None:
    sheet = t2204(
        tmp_path,
        [
            Artifact(T2204_PREMIUMS_DEDUCTED, D(line_4)),
            Artifact(T2204_LINE_5, D(line_5)),
        ],
    )

    assert sheet.get(T2204_LINE_6).value == D(expected)


def test_a_blank_line_5_is_traced_as_a_fallback_of_0(tmp_path: Path) -> None:
    sheet = t2204(tmp_path, [Artifact(T2204_PREMIUMS_DEDUCTED, D("32.96"))])

    assert BlankFallbackLine(T2204_LINE_5, D("0")) in sheet.trace


def test_a_blank_line_4_is_still_refused(tmp_path: Path) -> None:
    with pytest.raises(BlankNotAllowedError, match="may not be left blank"):
        t2204(tmp_path, [Artifact(T2204_PREMIUMS_DEDUCTED, BLANK)])
