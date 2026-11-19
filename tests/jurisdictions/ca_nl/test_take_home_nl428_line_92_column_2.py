"""NL428 (2025) line 92, line 90 minus line 91 (not below 0), column 2 (your spouse or partner).

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 92: Line 90 minus line 91 (if negative,
enter "0")". Column 2 is one core/subtract_not_below_zero step over the spouse's line 90 and line 91
(UCCB and RDSP income), both fed by optional inputs a salary-only single filer leaves out. A blank
line 90 is passed on, so line 92 is blank; a blank line 91 is read as 0.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92,
    NL428_SPOUSE_NET_INCOME_LINE_88,
    NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91,
)
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
LINE_91 = "ca-nl/nl428_spouse_uccb_rdsp_income_line_91"
LINE_92 = "ca-nl/nl428_spouse_family_income_less_uccb_rdsp_line_92"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART_92 = NL_PARTS / "nl428_line_92_column_2.yaml"
# The real parts, in composition order: the inputs and line 90, line 91's input, then line 92.
NL_LINE_PARTS = (
    NL_PARTS / "nl428_line_88_column_2_input.yaml",
    NL_PARTS / "nl428_line_89_column_2_input.yaml",
    NL_PARTS / "nl428_line_90_column_2.yaml",
    NL_PARTS / "nl428_line_91_column_2_input.yaml",
    PART_92,
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The form declaration, test-local: the tax form exports line 92.
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_92}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
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
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[TAX]
    return sheet


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_92_is_blank_when_the_spouse_lines_are_left_blank(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92).is_blank


def test_line_92_takes_line_91_off_line_90(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("30000.00")),
        Artifact(NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91, D("100.00")),
    )

    assert sheet.get(NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92).value == D("29900.00")


def test_line_92_reads_a_blank_line_91_as_0(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("30000.00")))

    assert sheet.get(NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92).value == D("30000.00")


def test_line_92_is_zero_when_line_91_is_more_than_line_90(tmp_path: Path) -> None:
    sheet = _sheet(
        tmp_path,
        "70000",
        Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("-2500.00")),
        Artifact(NL428_SPOUSE_UCCB_RDSP_INCOME_LINE_91, D("100.00")),
    )

    assert sheet.get(NL428_SPOUSE_FAMILY_INCOME_LESS_UCCB_RDSP_LINE_92).value == D("0.00")


def test_line_92_is_one_untitled_subtract_not_below_zero_step_over_lines_90_and_91() -> None:
    part: Any = yaml.safe_load(PART_92.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/subtract_not_below_zero",
                "reference": "92 (column 2)",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"amount": LINE_90, "less": LINE_91},
                "blank": {"amount": "pass_on", "less": "0"},
                "produces": {"output": LINE_92},
            }
        ],
    }
