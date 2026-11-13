"""Worksheet AB428 (2025) line 3, line 1 minus line 2, from the salary alone, real parts.

Form text (Worksheet AB428, CRA 5009-D): "Line 3: Line 1 minus line 2 = ^". The form prints no
"cannot be negative" or "if negative, enter 0" here (unlike lines 4 and 7), so line 3 is a plain
signed `core/subtract` of line 2 from line 1, rounded by `ca-ab/cent_rounding`, and its kind is
signed (not non-negative). The form prints no title text for the line, so the step is untitled,
and neither consumed line is ever blank, so the step has no blank rule.

The test composes the real Alberta salary part, the real Schedule 8 and T2204 parts, the real
AB428 credits parts up to line 52 (line 16, 25, 27, 29, 32, 33, 34 inputs, 36, 39, 41 input, 43,
51 inputs and 52), the real `worksheet_ab428_line_1.yaml` and `worksheet_ab428_line_2.yaml` parts
and the new `worksheet_ab428_line_3.yaml`, and types in only the salary (and, in two tests, line
41). The header and the two form declarations (AB428 credits, exporting lines 41 and 52, and the
worksheet, exporting lines 1, 2 and 3) are made up here, because the shared scaffold owns them.
Alberta is not yet listed in the registrations, so the service is built here over the Alberta
package list of `support.py`. The figures are hand-computed from the printed forms (not a CRA
example): line 1 is 23,467.75, 26,692.23 and 26,756.58 at the three salaries and line 2 is 0.00
(line 41 blank), so line 3 equals line 1. Line 41 is added into line 43, hence into line 52 and
line 1, so a given line 41 raises line 1 and line 2 together and line 3 does not move; a negative
line 3 cannot arise from the real parts and is tested through the capability.
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_ab.catalog import (
    AB428_UNUSED_TUITION_LINE_41,
    WORKSHEET_AB428_LINE_1,
    WORKSHEET_AB428_LINE_2,
    WORKSHEET_AB428_LINE_3,
)
from tax_engine.jurisdictions.core.capabilities.subtract import Subtract
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
LINE_PART = ALBERTA_PARTS / "worksheet_ab428_line_3.yaml"
KIND = "ca-ab/worksheet_ab428_line_3"
LINE_1 = "ca-ab/worksheet_ab428_line_1"
LINE_2 = "ca-ab/worksheet_ab428_line_2"
ROUNDING = "ca-ab/cent_rounding"

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
        - ca-ab/ab428_unused_tuition_rounded_line_41
        - ca-ab/ab428_credits_total_line_52
    capabilities: []
    """)
WORKSHEET_FORM = dedent("""\
    form:
      name: ca-ab/worksheet_ab428
      required: true
      exports:
        - ca-ab/worksheet_ab428_line_1
        - ca-ab/worksheet_ab428_line_2
        - ca-ab/worksheet_ab428_line_3
    capabilities: []
    """)

# salary, line 3: line 1 (line 52) less line 2 (line 41, blank and read as 0).
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
    yield ALBERTA_PARTS / "worksheet_ab428_line_1.yaml"
    yield ALBERTA_PARTS / "worksheet_ab428_line_2.yaml"
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
def test_line_3_is_line_1_minus_line_2_at_each_salary(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    value = sheet.get(WORKSHEET_AB428_LINE_3).value

    assert value == D(expected)
    assert (
        value == sheet.get(WORKSHEET_AB428_LINE_1).value - sheet.get(WORKSHEET_AB428_LINE_2).value
    )
    assert value.as_tuple().exponent == -2


def test_a_given_line_41_raises_line_1_and_line_2_alike_so_line_3_does_not_move(
    tmp_path: Path,
) -> None:
    # Line 41 enters line 43, so line 52 and line 1: 26,692.23 plus 1,500.00 is 28,192.23. Line 2
    # is the 1,500.00 itself, so line 3 is 28,192.23 less 1,500.00, 26,692.23 again.
    sheet = _sheet(tmp_path, "70000", Artifact(AB428_UNUSED_TUITION_LINE_41, D("1500.00")))

    assert sheet.get(WORKSHEET_AB428_LINE_1).value == D("28192.23")
    assert sheet.get(WORKSHEET_AB428_LINE_2).value == D("1500.00")
    assert sheet.get(WORKSHEET_AB428_LINE_3).value == D("26692.23")


def test_the_step_traces_one_subtracted_line_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = alberta_kinds()
    rounding = YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedLine)]
    assert line == SubtractedLine(
        output=kinds.kind(KIND),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("26692.23"),
        subtrahend=kinds.kind(LINE_2),
        subtrahend_amount=D("0.00"),
        rounding=rounding.rounding,
        result=D("26692.23"),
    )


def test_the_subtract_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert [row for row in rows if " less " in row] == [
        "Worksheet ab428 line 1 (26692.23) less worksheet ab428 line 2 (0.00) gives 26692.23 "
        "(rounded to the nearest cent)."
    ]


def _line_3_at(line_1_amount: str, line_2_amount: str) -> Decimal:
    """Line 3 over given lines 1 and 2: the capability the part builds, with the real dataset."""
    kinds = alberta_kinds()
    line_1, line_2, line_3 = kinds.kind(LINE_1), kinds.kind(LINE_2), kinds.kind(KIND)
    assert isinstance(line_1, AmountKind)
    assert isinstance(line_2, AmountKind)
    assert isinstance(line_3, AmountKind)
    rounding = YamlParameterSource(
        alberta_packages().roots(), alberta_parameter_parsers(), alberta_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)
    result = Subtract(rounding, line_1, line_2, line_3).run(
        (Artifact(line_1, D(line_1_amount)), Artifact(line_2, D(line_2_amount)))
    )
    (output,) = result.outputs
    value: Decimal = output.value
    return value


@pytest.mark.parametrize(
    ("line_1", "line_2", "expected"),
    [
        ("26692.23", "0.00", "26692.23"),
        ("28192.23", "1500.00", "26692.23"),
        ("100.00", "100.00", "0.00"),
        ("1000.00", "1500.00", "-500.00"),
        ("0.00", "0.01", "-0.01"),
    ],
)
def test_line_3_is_signed_with_no_floor_at_zero(line_1: str, line_2: str, expected: str) -> None:
    assert _line_3_at(line_1, line_2) == D(expected)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_subtract_step() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ab/worksheet_ab428"}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step["name"] == "core/subtract"
    assert step["reference"] == "3"
    assert step["unit"] == "ca/cad"
    assert step["params"] == {"rounding": ROUNDING}
    assert step["consumes"] == {"amount": LINE_1, "less": LINE_2}
    assert step["produces"] == {"output": KIND}


def test_line_3_is_a_registered_signed_amount_kind() -> None:
    kinds = alberta_kinds()

    assert KIND in kinds.identifiers()
    kind = kinds.kind(KIND)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind) is False
    assert kind is WORKSHEET_AB428_LINE_3
