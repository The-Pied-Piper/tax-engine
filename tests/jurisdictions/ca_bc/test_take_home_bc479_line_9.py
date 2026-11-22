"""BC479 (2025) line 9, the basic sales tax credit, as the BC take-home manifest part wires it.

Form text (Form BC479, CRA 5010-TC, read 2026-11-14): "Line 9 and line 60330: Basic sales tax
credit Claim $75". The amount is the `ca-bc/sales_tax_credit_basic` dataset, claimed whole through
core/credit_amount, so it is the same at every salary.

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. The service is built here over the British Columbia package
list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc.catalog import BC479_BASIC_SALES_TAX_CREDIT_LINE_9
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)

D = Decimal
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
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc479
      required: true
      exports:
        - ca-bc/bc479_basic_sales_tax_credit_line_9
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


def line_9(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-BC"), 2025)
    (sheet,) = worksheets["ca-bc/bc479"]
    return sheet.get(BC479_BASIC_SALES_TAX_CREDIT_LINE_9).value


@pytest.mark.parametrize("salary", ["17000", "200000"])
def test_line_9_is_the_basic_sales_tax_credit_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_9(tmp_path, salary) == D("75.00")
