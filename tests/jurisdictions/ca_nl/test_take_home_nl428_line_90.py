"""NL428 (2025) line 90, line 88 plus line 89, your column, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 90: Line 88 plus line 89". Column 1 (you)
only. Line 88 is the T1 net income before its floor, read as a record list by one core/record_total
step; line 90 is one core/sum step over line 88 and line 89 (the UCCB and RDSP repayments), an
optional input a salary-only caller leaves out, so the step reads it as 0. The form prints no title
for line 90, so its step is untitled.

Figures (hand-computed, not a CRA example): net income is 19,835.00 / 198,926.00 at
salaries of 20,000 / 200,000 (the salary less the enhanced CPP deduction), and line 89 is
blank, so line 90 is the same; with 100.00 on line 89 at 70,000, line 90 is 69,435.00.
"""

from __future__ import annotations

from collections.abc import Iterator
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME, UCCB_REPAYMENT
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_FAMILY_INCOME_LINE_90,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-NL")
TAX = "ca-nl/nl428"
LINE_88 = "ca-nl/nl428_net_income_line_88"
LINE_89 = "ca-nl/nl428_uccb_rdsp_repayments_line_89"
LINE_90 = "ca-nl/nl428_family_income_line_90"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART_88 = NL_PARTS / "nl428_line_88.yaml"
PART_90 = NL_PARTS / "nl428_line_90.yaml"
# The real parts, in composition order: line 88, the line 89 input, line 90.
NL_LINE_PARTS = (PART_88, NL_PARTS / "nl428_line_89.yaml", PART_90)
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

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
# The form declaration, test-local: the tax form exports line 90.
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_90}
    capabilities: []
    """)


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = next(FEDERAL_FORMS.rglob(name))
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    for part in NL_LINE_PARTS:
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_tax_form.yaml").write_text(TAX_FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
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


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "19835.00"), ("200000", "198926.00")],
)
def test_line_90_is_line_88_when_line_89_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(NL428_FAMILY_INCOME_LINE_90).value

    assert value == D(expected)
    assert str(value) == expected


def test_line_90_adds_line_89_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(UCCB_REPAYMENT, D("100.00")))

    # 69,335.00 plus 100.00.
    assert sheet.get(NL428_FAMILY_INCOME_LINE_90).value == D("69435.00")


def test_line_88_is_one_record_total_over_the_signed_net_income() -> None:
    part: Any = yaml.safe_load(PART_88.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/record_total",
                "title": "Net income from line 23600 of the return",
                "reference": "88 (column 1)",
                "unit": "ca/cad",
                "consumes": {"records": "ca/t1_taxable_income.net_income_signed"},
                "produces": {"output": LINE_88},
            }
        ],
    }


def test_line_90_is_one_untitled_sum_step_over_lines_88_and_89() -> None:
    part: Any = yaml.safe_load(PART_90.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/sum",
                "reference": "90 (column 1)",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [LINE_88, LINE_89]},
                "produces": {"output": LINE_90},
            }
        ],
    }
