"""Form MB479 (2025), line 7, the basic credit, as the Manitoba take-home manifest part wires it.

Form text (CRA 5007-tc-25e.txt): "Line 7: Basic credit 195.00". The amount is the
`ca-mb/personal_tax_credit_basic` dataset, claimed whole through core/credit_amount, so it is
the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. Manitoba is not yet listed in the registrations, so the
service is built here over the Manitoba package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB479_BASIC_CREDIT_LINE_7
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_mb.__file__).parent
    / "manifests"
    / "2025"
    / "mb479_line_7.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
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
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_basic_credit_line_7
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_mb479_line_7.yaml").write_text(
        PART_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def line_7(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-mb/mb479"]
    return sheet.get(MB479_BASIC_CREDIT_LINE_7).value


@pytest.mark.parametrize("salary", ["10000", "20000", "70000", "200000"])
def test_line_7_is_the_basic_credit_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_7(tmp_path, salary) == D("195.00")


def test_the_part_is_one_basic_credit_step() -> None:
    part = yaml.safe_load(PART_PATH.read_text(encoding="utf-8"))

    assert part["form"] == {"name": "ca-mb/mb479"}
    (step,) = part["capabilities"]
    assert step["name"] == "core/credit_amount"
    assert step["title"] == "Basic credit"
    assert step["reference"] == "7"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"amount": "ca-mb/personal_tax_credit_basic"}
    assert step["produces"] == {"output": "ca-mb/mb479_basic_credit_line_7"}


def test_the_basic_credit_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind("ca-mb/mb479_basic_credit_line_7")

    assert kind is MB479_BASIC_CREDIT_LINE_7
    assert non_negative(kind)
