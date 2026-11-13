"""AB428 (2025) line 62, Alberta non-refundable tax credits from line 58, real parts.

Form text (Form AB428, CRA 5009-c): "Line 62: Alberta non-refundable tax credits from line 58 ^".
Line 58 of the credits form says "Enter this amount on line 62". Line 62 is a calculation, not an
input: its one step is a core/record_total over the line 58 export of `ca-ab/ab428_credits`
(`ca-ab/ab428_non_refundable_credits_line_58`), a cross-form read as the worksheet line 1 reads line
52. The form prints no title for the line beyond its label, so the step is untitled. Line 58 is
always computed, so the step has no blank rule.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real AB428
credits parts up to line 58 (line 16, 25, 27, 29, 32, 33, 34 inputs, 36, 39, 41 input, 43, 51
inputs, 52, 54, 57 inputs and 58) and the new `ab428_line_62.yaml`, and types in only the salary.
The header and the two form declarations (AB428 credits, exporting line 58, and AB428, exporting
line 62) are made up here, because the shared scaffold owns them. The figures are the line 58
figures of the line 58 test (line 54 plus a blank line 57 read as 0): 1,877.42, 2,135.38 and
2,140.53 at the three salaries.
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
from tax_engine.jurisdictions.ca_ab.catalog import AB428_CREDITS_FROM_LINE_58_LINE_62
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
LINE_PART = ALBERTA_PARTS / "ab428_line_62.yaml"
KIND = "ca-ab/ab428_credits_from_line_58_line_62"

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
        - ca-ab/ab428_non_refundable_credits_line_58
    capabilities: []
    """)
AB428_FORM = dedent("""\
    form:
      name: ca-ab/ab428
      required: true
      exports:
        - ca-ab/ab428_credits_from_line_58_line_62
    capabilities: []
    """)

# salary, line 62: line 58 (line 54 plus a blank line 57, as the line 58 test pins).
CASES = [("20000", "1877.42"), ("70000", "2135.38"), ("200000", "2140.53")]


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
    yield ALBERTA_PARTS / "ab428_credits_line_54.yaml"
    yield ALBERTA_PARTS / "ab428_line_57_inputs.yaml"
    yield ALBERTA_PARTS / "ab428_credits_line_58.yaml"
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Alberta manifest of a test header, two form declarations and
    the real part files, every other namespace being the Alberta package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_ab428_form.yaml").write_text(AB428_FORM, encoding="utf-8")
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
    (sheet,) = worksheets["ca-ab/ab428"]
    return sheet


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_62_is_line_58_at_each_salary(tmp_path: Path, salary: str, expected: str) -> None:
    assert _sheet(tmp_path, salary).get(AB428_CREDITS_FROM_LINE_58_LINE_62).value == D(expected)


def test_the_trace_has_a_row_for_line_62(tmp_path: Path) -> None:
    rows = EnglishTraceRenderer().render_all(_sheet(tmp_path, "70000").trace)

    assert any(("2135.38" in row or "2,135.38" in row) and "gives" in row for row in rows)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_record_total_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "consumes", "produces"]
    assert step["name"] == "core/record_total"
    assert step["reference"] == "62"
    assert step["unit"] == "ca/cad"
    assert step["consumes"] == {
        "records": "ca-ab/ab428_credits.ab428_non_refundable_credits_line_58"
    }
    assert step["produces"] == {"output": KIND}


def test_line_62_is_a_registered_non_negative_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is AB428_CREDITS_FROM_LINE_58_LINE_62
