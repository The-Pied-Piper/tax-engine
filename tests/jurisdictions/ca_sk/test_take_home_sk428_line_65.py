"""SK428 (2025) line 65, the minimum tax carryover times 50%, from the real parts, real engine.

Form text (Form SK428, CRA 5008-C): "Saskatchewan minimum tax carryover:" / "Line 65: Amount from
line 40427 of your return Line 61540" / "multiplied by 50% =". The input is the amount from line
40427 of the return (`ca-sk/sk428_minimum_tax_carryover_amount_line_65`), which the inputs part
declares as optional, read as 0 when left out. Line 65 box B is one calculation: 50% of the amount,
a printed rate held in the `ca-sk/minimum_tax_rate` dataset, rounded half-up to the cent. The output
is `ca-sk/sk428_minimum_tax_carryover_line_65`. The step is titled with the heading the form prints
above the line, "Saskatchewan minimum tax carryover". Because the input is blank for a salary-only
caller, the step prints its own "left blank, taken as 0" row.

The T1 employment income form, the inputs part and the line 65 part are loaded under a test-local
header and form declaration, over the Saskatchewan package list of `support.py`."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_sk
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
from tax_engine.jurisdictions.ca_sk.catalog import SK428_MINIMUM_TAX_CARRYOVER_LINE_65
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
CODE = JurisdictionCode("CA-SK")
FORM_NAME = "ca-sk/sk428"
AMOUNT = "ca-sk/sk428_minimum_tax_carryover_amount_line_65"
LINE_65 = "ca-sk/sk428_minimum_tax_carryover_line_65"
SALARY = "ca/employment_income"
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
# The T1 employment income form owns the salary input: its declaration, its line 10100 step and
# the input part, as the real parts have them.
T1_PARTS = (*form_parts("t1_employment_income"),)
PART = SK_PARTS / "sk428_line_65.yaml"

HEADER = dedent("""\
    jurisdiction: CA-SK
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
        - {LINE_65}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, a form declaration and
    the real salary, inputs and line 65 parts, the other namespaces being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    parts = [*T1_PARTS, SK_PARTS / "sk428_line_65_inputs.yaml", PART]
    for number, part in enumerate(parts, start=2):
        text = part.read_text(encoding="utf-8")
        (folder / f"{number:02d}_{part.name}").write_text(text, encoding="utf-8")
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str, amount: str | None) -> Worksheet:
    kinds = saskatchewan_kinds()
    given = [Artifact(kinds.kind(SALARY), D(salary))]
    if amount is not None:
        given.append(Artifact(kinds.kind(AMOUNT), D(amount)))
    (sheet,) = _service(tmp_path).compute(CODE, 2025, *given)[FORM_NAME]
    return sheet


def _line_65(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(saskatchewan_kinds().kind(LINE_65)).value
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


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_salary_only_caller_who_leaves_out_the_amount_gets_0(tmp_path: Path, salary: str) -> None:
    # The amount is left out, read as 0 by the step's blank rule, so line 65 is 0.00 throughout.
    value = _line_65(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 50% of 1000.00 is 500.00.
        ("1000.00", "500.00"),
        # An amount of 0 gives 0.
        ("0", "0.00"),
        # 0.01 x 50% = 0.005, a tie, rounded half-up to 0.01.
        ("0.01", "0.01"),
    ],
)
def test_line_65_is_50_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_65(tmp_path, "70000", amount)

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


def test_the_part_is_one_apply_rate_step_over_the_line_65_amount() -> None:
    assert _step() == {
        "name": "core/apply_rate",
        "title": "Saskatchewan minimum tax carryover",
        "reference": "65 box B",
        "unit": "ca/cad",
        "params": {"rate": "ca-sk/minimum_tax_rate"},
        "consumes": {"base": AMOUNT},
        "blank": {"base": "0"},
        "produces": {"output": LINE_65},
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
    assert _step()["title"] == "Saskatchewan minimum tax carryover"


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = saskatchewan_kinds().kind(LINE_65)

    assert kind is SK428_MINIMUM_TAX_CARRYOVER_LINE_65
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_65
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_a_negative_amount_is_rejected() -> None:
    kind = saskatchewan_kinds().kind(AMOUNT)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
