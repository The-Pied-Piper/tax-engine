"""MB479 (2025) line 72, line 70 plus line 71, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 72: Line 70 plus line 71 = ^". Line 72 prints no label
and no maximum, so its step has no title. It is one core/sum over line 70 and the line 71 input,
which is optional and read as 0 when left blank, so the step carries a blank block and prints its
own "left blank, taken as 0" row.

The test composes the T1 employment income form, the real Schedule 8 parts, the real T1 taxable
income parts, the real MB479 parts of lines 1 to 7, 17, 18, 19, 53, 55, 56, 57, 59, 60, 61, 62, 63,
64, 65, 66, 67, 68, 69 and 70, the line 71 input part and the new `mb479_line_72.yaml`, and types
in only the salary (and, in some tests, line 71). The MB479 form declaration is made up here,
exporting only lines 70, 71 and 72. The figures are line 70 with line 71 blank (95.65 / 0.00 /
0.00 / 0.00). They are hand-computed from the printed forms, not a CRA example.
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
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
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
LINE_PART = MB_PARTS / "mb479_line_72.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_credits_line_72"
LINE_70 = "ca-mb/mb479_credits_line_70"
LINE_71 = "ca-mb/mb479_book_publishing_credit_line_71"
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)
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
    "mb479_line_8.yaml",
    "mb479_line_12_inputs.yaml",
    "mb479_line_12.yaml",
    "mb479_line_14_inputs.yaml",
    "mb479_line_14_amount.yaml",
    "mb479_line_14.yaml",
    "mb479_line_15_inputs.yaml",
    "mb479_line_15_amount.yaml",
    "mb479_line_15.yaml",
    "mb479_line_16_inputs.yaml",
    "mb479_line_16_amount.yaml",
    "mb479_line_16.yaml",
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
    "mb479_line_62.yaml",
    "mb479_line_63_input.yaml",
    "mb479_line_64.yaml",
    "mb479_line_65_input.yaml",
    "mb479_line_66.yaml",
    "mb479_line_67_input.yaml",
    "mb479_line_68_input.yaml",
    "mb479_line_68.yaml",
    "mb479_line_69.yaml",
    "mb479_line_70.yaml",
    "mb479_line_71_input.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb479
      required: true
      exports:
        - ca-mb/mb479_credits_line_70
        - ca-mb/mb479_book_publishing_credit_line_71
        - ca-mb/mb479_credits_line_72
    capabilities: []
    """)

# salary, line 72: line 70 plus line 71, with line 71 left blank and read as 0.
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
    for number, part in enumerate(dict.fromkeys(_part_files()), start=2):
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


def _sheet(tmp_path: Path, salary: str, line_71: str | None = None) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_71 is not None:
        given.append(Artifact(manitoba_kinds().kind(LINE_71), D(line_71)))
    worksheets = _service(tmp_path).compute(
        TaxCalculationRequest(JurisdictionCode("CA-MB"), 2025, tuple(given))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _blank_rows(sheet: Worksheet) -> list[str]:
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    return [row for row in rows if row.lower().startswith("left blank, taken as ca$0")]


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
def test_line_72_is_line_70_when_line_71_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    value = _line(sheet, IDENTIFIER)

    assert value == _line(sheet, LINE_70) == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "line_71", "expected"),
    [
        ("10000", "10.00", "105.65"),
        ("200000", "0.00", "0.00"),
    ],
)
def test_line_72_adds_a_given_line_71_to_line_70(
    tmp_path: Path, salary: str, line_71: str, expected: str
) -> None:
    value = _line(_sheet(tmp_path, salary, line_71=line_71), IDENTIFIER)

    assert value == D(expected)
    assert str(value) == expected


def test_the_sheet_prints_no_title_and_the_reference_of_line_72(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "72"


def test_the_step_traces_one_sum_line_over_lines_70_and_71(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000", line_71="10.00")
    kinds = manitoba_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line.parts == ((kinds.kind(LINE_70), D("95.65")), (kinds.kind(LINE_71), D("10.00")))
    assert line.total == D("105.65")


def test_the_trace_prints_the_left_blank_row_of_line_72_when_line_71_is_blank(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "10000")
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert _blank_rows(sheet)
    (row,) = [
        r
        for r in rows
        if r.startswith("Line 70 (")
        and " plus line 71 " in r
        and "(CA$95.65)" in r
        and "(CA$0.00)" in r
    ]
    assert row.index("(CA$95.65)") < row.index("(CA$0.00)")
    assert "95.65" in row.split(" gives ")[1]


def test_the_part_is_one_untitled_sum_step_over_lines_70_and_71() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "72",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_70, LINE_71]},
        "blank": {LINE_71: "0"},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_CREDITS_LINE_72
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_a_negative_line_71_is_refused_by_its_kind() -> None:
    kind = manitoba_kinds().kind(LINE_71)

    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
