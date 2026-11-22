"""MB479 (2025) line 68, the adjusted cost of geothermal heat pumps times 7.5%, from the real parts.

Form text (Form MB479, CRA 5007-TC): "Green energy equipment tax credit (manufacturer):" /
"Line 68 and line 61390: 7.5% of the adjusted cost of geothermal heat pumps ^". The input is the
adjusted cost of geothermal heat pumps (`ca-mb/mb479_geothermal_heat_pump_cost_line_68`), which the
line 68 input part declares as optional, read as 0 when left out. Line 68 is one calculation: 7.5%
of the cost, a printed rate held in the `ca-mb/geothermal_heat_pump_credit_rate` dataset, rounded
half-up to the cent. The output is `ca-mb/mb479_geothermal_heat_pump_credit_line_68`. The form
prints no maximum for line 68, and the heading above the line is a section heading, so the step is
untitled.

The T1 employment income form, the input part and the line 68 part are loaded under a test-local
header and form declaration, over the Manitoba package list of `support.py`."""

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
from tax_engine.application.models.calculation_request import TaxCalculationRequest
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
AMOUNT = "ca-mb/mb479_geothermal_heat_pump_cost_line_68"
LINE_68 = "ca-mb/mb479_geothermal_heat_pump_credit_line_68"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb479_line_68.yaml"

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_68}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, input and line 68 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    names = ["mb479_line_68_input.yaml", PART.name]
    for number, name in enumerate(names, start=2):
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


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Worksheet:
    kinds = manitoba_kinds()
    given: list[Artifact[Any]] = []
    if amount is not None:
        given.append(Artifact(kinds.kind(AMOUNT), D(amount)))
    (sheet,) = _service(tmp_path).compute(TaxCalculationRequest(CODE, 2025, tuple(given)))[
        FORM_NAME
    ]
    return sheet


def _line_68(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(manitoba_kinds().kind(LINE_68)).value
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


@pytest.mark.parametrize("salary", ["10000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 68 is 0.00 throughout.
    value = _line_68(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # 0.06 x 7.5% = 0.0045, rounded half-up to 0.00.
        ("0.06", "0.00"),
        # 0.07 x 7.5% = 0.00525, rounded half-up to 0.01.
        ("0.07", "0.01"),
        # 100.00 x 7.5% = 7.50 exactly.
        ("100.00", "7.50"),
    ],
)
def test_line_68_is_7_5_percent_of_the_cost_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_68(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_a_blank_cost_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", None)

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    blank_rows = [row for row in rows if "left blank, taken as 0" in row.lower()]
    assert len(blank_rows) == 1


def test_a_given_cost_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert rows
    assert not any("left blank, taken as 0" in row.lower() for row in rows)


def test_the_part_is_one_apply_rate_step_that_carries_the_reference() -> None:
    assert _steps() == [
        {
            "name": "core/apply_rate",
            "reference": "68",
            "unit": "ca/cad",
            "params": {"rate": "ca-mb/geothermal_heat_pump_credit_rate"},
            "consumes": {"base": AMOUNT},
            "blank": {"base": "0"},
            "produces": {"output": LINE_68},
        },
    ]


def test_the_step_keys_are_in_the_order_of_the_line_61_rate_step() -> None:
    (step,) = _steps()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]


def test_the_step_is_untitled_because_the_form_prints_a_section_heading_only() -> None:
    (step,) = _steps()

    assert "title" not in step


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(LINE_68)

    assert kind is catalog.MB479_GEOTHERMAL_HEAT_PUMP_CREDIT_LINE_68
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_68
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
