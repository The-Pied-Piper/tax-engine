"""MB479 (2025) line 62, line 60 plus line 61, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 62: Line 60 plus line 61 = ^". Line 62 prints no label
and no maximum, so its step has no title. It is one core/sum over line 60 and line 61. Neither is
a blank input: line 60 is computed, and line 61 is computed by its own step, which reads blank
expenses as 0 and holds its $16,000 maximum upstream, so the sum has no blank block.

The test composes the T1 employment income form, the real Schedule 8 parts, the real T1 taxable
income parts, the real MB479 parts of lines 1 to 7, 17, 18, 19, 53, 55, 56, 57, 59 and 60, the
line 61 input and step parts and the new `mb479_line_62.yaml`, and types in only the salary (and,
in some tests, the line 61 expenses). The MB479 form declaration is made up here, exporting only
lines 60, 61 and 62. The figures are line 60 with line 61 at 0.00 (95.65 / 0.00 / 0.00 / 0.00).
They are hand-computed from the printed forms, not a CRA example.
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
import tax_engine.jurisdictions.ca_mb
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
LINE_PART = MB_PARTS / "mb479_line_62.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_credits_line_62"
LINE_60 = "ca-mb/mb479_credits_line_60"
LINE_61 = "ca-mb/mb479_fertility_treatment_credit_line_61"
EXPENSES_61 = "ca-mb/mb479_fertility_treatment_expenses_line_61"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")
MB479_PARTS = (
    "mb479_line_1.yaml",
    "mb479_line_2.yaml",
    "mb479_line_3.yaml",
    "mb479_line_4.yaml",
    "mb479_line_5.yaml",
    "mb479_line_5_column_2_input.yaml",
    "mb479_line_6.yaml",
    "mb479_line_7.yaml",
    "mb479_line_17_inputs.yaml",
    "mb479_line_17.yaml",
    "mb479_line_18.yaml",
    "mb479_line_19.yaml",
    "mb479_line_53_input.yaml",
    "mb479_line_55.yaml",
    "mb479_line_56_input.yaml",
    "mb479_line_57.yaml",
    "mb479_line_59_input.yaml",
    "mb479_line_60.yaml",
    "mb479_line_61_input.yaml",
    "mb479_line_61.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_credits_line_60
        - ca-mb/mb479_fertility_treatment_credit_line_61
        - ca-mb/mb479_credits_line_62
    capabilities: []
    """)

# salary, line 62: line 60 plus line 61, with line 61 at 0.00 when no expenses are entered.
CASES = [
    ("10000", "95.65"),
    ("200000", "0.00"),
]


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in MB479_PARTS:
        yield MB_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, expenses: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if expenses is not None:
        given.append(Artifact(manitoba_kinds().kind(EXPENSES_61), D(expenses)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)
    return steps


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_62_is_line_60_when_line_61_is_zero(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    value = _line(sheet, IDENTIFIER)

    assert _line(sheet, LINE_61) == D("0.00")
    assert value == _line(sheet, LINE_60) == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "expenses", "line_61", "expected"),
    [
        ("70000", "1000", "400.00", "400.00"),
        ("10000", "1000", "400.00", "495.65"),
    ],
)
def test_line_62_adds_line_61_to_line_60(
    tmp_path: Path, salary: str, expenses: str, line_61: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, expenses)
    value = _line(sheet, IDENTIFIER)

    assert _line(sheet, LINE_61) == D(line_61)
    assert value == D(expected)
    assert str(value) == expected


def test_the_16000_maximum_of_line_61_holds_through_line_62(tmp_path: Path) -> None:
    # 50,000 of expenses at 40% is 20,000, capped to 16,000 on line 61; line 60 is 0.00 at 70,000.
    sheet = _sheet(tmp_path, "70000", "50000")

    assert _line(sheet, LINE_61) == D("16000.00")
    assert _line(sheet, LINE_60) == D("0.00")
    value = _line(sheet, IDENTIFIER)
    assert value == D("16000.00")
    assert str(value) == "16000.00"


def test_the_sheet_prints_no_title_and_the_reference_of_line_62(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "62"


def test_the_part_is_one_untitled_sum_step_over_lines_60_and_61() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "62",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_60, LINE_61]},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step
    assert "blank" not in step


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_CREDITS_LINE_62
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
