"""NL428 (2025) line 65, line 63 plus line 64, real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 65: Line 63 plus line 64 = ^". One
core/sum step, rounded half-up to the cent by `ca-nl/cent_rounding`, over line 63 (the tax on
taxable income from line 8 or 15, always computed) and line 64 (the tax on split income, an optional
input a salary-only caller leaves out, so the step reads it as 0). The form prints no title for the
line, so the step is untitled.

Figures (hand-computed, not a CRA example): line 63 is 1,725.65 / 7,490.44 / 28,540.88 at salaries
of 20,000 / 70,000 / 200,000 and line 64 is blank, so line 65 is the same; with 100.00 on line 64 at
70,000, line 65 is 7,590.44.
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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import (
    NL428_TAX_BEFORE_CREDITS_LINE_65,
    NL428_TAX_ON_SPLIT_INCOME_LINE_64,
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
CREDITS = "ca-nl/nl428_credits"
TAX = "ca-nl/nl428"
LINE_8 = "ca-nl/nl428_tax_on_taxable_income_line_8"
LINE_15 = "ca-nl/nl428_tax_on_taxable_income_line_15"
LINE_63 = "ca-nl/nl428_newfoundland_and_labrador_tax_on_taxable_income_line_63"
LINE_64 = "ca-nl/nl428_tax_on_split_income_line_64"
LINE_65 = "ca-nl/nl428_tax_before_credits_line_65"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART = NL_PARTS / "nl428_line_65.yaml"
# The real parts, in composition order: lines 1 and 3 to 8, lines 10 to 15, lines 63 and 64, 65.
NL_LINE_PARTS = (
    *(
        NL_PARTS / f"nl428_credits_line_{number}.yaml"
        for number in (1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15)
    ),
    NL_PARTS / "nl428_line_63.yaml",
    NL_PARTS / "nl428_line_64_input.yaml",
    PART,
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The two form declarations, test-local: the credits form exports lines 8 and 15, the tax form
# line 65.
CREDITS_FORM_TEXT = dedent(f"""\
    form:
      name: {CREDITS}
      required: true
      exports:
        - {LINE_8}
        - {LINE_15}
    capabilities: []
    """)
TAX_FORM_TEXT = dedent(f"""\
    form:
      name: {TAX}
      required: true
      exports:
        - {LINE_65}
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
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM_TEXT, encoding="utf-8")
    (folder / "02_tax_form.yaml").write_text(TAX_FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(dict.fromkeys(_part_files()), start=3):
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
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[TAX]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "1725.65"), ("200000", "28540.88")],
)
def test_line_65_is_line_63_when_line_64_is_left_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(NL428_TAX_BEFORE_CREDITS_LINE_65).value

    assert value == D(expected)
    assert str(value) == expected


def test_line_65_adds_line_64_when_it_is_given(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", Artifact(NL428_TAX_ON_SPLIT_INCOME_LINE_64, D("100.00")))

    # 7,490.44 plus 100.00.
    assert sheet.get(NL428_TAX_BEFORE_CREDITS_LINE_65).value == D("7590.44")


def test_the_part_is_one_untitled_sum_step_over_lines_63_and_64() -> None:
    part: Any = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": TAX},
        "capabilities": [
            {
                "name": "core/sum",
                "reference": "65",
                "unit": "ca/cad",
                "params": {"rounding": "ca-nl/cent_rounding"},
                "consumes": {"parts": [LINE_63, LINE_64]},
                "blank": {LINE_64: "0"},
                "produces": {"output": LINE_65},
            }
        ],
    }
