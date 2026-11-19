"""MB479 (2025) line 69, line 67 plus line 68, from the real parts.

Form text (Form MB479, CRA 5007-TC): "Line 69: Line 67 plus line 68 = ^". The form prints no maximum
for line 69, and the heading above the line is a section heading, so the step is untitled. Line 67,
"Line 67 and line 61380: Complete Form T1294.", is an optional input, read as 0 when left blank.
Line 68 is the computed credit of the adjusted cost of geothermal heat pumps (an optional input,
read as 0 when left out, so line 68 is never blank). Line 69 is one core/sum over line 67 and
line 68, as MB428 line 60 is over line 58 and the line 59 input; the blank line 67 is read as 0 and
the step prints its own "left blank, taken as 0" row.

The salary part, the line 67 and line 68 input parts, the line 68 part and the line 69 part are
loaded under a test-local header and form declaration, over the Manitoba package list of
`support.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_mb import catalog
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-MB")
FORM_NAME = "ca-mb/mb479"
LINE_67 = "ca-mb/mb479_green_energy_purchaser_credit_line_67"
COST_68 = "ca-mb/mb479_geothermal_heat_pump_cost_line_68"
LINE_68 = "ca-mb/mb479_geothermal_heat_pump_credit_line_68"
LINE_69 = "ca-mb/mb479_green_energy_credits_line_69"
SALARY = "ca/employment_income"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb479_line_69.yaml"
PART_NAMES = [
    "salary.yaml",
    "mb479_line_67_input.yaml",
    "mb479_line_68_input.yaml",
    "mb479_line_68.yaml",
    PART.name,
]

HEADER = dedent(f"""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - {SALARY}
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_69}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, input and line 68 and 69 parts, every other namespace being the package list's own.
    """
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, name in enumerate(PART_NAMES, start=2):
        text = (MB_PARTS / name).read_text(encoding="utf-8")
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(
    tmp_path: Path, salary: str, line_67: str | None = None, cost_68: str | None = None
) -> Worksheet:
    kinds = manitoba_kinds()
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if line_67 is not None:
        given.append(Artifact(kinds.kind(LINE_67), D(line_67)))
    if cost_68 is not None:
        given.append(Artifact(kinds.kind(COST_68), D(cost_68)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_69(
    tmp_path: Path, salary: str, line_67: str | None = None, cost_68: str | None = None
) -> Decimal:
    value = _sheet(tmp_path, salary, line_67, cost_68).get(manitoba_kinds().kind(LINE_69)).value
    assert isinstance(value, Decimal)
    return value


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    assert all(isinstance(step, dict) for step in steps)
    return steps


@pytest.mark.parametrize("salary", ["10000", "20000", "70000", "200000"])
def test_a_salary_only_caller_gets_0_on_line_69(tmp_path: Path, salary: str) -> None:
    # Lines 67 and 68's cost are left out, read as 0, so line 69 is 0.00 at every salary.
    value = _line_69(tmp_path, salary)

    assert value == D("0.00")
    assert str(value) == "0.00"


def test_line_69_is_line_67_when_only_line_67_is_given(tmp_path: Path) -> None:
    value = _line_69(tmp_path, "70000", line_67="1000.00")

    assert value == D("1000.00")
    assert str(value) == "1000.00"


def test_line_69_is_line_68_when_only_the_cost_is_given(tmp_path: Path) -> None:
    # A cost of 20000.00 x 7.5% = 1500.00 on line 68.
    value = _line_69(tmp_path, "70000", cost_68="20000.00")

    assert value == D("1500.00")
    assert str(value) == "1500.00"


def test_line_69_adds_line_67_and_line_68_when_both_are_given(tmp_path: Path) -> None:
    value = _line_69(tmp_path, "70000", line_67="1000.00", cost_68="20000.00")

    assert value == D("2500.00")
    assert str(value) == "2500.00"


def test_line_69_sums_line_68_after_it_is_rounded_half_up(tmp_path: Path) -> None:
    # 1000.07 x 7.5% = 75.00525, rounded half-up to 75.01 on line 68; plus line 67 of 10.10.
    value = _line_69(tmp_path, "70000", line_67="10.10", cost_68="1000.07")

    assert value == D("85.11")
    assert str(value) == "85.11"


def test_line_69_rounds_a_half_cent_of_line_68_up_before_the_sum(tmp_path: Path) -> None:
    # 0.07 x 7.5% = 0.00525, rounded half-up to 0.01 on line 68; the sum is 0.01, not 0.00.
    value = _line_69(tmp_path, "70000", cost_68="0.07")

    assert value == D("0.01")


def test_a_given_line_67_prints_no_left_blank_row_for_line_67(tmp_path: Path) -> None:
    blank = EnglishTraceRenderer().render_all(
        _sheet(tmp_path / "blank", "70000", cost_68="20000.00").trace
    )
    given = EnglishTraceRenderer().render_all(
        _sheet(tmp_path / "given", "70000", line_67="1000.00", cost_68="20000.00").trace
    )

    assert sum("left blank, taken as 0" in row.lower() for row in blank) == 1
    assert not any("left blank, taken as 0" in row.lower() for row in given)


def test_the_sheet_prints_no_title_and_the_reference_of_line_69(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = manitoba_kinds().kind(LINE_69).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "69"


def test_the_part_is_one_untitled_sum_step_over_lines_67_and_68() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/sum",
        "reference": "69",
        "unit": "ca/cad",
        "params": {"rounding": "ca-mb/cent_rounding"},
        "consumes": {"parts": [LINE_67, LINE_68]},
        "blank": {LINE_67: "0"},
        "produces": {"output": LINE_69},
    }
    assert "title" not in step


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(LINE_69)

    assert kind is catalog.MB479_GREEN_ENERGY_CREDITS_LINE_69
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_69
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
