"""BC479 (2025) line 9, the basic sales tax credit, as the BC take-home manifest part wires it.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 9 and line 60330: Basic sales tax
credit Claim $75". The amount is the `ca-bc/sales_tax_credit_basic` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. The output kind is looked up by its identifier in the
British Columbia kinds, so a missing kind fails the test rather than the import. British Columbia
is not yet listed in the registrations, so the service is built here over the British Columbia
package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.credit import Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import CreditAmountLine
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)

D = Decimal
IDENTIFIER = "ca-bc/bc479_basic_sales_tax_credit_line_9"
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_bc.__file__).parent
    / "manifests"
    / "2025"
    / "bc479_line_9.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    """)
FORM = dedent(f"""\
    form:
      name: ca-bc/bc479
      required: true
      exports:
        - {IDENTIFIER}
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_bc479_line_9.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**british_columbia_packages().roots(), Namespace("ca-bc"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, british_columbia_kinds(), british_columbia_units()),
        YamlParameterSource(
            british_columbia_packages().roots(),
            british_columbia_parameter_parsers(),
            british_columbia_units(),
        ),
        british_columbia_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Any:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-bc/bc479"]
    return sheet


def line_9(tmp_path: Path, salary: str) -> Decimal:
    value = _sheet(tmp_path, salary).get(british_columbia_kinds().kind(IDENTIFIER)).value
    assert isinstance(value, Decimal)
    return value


@pytest.mark.parametrize("salary", ["17000", "20000", "30000", "70000", "200000"])
def test_line_9_is_the_basic_sales_tax_credit_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_9(tmp_path, salary) == D("75.00")


def test_line_9_traces_one_credit_amount_line_of_the_dataset(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (row for row in sheet.trace if isinstance(row, CreditAmountLine))
    assert line.output.identifier == IDENTIFIER
    assert line.basis == Credit(D("75"))
    assert line.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert line.value == D("75.00")


def test_the_part_is_one_credit_amount_step_titled_and_numbered_as_printed() -> None:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-bc/bc479"}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "Basic sales tax credit",
            "reference": "9",
            "unit": "ca/cad",
            "params": {"amount": "ca-bc/sales_tax_credit_basic"},
            "produces": {"output": IDENTIFIER},
        }
    ]
