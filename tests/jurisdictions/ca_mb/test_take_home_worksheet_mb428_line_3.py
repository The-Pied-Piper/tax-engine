"""Worksheet MB428 (2025), section "Line 58040 - Basic personal amount", line 3, the income
threshold, as the Manitoba take-home manifest part wires it.

Form text (CRA 5007-d-25e.txt): "Line 3: Income threshold 200,000.00". The amount is the
`ca-mb/basic_personal_amount_threshold` dataset, claimed whole through core/credit_amount, so it is
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

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_mb.catalog import WORKSHEET_MB428_LINE_3
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
PART_PATH = (
    Path(tax_engine.jurisdictions.ca_mb.__file__).parent
    / "manifests"
    / "2025"
    / "worksheet_mb428_line_3.yaml"
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_line_3
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_worksheet_mb428_line_3.yaml").write_text(
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


def line_3(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(TaxCalculationRequest(JurisdictionCode("CA-MB"), 2025))
    (sheet,) = worksheets["ca-mb/worksheet_mb428"]
    return sheet.get(WORKSHEET_MB428_LINE_3).value


@pytest.mark.parametrize("salary", ["10000", "200000"])
def test_line_3_is_the_income_threshold_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_3(tmp_path, salary) == D("200000.00")
