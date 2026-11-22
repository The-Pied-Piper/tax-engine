"""BC428 (2025) line 25, the credits subtotal, as the BC take-home manifest parts wire it.

Form text (Form BC428, CRA 5010-C, read 2026-11-14): "Line 25: Add lines 16, 17, 20, 23 and 24."
Lines 17, 20, 23 and 24 (age, spouse, eligible dependant and caregiver amounts) are not built: a
salary-only single filer under 65 has none, so only line 16, the basic personal amount (12,932.00),
contributes, at every salary. Alberta's line 25 is the analogue (`ab428_line_25.yaml`). The figures
are hand-computed from the printed form (not a CRA example).

The manifest parts are loaded from the package. The header and the form's exports are made up here,
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca_bc.catalog import BC428_SUBTOTAL_LINE_25
from tests.jurisdictions.ca_bc.support import (
    british_columbia_capabilities,
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)

D = Decimal
PARTS_PATH = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025"
LINE_PART = PARTS_PATH / "bc428_line_25.yaml"

HEADER = dedent("""\
    jurisdiction: CA-BC
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-bc/bc428
      required: true
      exports:
        - ca-bc/basic_personal_amount
        - ca-bc/bc428_subtotal_line_25
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    (folder / "02_bc428_line_16.yaml").write_text(
        (PARTS_PATH / "bc428_line_16.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (folder / "03_bc428_line_25.yaml").write_text(
        LINE_PART.read_text(encoding="utf-8"), encoding="utf-8"
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


def line_25(tmp_path: Path, salary: str) -> Decimal:
    worksheets = _service(tmp_path).compute(TaxCalculationRequest(JurisdictionCode("CA-BC"), 2025))
    (sheet,) = worksheets["ca-bc/bc428"]
    return sheet.get(BC428_SUBTOTAL_LINE_25).value


@pytest.mark.parametrize("salary", ["17000", "200000"])
def test_line_25_is_line_16_alone_at_every_salary(tmp_path: Path, salary: str) -> None:
    assert line_25(tmp_path, salary) == D("12932.00")
