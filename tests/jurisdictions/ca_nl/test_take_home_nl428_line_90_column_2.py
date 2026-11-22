"""NL428 (2025) line 90, line 88 plus line 89, column 2 (your spouse or common-law partner).

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 90: Line 88 plus line 89". Column 2 is one
core/sum step over the spouse's line 88 (net income) and line 89 (UCCB and RDSP repayments), both
optional inputs a salary-only single filer leaves out. A blank line 88 is passed on, so line 90 is
blank; a blank line 89 is read as 0.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_SPOUSE_FAMILY_INCOME_LINE_90,
    NL428_SPOUSE_NET_INCOME_LINE_88,
    NL428_SPOUSE_UCCB_AND_RDSP_REPAYMENT_LINE_89,
)
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)

D = Decimal
CODE = JurisdictionCode("CA-NL")
TAX = "ca-nl/nl428"
LINE_88 = "ca-nl/nl428_spouse_net_income_line_88"
LINE_89 = "ca-nl/nl428_spouse_uccb_and_rdsp_repayment_line_89"
LINE_90 = "ca-nl/nl428_spouse_family_income_line_90"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART_90 = NL_PARTS / "nl428_line_90_column_2.yaml"
# The real parts, in composition order: the two inputs, then line 90.
NL_LINE_PARTS = (
    NL_PARTS / "nl428_line_88_column_2_input.yaml",
    NL_PARTS / "nl428_line_89_column_2_input.yaml",
    PART_90,
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The form declaration, test-local: the tax form exports line 90.
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_90}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    for part in form_parts("t1_employment_income"):
        (folder / f"00_t1_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    (folder / "01_tax_form.yaml").write_text(TAX_FORM_TEXT, encoding="utf-8")
    for number, part in enumerate(NL_LINE_PARTS, start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[TAX]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_90_is_blank_when_the_spouse_lines_are_left_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(NL428_SPOUSE_FAMILY_INCOME_LINE_90).is_blank


def test_line_90_adds_line_89_to_line_88(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("30000.00")),
        Artifact(NL428_SPOUSE_UCCB_AND_RDSP_REPAYMENT_LINE_89, D("100.00")),
    )

    assert sheet.get(NL428_SPOUSE_FAMILY_INCOME_LINE_90).value == D("30100.00")


def test_line_90_reads_a_blank_line_89_as_0_and_keeps_a_negative_line_88(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("-2500.00")))

    assert sheet.get(NL428_SPOUSE_FAMILY_INCOME_LINE_90).value == D("-2500.00")


def test_line_90_is_one_untitled_sum_step_over_the_spouse_lines_88_and_89() -> None:
    part: Any = yaml.safe_load(PART_90.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/sum",
                "reference": "90 (column 2)",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [LINE_88, LINE_89]},
                "blank": {LINE_88: "pass_on", LINE_89: "0"},
                "produces": {"output": LINE_90},
            }
        ],
    }
