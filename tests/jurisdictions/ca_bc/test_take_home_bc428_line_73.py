"""BC428 (2025) line 73, the basic reduction, as the BC take-home manifest part wires it.

Form text (Form BC428, CRA 5010-c-25e.txt): "Line 73:
Basic reduction Claim $562". The amount is the `ca-bc/tax_reduction_basic` dataset, claimed whole
through core/credit_amount, so it is the same at every salary (line 79 takes it down to 0 from net
income 40,807, which is not built here).

The manifest part is loaded from the package. The header and the form's export are made up here,
because the shared scaffold owns them. British Columbia is not yet listed in the registrations,
so the service is built here over the British Columbia package list of `support.py`.
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
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_bc.catalog import BC428_BASIC_REDUCTION_LINE_73
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
    / "bc428_line_73.yaml"
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
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/bc428_basic_reduction_line_73
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_bc428_line_73.yaml").write_text(
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


def line_73(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-BC"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet.get(BC428_BASIC_REDUCTION_LINE_73).value


@pytest.mark.parametrize("salary", ["17000", "20000", "30000", "70000", "200000"])
def test_line_73_is_the_basic_reduction_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_73(tmp_path, salary) == D("562.00")
