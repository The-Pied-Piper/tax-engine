"""MB479 (2025) line 70, line 66 plus line 69, from the salary alone, real parts.

Form text (Form MB479, CRA 5007-TC): "Line 70: Line 66 plus line 69 = ^". Line 70 prints no label
and no maximum, so its step has no title. It is one core/sum over line 66 and line 69, which are
both always computed (each reads its own optional inputs as 0 in its own step), so the step has no
blank rule and prints no "left blank, taken as 0" row of its own.

The test composes the T1 employment income form, the real Schedule 8 parts, the real T1 taxable
income parts, the real MB479 parts of lines 1 to 7, 17, 18, 19, 53, 55, 56, 57, 59, 60, 61, 62, 63
and 64, the line 65 input part, line 66, the line 67 and 68 input parts, line 68, line 69 and the
new `mb479_line_70.yaml`, and types in only the salary (and, in some tests, lines 65, 67 and the
cost on line 68). The MB479 form declaration is made up here, exporting only lines 66, 69 and 70.
The figures are line 66 with lines 65, 67 and 68 blank (95.65 / 0.00 / 0.00 / 0.00). They are
hand-computed from the printed forms, not a CRA example.
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
LINE_PART = MB_PARTS / "mb479_line_70.yaml"
FORM_NAME = "ca-mb/mb479"
IDENTIFIER = "ca-mb/mb479_credits_line_70"
LINE_66 = "ca-mb/mb479_credits_line_66"
LINE_69 = "ca-mb/mb479_green_energy_credits_line_69"
LINE_65 = "ca-mb/mb479_odour_control_credit_line_65"
LINE_67 = "ca-mb/mb479_green_energy_purchaser_credit_line_67"
COST_68 = "ca-mb/mb479_geothermal_heat_pump_cost_line_68"
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
        - ca-mb/mb479_credits_line_66
        - ca-mb/mb479_green_energy_credits_line_69
        - ca-mb/mb479_credits_line_70
    capabilities: []
    """)

# salary, line 70: line 66 plus line 69, with lines 65, 67 and 68 left blank and read as 0.
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


def _sheet(
    tmp_path: Path,
    salary: str,
    line_65: str | None = None,
    line_67: str | None = None,
    cost_68: str | None = None,
) -> Worksheet:
    kinds = manitoba_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    for name, amount in ((LINE_65, line_65), (LINE_67, line_67), (COST_68, cost_68)):
        if amount is not None:
            given.append(Artifact(kinds.kind(name), D(amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-MB"), 2025, *given)
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
def test_line_70_is_line_66_when_lines_65_67_and_68_are_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    value = _line(sheet, IDENTIFIER)

    assert value == _line(sheet, LINE_66) == D(expected)
    assert _line(sheet, LINE_69) == D("0.00")
    assert str(value) == expected


def test_line_70_is_a_given_line_65_through_line_66(tmp_path: Path) -> None:
    value = _line(_sheet(tmp_path, "70000", line_65="400"), IDENTIFIER)

    assert value == D("400.00")
    assert str(value) == "400.00"


def test_line_70_is_a_given_line_67_through_line_69(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_67="1000.00")

    assert _line(sheet, LINE_69) == D("1000.00")
    value = _line(sheet, IDENTIFIER)
    assert value == D("1000.00")
    assert str(value) == "1000.00"


def test_line_70_is_the_line_68_credit_through_line_69(tmp_path: Path) -> None:
    # A cost of 20000.00 x 7.5% = 1500.00 on line 68, so 1500.00 on line 69.
    value = _line(_sheet(tmp_path, "70000", cost_68="20000.00"), IDENTIFIER)

    assert value == D("1500.00")
    assert str(value) == "1500.00"


def test_line_70_adds_line_66_and_line_69_when_both_are_given(tmp_path: Path) -> None:
    # Line 66 is 95.65 + 100 = 195.65 at 10,000; line 69 is 1000.00 + 1500.00 = 2500.00.
    sheet = _sheet(tmp_path, "10000", line_65="100", line_67="1000.00", cost_68="20000.00")

    assert _line(sheet, LINE_66) == D("195.65")
    assert _line(sheet, LINE_69) == D("2500.00")
    value = _line(sheet, IDENTIFIER)
    assert value == D("2695.65")
    assert str(value) == "2695.65"


def test_line_70_sums_line_69_after_it_is_rounded_half_up(tmp_path: Path) -> None:
    # 0.07 x 7.5% = 0.00525, rounded half-up to 0.01 on line 68; plus 95.65 on line 66.
    value = _line(_sheet(tmp_path, "10000", cost_68="0.07"), IDENTIFIER)

    assert value == D("95.66")
    assert str(value) == "95.66"


def test_line_70_has_no_left_blank_row_of_its_own(tmp_path: Path) -> None:
    # Each input left blank (lines 65, 67 and the cost on line 68) adds exactly one row from the
    # step that reads it; line 70's step has no blank rule and adds none.
    given = _blank_rows(
        _sheet(tmp_path / "given", "10000", line_65="100", line_67="1000.00", cost_68="20000.00")
    )
    blank = _blank_rows(_sheet(tmp_path / "blank", "10000"))

    assert len(blank) == len(given) + 3


def test_the_sheet_prints_no_title_and_the_reference_of_line_70(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000")
    label = manitoba_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "70"


def test_the_step_traces_one_sum_line_over_lines_66_and_69(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "10000", line_67="1000.00")
    kinds = manitoba_kinds()

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line.parts == ((kinds.kind(LINE_66), D("95.65")), (kinds.kind(LINE_69), D("1000.00")))
    assert line.total == D("1095.65")


def test_the_part_is_one_untitled_sum_step_over_lines_66_and_69() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "70",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_66, LINE_69]},
        "produces": {"output": IDENTIFIER},
    }
    assert "title" not in step


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB479_CREDITS_LINE_70
    assert isinstance(kind, AmountKind)
    assert kind.identifier == IDENTIFIER
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
