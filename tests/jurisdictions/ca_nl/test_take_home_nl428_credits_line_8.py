"""NL428 (2025) line 8, the Newfoundland and Labrador tax on taxable income, real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 8: Line 6 plus line 7 Newfoundland and
Labrador tax on taxable income =". The form prints that label, so the step is titled "Newfoundland
and Labrador tax on taxable income" and carries the reference "8". Line 8 is one `core/sum` over
`ca-nl/nl428_tax_on_excess_line_6` and `ca-nl/nl428_bracket_tax_at_start_line_7` with
`ca-nl/cent_rounding`, output `ca-nl/nl428_tax_on_taxable_income_line_8`, in the part
`nl428_credits_line_8.yaml`. Above 220,910 lines 6 and 7 are blank (lines 9 to 15 apply), so line 8
is blank too.

Figures (hand-computed, not a CRA example): salary 20,000 gives line 6 of 1,725.65 and line 7 of
0.00, so line 8 is 1,725.65; 200,000 gives 7,321.85 and 21,219.03, so 28,540.88.
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
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
FORM = "ca-nl/nl428_credits"
ROUNDING = "ca-nl/cent_rounding"
LINE_6 = "ca-nl/nl428_tax_on_excess_line_6"
LINE_7 = "ca-nl/nl428_bracket_tax_at_start_line_7"
LINE_8 = "ca-nl/nl428_tax_on_taxable_income_line_8"
TITLE = "Newfoundland and Labrador tax on taxable income"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_credits_line_8.yaml"
NL_LINE_PARTS = tuple(
    NL_PARTS / f"nl428_credits_line_{number}.yaml" for number in (1, 3, 4, 5, 6, 7)
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
# The NL428 declaration, test-local: lines 6, 7 and 8 are read or exported here.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
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
    for part in (*NL_LINE_PARTS, LINE_PART):
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(dict.fromkeys(_part_files()), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(CODE, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "line_6", "line_7", "expected"),
    [
        # Line 1 is 19,835.00: column 1, 19,835.00 x 8.7% = 1,725.645, half-up to 1,725.65.
        ("20000", "1725.65", "0.00", "1725.65"),
        # Line 1 is 198,926.00: column 4, 41,134.00 x 17.8% = 7,321.852, to 7,321.85.
        ("200000", "7321.85", "21219.03", "28540.88"),
    ],
)
def test_line_8_is_line_6_plus_line_7(
    tmp_path: Path, salary: str, line_6: str, line_7: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_6)).value == D(line_6)
    assert sheet.get(_kind(LINE_7)).value == D(line_7)
    value = sheet.get(_kind(LINE_8)).value
    assert value == D(expected)
    assert str(value) == expected


def test_line_8_is_blank_when_line_1_is_above_220910(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")

    assert sheet.get(_kind(LINE_6)).is_blank
    assert sheet.get(_kind(LINE_7)).is_blank
    assert sheet.get(_kind(LINE_8)).is_blank


def test_the_part_is_one_titled_sum_step_over_lines_6_and_7() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM},
        "capabilities": [
            {
                "name": "core/sum",
                "title": TITLE,
                "reference": "8",
                "unit": "ca/cad",
                "params": {"rounding": ROUNDING},
                "consumes": {"parts": [LINE_6, LINE_7]},
                "blank": {LINE_6: "pass_on", LINE_7: "pass_on"},
                "produces": {"output": LINE_8},
            }
        ],
    }
