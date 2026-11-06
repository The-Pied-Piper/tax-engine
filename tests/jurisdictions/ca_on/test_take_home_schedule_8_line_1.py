"""Schedule 8 (5000-S8, 2025) Part 3 line 1, the total CPP pensionable earnings, as the Ontario
take-home manifest part wires it: the salary capped at the printed "(maximum $81,200 per slip)".

The manifest part is loaded from the package. The header, the salary input and the form's export
are made up here, because the shared scaffold owns them. The caller has no T4, so line 1 reads the
salary typed once (T1 line 10100) in place of box 26.
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.rc381_cpp_qpp import (
    T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC,
)

D = Decimal
PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent
    / "manifests"
    / "take_home"
    / "schedule_8_line_1.yaml"
)

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
      name: ca/schedule_8
      required: true
      exports:
        - ca/t4_cpp_pensionable_earnings_outside_quebec
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


def line_1(tmp_path: Path, salary: str) -> Decimal:
    worksheets = service(tmp_path).compute(
        JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca/schedule_8"]
    return sheet.get(T4_CPP_PENSIONABLE_EARNINGS_OUTSIDE_QUEBEC).value


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # A $70,000 salary is under the maximum, so line 1 is the salary.
        ("70000", "70000.00"),
        # $90,000 is above the $81,200 ceiling, so line 1 is the printed maximum.
        ("90000", "81200.00"),
        # At the maximum and a cent either side of it.
        ("81200", "81200.00"),
        ("81200.01", "81200.00"),
        ("81199.99", "81199.99"),
        ("0", "0.00"),
    ],
)
def test_line_1_is_the_salary_capped_at_the_per_slip_maximum(
    tmp_path: Path, salary: str, expected: str
) -> None:
    result = line_1(tmp_path, salary)

    assert result == D(expected)
    # Dollars and cents, from the cap dataset's rounding rule.
    assert result.as_tuple().exponent == -2
