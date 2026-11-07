"""T1 (5006-R, 2025) total income from the salary alone: the form's real parts composed end to end.

Every line part has its own test with its neighbours typed in. This module copies every
`t1_taxable_income*.yaml` part from the package into a temporary manifest folder beside a test-only
header, and types in only the gross salary (`ca/employment_income`, line 10100). Other employment
income (line 10400) is an optional header input read as 0. This is not a worked return: no return
file, one form. Parts that sibling tickets add later join through the glob.

Form text (5006-R page 3): "Line 33 and line 15000: Line 28 plus line 32 Total income".
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, TOTAL_INCOME

D = Decimal
TAKE_HOME = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "take_home"
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
      - name: ca/other_employment_income
        required: false
        default: "0"
        basis: 'Other employment income (T1 line 10400)'
    outputs:
      - ca/employment_income
    capabilities: []
    """)


def service(tmp_path: Path) -> TaxComputationService:
    parts = tmp_path / "manifests" / "take_home"
    parts.mkdir(parents=True)
    (parts / "00_header.yaml").write_text(HEADER)
    for part in sorted(TAKE_HOME.glob("t1_taxable_income*.yaml")):
        shutil.copy(part, parts / part.name)
    roots = dict(tax_engine.registrations.JURISDICTIONS.roots())
    parameter_roots = dict(roots)
    roots[Namespace("ca-on")] = tmp_path
    return TaxComputationService(
        YamlJurisdictionSource(roots, tax_engine.registrations.artifact_kinds()),
        YamlParameterSource(parameter_roots, tax_engine.registrations.parameter_parsers()),
        tax_engine.registrations.capabilities(),
    )


def t1(tmp_path: Path, salary: str) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    worksheets = service(tmp_path).compute(JurisdictionCode("CA-ON"), 2025, *given)
    (sheet,) = worksheets["ca/t1_taxable_income"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), [("70000", "70000.00"), ("90000", "90000.00")])
def test_line_15000_is_the_salary_when_line_10400_is_left_out(
    tmp_path: Path, salary: str, expected: str
) -> None:
    assert t1(tmp_path, salary).get(TOTAL_INCOME).value == D(expected)
