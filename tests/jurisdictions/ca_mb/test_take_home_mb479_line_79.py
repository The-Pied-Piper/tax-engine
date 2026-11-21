"""MB479 (2025) line 79, eligible teaching supplies expenses times 15%, from the real parts.

Form text (Form MB479, CRA 5007-tc-25e.txt): "Teaching expense tax credit:" / "Line 79: Eligible
teaching supplies expenses (maximum $1,000) Line 61495 ^ multiplied by 15% = ^". The input is
`ca-mb/mb479_teaching_supplies_expenses_line_79`, which the line 79 input part declares as optional,
blank by default. The printed maximum precedes the box, so it bounds the entry: an amount above it
is rejected, not capped. Three steps: `core/credit_amount` supplies the maximum (no title, no
reference), `core/at_most` checks the entry against it (no title, no reference, an intermediate),
and `core/apply_rate` multiplies the checked amount by 15%, rounded half-up to the cent, and
carries the reference "79". The heading above the line is a section heading, so no step is titled.

The T1 employment income form, the input part and the line 79 part are loaded under a test-local
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
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
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
AMOUNT = "ca-mb/mb479_teaching_supplies_expenses_line_79"
MAXIMUM = "ca-mb/mb479_teaching_supplies_expenses_maximum"
CHECKED = "ca-mb/mb479_teaching_supplies_expenses_checked_line_79"
LINE_79 = "ca-mb/mb479_teaching_expense_credit_line_79"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb479_line_79.yaml"

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
        - {LINE_79}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, input and line 79 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    names = ["mb479_line_79_input.yaml", PART.name]
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
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_79(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(manitoba_kinds().kind(LINE_79)).value
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
    # The amount is left out, passed on blank by the check and read as 0 by the rate step, so
    # line 79 is 0.00 throughout.
    value = _line_79(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # 1000 x 15% = 150.00 exactly, the printed maximum itself.
        ("1000", "150.00"),
        # 333.33 x 15% = 49.9995, rounded half-up to 50.00.
        ("333.33", "50.00"),
    ],
)
def test_line_79_is_15_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_79(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_one_cent_above_the_maximum_is_rejected_not_capped(tmp_path: Path) -> None:
    with pytest.raises(InputAboveBoundError):
        _line_79(tmp_path, "70000", "1000.01")


def test_a_blank_amount_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", None)

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    blank_rows = [row for row in rows if "left blank, taken as 0" in row.lower()]
    assert len(blank_rows) == 1


def test_a_given_amount_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "1000")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert rows
    assert not any("left blank, taken as 0" in row.lower() for row in rows)


def test_the_part_names_the_form_and_has_three_steps_in_order() -> None:
    first, second, third = _steps()

    assert first["name"] == "core/credit_amount"
    assert second["name"] == "core/at_most"
    assert third["name"] == "core/apply_rate"


def test_the_first_step_supplies_the_printed_maximum_with_no_title_and_no_reference() -> None:
    first, _, _ = _steps()

    assert "title" not in first
    assert "reference" not in first
    assert first == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": "ca-mb/teaching_supplies_expenses_maximum"},
        "produces": {"output": MAXIMUM},
    }


def test_the_second_step_is_a_printed_title_unreferenced_intermediate() -> None:
    _, second, _ = _steps()

    assert "reference" not in second
    assert second == {
        "name": "core/at_most",
        "title": "Eligible teaching supplies expenses",
        "unit": "ca/cad",
        "consumes": {"amount": AMOUNT, "bound": MAXIMUM},
        "blank": {"amount": "pass_on"},
        "produces": {"output": CHECKED},
    }


def test_the_third_step_is_line_79_untitled_and_referenced() -> None:
    _, _, third = _steps()

    assert "title" not in third
    assert third == {
        "name": "core/apply_rate",
        "reference": "79",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/teaching_expense_credit_rate"},
        "consumes": {"base": CHECKED},
        "blank": {"base": "0"},
        "produces": {"output": LINE_79},
    }


def test_the_third_step_keys_are_in_the_order_of_the_line_68_rate_step() -> None:
    _, _, third = _steps()

    assert list(third) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]


@pytest.mark.parametrize("identifier", [MAXIMUM, CHECKED, LINE_79])
def test_each_new_kind_is_a_registered_non_negative_decimal_amount_kind(identifier: str) -> None:
    kind = manitoba_kinds().kind(identifier)

    assert isinstance(kind, AmountKind)
    assert kind.identifier == identifier
    assert kind.value_type is Decimal
    assert non_negative(kind)
