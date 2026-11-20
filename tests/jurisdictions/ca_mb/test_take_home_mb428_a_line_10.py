"""Schedule MB428-A (2025), line 10, the sum of lines 1 to 9, as the Manitoba take-home manifest
parts wire it.

Form text (CRA 5007-a-25e.txt): "Line 10: Add lines 1 to 9. = ^". Lines 2 to 9 are a block that
exists only for blank optional inputs and is skipped, so only line 1, the basic amount (2,065.00),
contributes, at every salary.

The manifest parts are loaded from the package. The header and the form's exports are made up here,
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_mb.catalog import MB428_A_LINE_10
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
PARTS_PATH = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"

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
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_basic_amount_line_1
        - ca-mb/mb428_a_line_10
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_mb428_a_line_1.yaml").write_text(
        (PARTS_PATH / "mb428_a_line_1.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (folder / "03_mb428_a_line_10.yaml").write_text(
        (PARTS_PATH / "mb428_a_line_10.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def line_10(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-mb/mb428_a"]
    return sheet.get(MB428_A_LINE_10).value


@pytest.mark.parametrize("salary", ["10000", "200000"])
def test_line_10_is_line_1_alone_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_10(tmp_path, salary) == D("2065.00")
