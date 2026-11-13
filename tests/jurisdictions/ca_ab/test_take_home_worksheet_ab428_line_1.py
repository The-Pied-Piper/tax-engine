"""Worksheet AB428 (2025) line 1, the amount from AB428 line 52, from the salary alone, real parts.

Form text (Worksheet AB428, CRA 5009-D): "Line 1: Amount from line 58800 of your Form AB428 ^". Line
58800 of Form AB428 is line 52 ("Line 52 and line 58800: Line 43 plus line 51 = ^"). Line 1 is a
calculation, not an input: its one step is a core/record_total over the AB428 line 52 export
(`ca-ab/ab428_credits.ab428_credits_total_line_52`), as Ontario's line 1 reads a cross-form
export. The form prints no title text for the line, so the step is untitled. Line 52 is always
computed, so the step has no blank rule.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real
AB428 credits parts up to line 52 (line 16, 25, 27, 29, 32, 33, 34 inputs, 36, 39, 41 input, 43,
51 inputs and 52) and the new `worksheet_ab428_line_1.yaml`, and types in only the salary. The
header and the two form declarations (AB428 credits, exporting line 52, and the worksheet,
exporting line 1) are made up here, because the shared scaffold owns them. Alberta is not yet
listed in the registrations, so the service is built here over the Alberta package list of
`support.py`. The figures are hand-computed from the printed forms (not a CRA example): line 52 is
23,467.75, 26,692.23 and 26,756.58 at the three salaries.
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
import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import WORKSHEET_AB428_LINE_1
from tests.jurisdictions.ca_ab.support import (
    alberta_capabilities,
    alberta_kinds,
    alberta_packages,
    alberta_parameter_parsers,
    alberta_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
ALBERTA_PARTS = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = ALBERTA_PARTS / "worksheet_ab428_line_1.yaml"
KIND = "ca-ab/worksheet_ab428_line_1"

HEADER = dedent("""\
    jurisdiction: CA-AB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
CREDITS_FORM = dedent("""\
    form:
      name: ca-ab/ab428_credits
      required: true
      exports:
        - ca-ab/ab428_credits_total_line_52
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-ab/worksheet_ab428
      required: true
      exports:
        - ca-ab/worksheet_ab428_line_1
    capabilities: []
    """)

# salary, line 1: line 52 (line 43 plus line 51, blank and read as 0).
CASES = [("20000", "23467.75"), ("70000", "26692.23"), ("200000", "26756.58")]


def _part_files() -> Iterator[Path]:
    yield ALBERTA_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
    yield ALBERTA_PARTS / "ab428_line_16.yaml"
    yield ALBERTA_PARTS / "ab428_line_25.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_27.yaml"
    yield ALBERTA_PARTS / "ab428_line_29.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_32.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_33.yaml"
    yield ALBERTA_PARTS / "ab428_line_34_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_36.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_39.yaml"
    yield ALBERTA_PARTS / "ab428_line_41_input.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_41.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_43.yaml"
    yield ALBERTA_PARTS / "ab428_line_51_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_52.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, two form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_worksheet_form.yaml").write_text(WORKSHEET_FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=3):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**alberta_packages().roots(), Namespace("ca-ab"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, alberta_kinds(), alberta_units()),
        YamlParameterSource(
            alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
        ),
        alberta_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, *extra: Artifact[Decimal]) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary)), *extra]
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-AB"), 2025, *given)
    (sheet,) = worksheets["ca-ab/worksheet_ab428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_1_is_line_52_at_each_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(WORKSHEET_AB428_LINE_1).value == D(expected)


def test_the_trace_has_a_row_for_line_1(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any("26692.23" in row or "26,692.23" in row for row in rows)


def _line() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_record_total_step() -> None:
    part = _line()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/worksheet_ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["reference"] == "1"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {"records": "ca-ab/ab428_credits.ab428_credits_total_line_52"}
    assert step["produces"] == {"output": KIND}


def test_line_1_is_a_registered_non_negative_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is WORKSHEET_AB428_LINE_1
