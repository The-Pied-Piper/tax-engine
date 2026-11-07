"""T2204 (2025) line 7, the amount from line 3 less $2,000, as the Ontario take-home manifest part
wires it: the exemption (`ca/t2204_exemption`) and the difference, not below zero.

T2204 line 7: "Amount from line 3 – $2,000 = (if negative, enter "0")". The manifest part is loaded
from the package. The header and the form's export are made up here, because the shared scaffold
owns them. Line 3 (`ca/t2204_line_3`) is produced by another ticket (#206), so the test header
declares it as a required starting input, as the Schedule 8 line D test does.

The $2,000 is the `ca/t2204_exemption` dataset, claimed whole through core/credit_amount.
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
    T2204_EXEMPTION,
    T2204_LINE_3,
    T2204_LINE_7,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "t2204_line_7.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/t2204_line_3
        required: true
    outputs:
      - ca/t2204_line_3
    """)
FORM = dedent("""\
    form:
      name: ca/t2204
      required: true
      exports:
        - ca/t2204_line_7
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "a_header.yaml").write_text(HEADER)
    (parts / "b_form.yaml").write_text(FORM)
    shutil.copy(PART, parts / "c_line_7.yaml")
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def t2204(tmp_path: Path, line_3: str) -> Worksheet:
    """The T2204 worksheet for a line 3."""
    starting = [Artifact(T2204_LINE_3, D(line_3))]
    (sheet,) = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *starting)["ca/t2204"]
    return sheet


@pytest.mark.parametrize(
    ("line_3", "expected"),
    [
        # The maximum of line 3, $65,700, less $2,000.
        ("65700", "63700.00"),
        # Under $2,000 the difference is negative, so line 7 is "0".
        ("1500", "0.00"),
        ("2010", "10.00"),
        # Exactly $2,000: the difference is 0, not negative.
        ("2000", "0.00"),
    ],
)
def test_line_7_is_line_3_less_2000_and_not_below_zero(
    tmp_path: Path, line_3: str, expected: str
) -> None:
    assert t2204(tmp_path, line_3).get(T2204_LINE_7).value == D(expected)


def test_the_exemption_is_the_2000_of_the_form(tmp_path: Path) -> None:
    assert t2204(tmp_path, "65700").get(T2204_EXEMPTION).value == D("2000.00")
