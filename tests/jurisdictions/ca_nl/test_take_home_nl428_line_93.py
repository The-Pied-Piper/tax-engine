"""NL428 (2025) line 93, adjusted family income (line 92 of both columns added), real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 93: Add the amounts from line 92 of
columns 1 and 2. Enter this amount on line 99. Adjusted family income". Line 93 is one core/sum
step over line 92 of column 1 (you) and line 92 of column 2 (your spouse or common-law partner).
Column 2 is blank for a salary-only single filer, so the step reads it as 0. The form prints the
title "Adjusted family income" on line 93.

Figures (hand-computed, not a CRA example): line 92 of column 1 is 19,835.00 /
198,926.00 at salaries of 20,000 / 200,000, and column 2 is blank, so line 93 is the same;
with a spouse's line 88 of 30,000.00 at 70,000, line 93 is 99,335.00.
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
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_ADJUSTED_FAMILY_INCOME_LINE_93,
    NL428_SPOUSE_NET_INCOME_LINE_88,
)
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
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
LINE_88 = "ca-nl/nl428_net_income_line_88"
LINE_89 = "ca-nl/nl428_uccb_rdsp_repayments_line_89"
LINE_90 = "ca-nl/nl428_family_income_line_90"
LINE_91 = "ca-nl/nl428_uccb_rdsp_income_line_91"
LINE_92 = "ca-nl/nl428_family_income_less_uccb_rdsp_line_92"
LINE_92_COLUMN_2 = "ca-nl/nl428_spouse_family_income_less_uccb_rdsp_line_92"
LINE_93 = "ca-nl/nl428_adjusted_family_income_line_93"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART_93 = NL_PARTS / "nl428_line_93.yaml"
# The real parts, in composition order: lines 88 to 92 of column 1, then of column 2, then line 93.
NL_LINE_PARTS = (
    NL_PARTS / "nl428_line_88.yaml",
    NL_PARTS / "nl428_line_89.yaml",
    NL_PARTS / "nl428_line_90.yaml",
    NL_PARTS / "nl428_line_91.yaml",
    NL_PARTS / "nl428_line_92.yaml",
    NL_PARTS / "nl428_line_88_column_2_input.yaml",
    NL_PARTS / "nl428_line_89_column_2_input.yaml",
    NL_PARTS / "nl428_line_90_column_2.yaml",
    NL_PARTS / "nl428_line_91_column_2_input.yaml",
    NL_PARTS / "nl428_line_92_column_2.yaml",
    PART_93,
)
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The form declaration, test-local: the tax form exports line 93.
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_93}
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
            found.read_text("utf-8"),
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
def test_line_93_is_line_92_of_column_1_when_column_2_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(NL428_ADJUSTED_FAMILY_INCOME_LINE_93).value

    assert value == D(expected)
    assert str(value) == expected


def test_line_93_adds_line_92_of_column_2_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(NL428_SPOUSE_NET_INCOME_LINE_88, D("30000.00")))

    # 69,335.00 plus 30,000.00.
    assert sheet.get(NL428_ADJUSTED_FAMILY_INCOME_LINE_93).value == D("99335.00")


def test_line_93_is_one_titled_sum_step_over_line_92_of_both_columns() -> None:
    part: Any = yaml.safe_load(PART_93.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/sum",
                "title": "Adjusted family income",
                "reference": "93",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [LINE_92, LINE_92_COLUMN_2]},
                "blank": {LINE_92_COLUMN_2: "0"},
                "produces": {"output": LINE_93},
            }
        ],
    }
