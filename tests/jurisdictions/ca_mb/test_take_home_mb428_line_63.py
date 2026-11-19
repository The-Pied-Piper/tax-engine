"""MB428 (2025) line 63, the minimum tax carryover times 50%, from the real parts, real engine.

Form text (Form MB428, CRA 5007-C, read 2026-11-17): "Manitoba minimum tax carryover:" /
"Line 63 and line 61540: Amount from line 40427 of your return ^" / "multiplied by 50% = ^". The
input is the amount from line 40427 of the return (`ca-mb/mb428_minimum_tax_carryover_line_63`),
which the inputs part declares as optional, read as 0 when left out. Line 63 is one calculation:
50% of the amount, a printed rate held in the `ca-mb/minimum_tax_rate` dataset, rounded half-up to
the cent. The output is `ca-mb/mb428_minimum_tax_carryover_credit_line_63`. The step is
titled with the heading the form prints above the line, "Manitoba minimum tax carryover". Because
the input is blank for a salary-only caller, the step prints its own "left blank, taken as 0" row.

The salary part, the inputs part and the line 63 part are loaded under a test-local header and form
declaration, over the Manitoba package list of `support.py`.
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
from tax_engine.jurisdictions.ca_mb.catalog import MB428_MINIMUM_TAX_CARRYOVER_CREDIT_LINE_63
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
FORM_NAME = "ca-mb/mb428"
AMOUNT = "ca-mb/mb428_minimum_tax_carryover_line_63"
LINE_63 = "ca-mb/mb428_minimum_tax_carryover_credit_line_63"
SALARY = "ca/employment_income"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb428_line_63.yaml"

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
        - {LINE_63}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, inputs and line 63 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    names = ["salary.yaml", "mb428_credits_line_63_input.yaml", PART.name]
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
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if amount is not None:
        given.append(Artifact(kinds.kind(AMOUNT), D(amount)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_63(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(manitoba_kinds().kind(LINE_63)).value
    assert isinstance(value, Decimal)
    return value


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize("salary", ["10000", "200000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 63 is 0.00 throughout.
    value = _line_63(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 50% of 1000.00 is 500.00.
        ("1000.00", "500.00"),
        # 333.33 x 50% = 166.665, a tie, rounded half-up to 166.67.
        ("333.33", "166.67"),
    ],
)
def test_line_63_is_50_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_63(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_a_blank_amount_prints_the_steps_own_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", None)

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    blank_rows = [row for row in rows if "left blank, taken as 0" in row.lower()]
    assert len(blank_rows) == 1


def test_a_given_amount_prints_no_left_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "1000.00")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert rows
    assert not any("left blank, taken as 0" in row.lower() for row in rows)


def test_the_part_is_one_apply_rate_step_over_the_line_63_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "Manitoba minimum tax carryover",
        "reference": "63",
        "unit": "ca/cad",
        "params": {"rate": "ca-mb/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "blank": {"base": "0"},
        "produces": {"output": LINE_63},
    }


def test_the_step_keys_are_in_the_order_of_the_neighbouring_parts() -> None:
    assert list(_step()) == [
        "name",
        "title",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]


def test_the_step_is_titled_with_the_heading_the_form_prints_above_the_line() -> None:
    assert _step()["title"] == "Manitoba minimum tax carryover"


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(LINE_63)

    assert kind is MB428_MINIMUM_TAX_CARRYOVER_CREDIT_LINE_63
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_63
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
