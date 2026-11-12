"""AB428 (2025) line 25, the credits subtotal, as the Alberta take-home manifest parts wire it.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 25: Add lines 16, 17, 20, 23, and 24." Lines 17,
20, 23 and 24 are blank for a salary-only single filer, so only line 16, the basic personal amount
(22,323.00), contributes, at every salary.

The manifest parts are loaded from the package. The header and the form's exports are made up
here, because the shared scaffold owns them. Alberta is not yet listed in the registrations, so
the service is built here over the Alberta package list of `support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import pytest

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import AB428_CREDITS_SUBTOTAL_LINE_25
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)

D = Decimal
PARTS_PATH = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"

HEADER = dedent("""\
    jurisdiction: CA-AB
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
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/basic_personal_amount
        - ca-ab/ab428_credits_subtotal_line_25
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_ab428_line_16.yaml").write_text(
        (PARTS_PATH / "ab428_line_16.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "03_ab428_line_25.yaml").write_text(
        (PARTS_PATH / "ab428_line_25.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def line_25(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-AB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets["ca-ab/ab428_credits"]
    return sheet.get(AB428_CREDITS_SUBTOTAL_LINE_25).value


@pytest.mark.parametrize("salary", ["20000", "70000", "200000"])
def test_line_25_is_line_16_alone_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_25(tmp_path, salary) == D("22323.00")
