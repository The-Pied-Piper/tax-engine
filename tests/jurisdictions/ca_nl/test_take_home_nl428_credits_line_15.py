"""NL428 (2025) line 15, the Newfoundland and Labrador tax on taxable income, real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 15: Line 13 plus line 14 Newfoundland and
Labrador tax on taxable income =". The form prints that label, so the step is titled "Newfoundland
and Labrador tax on taxable income" and carries the reference "15". Line 15 is one `core/sum` over
`ca-nl/nl428_tax_on_excess_line_13` and `ca-nl/nl428_bracket_tax_at_start_line_14` with
`ca-nl/cent_rounding`, output `ca-nl/nl428_tax_on_taxable_income_line_15`, in the part
`nl428_credits_line_15.yaml`. At or below 220,910 lines 13 and 14 are blank (lines 2 to 8 apply), so
line 15 is blank too.

Figures (hand-computed, not a CRA example): salary 250,000 gives line 13 of 5,547.17 and line 14 of
32,454.04, so 38,001.21; 700,000 gives
28,647.86 and 103,292.95, so 131,940.81.
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
from tests.manifest_support import inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
ROUNDING = "ca-nl/cent_rounding"
LINE_13 = "ca-nl/nl428_tax_on_excess_line_13"
LINE_14 = "ca-nl/nl428_bracket_tax_at_start_line_14"
LINE_15 = "ca-nl/nl428_tax_on_taxable_income_line_15"
TITLE = "Newfoundland and Labrador tax on taxable income"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_credits_line_15.yaml"
NL_LINE_PARTS = tuple(
    NL_PARTS / f"nl428_credits_line_{number}.yaml" for number in (1, 10, 11, 12, 13, 14)
)
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
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
# The NL428 declaration, test-local: lines 13, 14 and 15 are read or exported here.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_13}
        - {LINE_14}
        - {LINE_15}
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
    for part in (*NL_LINE_PARTS, LINE_PART):
        yield part.name, part.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
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


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


@pytest.mark.parametrize(
    ("salary", "line_13", "line_14", "expected"),
    [
        # Line 1 is 248,926.00: column 1, 28,016.00 x 19.8% = 5,547.168, half-up to 5,547.17.
        ("250000", "5547.17", "32454.04", "38001.21"),
        # Line 1 is 698,926.00: column 3, 134,497.00 x 21.3% = 28,647.861, to 28,647.86.
        ("700000", "28647.86", "103292.95", "131940.81"),
    ],
)
def test_line_15_is_line_13_plus_line_14(
    tmp_path: Path, salary: str, line_13: str, line_14: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_13)).value == D(line_13)
    assert sheet.get(_kind(LINE_14)).value == D(line_14)
    value = sheet.get(_kind(LINE_15)).value
    assert value == D(expected)
    assert str(value) == expected


def test_line_15_is_blank_when_line_1_is_220910_or_less(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "200000")

    assert sheet.get(_kind(LINE_13)).is_blank
    assert sheet.get(_kind(LINE_14)).is_blank
    assert sheet.get(_kind(LINE_15)).is_blank


def test_the_part_is_one_titled_sum_step_over_lines_13_and_14() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert part == {
        "form": {"name": FORM},
        "capabilities": [
            {
                "name": "core/sum",
                "title": TITLE,
                "reference": "15",
                "unit": "ca/cad",
                "params": {"rounding": ROUNDING},
                "consumes": {"parts": [LINE_13, LINE_14]},
                "blank": {LINE_13: "pass_on", LINE_14: "pass_on"},
                "produces": {"output": LINE_15},
            }
        ],
    }
