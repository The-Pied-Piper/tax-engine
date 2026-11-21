"""MB479 (2025) line 61, the fertility treatment expenses times 40%, from the real parts.

Form text (Form MB479, CRA 5007-TC): "Fertility treatment tax credit:" / "Line 61: Eligible medical
expenses for fertility treatments Line 61268 ^" / "multiplied by 40% (maximum $16,000) = ^". The
input is the eligible medical expenses (`ca-mb/mb479_fertility_treatment_expenses_line_61`), which
the line 61 input part declares as optional, read as 0 when left out. Line 61 is one calculation:
40% of the expenses, a printed rate held in the `ca-mb/fertility_treatment_credit_rate` dataset,
rounded half-up to the cent. The output is `ca-mb/mb479_fertility_treatment_credit_line_61`. The
capping step is titled with the heading the form prints above the line, "Fertility treatment tax
credit".

The form prints the maximum between "multiplied by 40%" and "=", so it bounds the line's result, as
the same form prints it on line 32 and as Ontario's LIFT line 5 is built. Line 61 is therefore two
steps: 40% of the expenses rounded half-up to the cent (`core/apply_rate`, read as 0 when the
input is left out, so it prints the "left blank, taken as 0" row), then that figure capped at the
printed maximum of 16000.00 (`core/capped_amount`, `ca-mb/fertility_treatment_credit_maximum`).

The T1 employment income form, the input part and the line 61 part are loaded under a test-local
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
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_mb import catalog
from tax_engine.jurisdictions.ca_mb.catalog import MB479_FERTILITY_TREATMENT_CREDIT_LINE_61
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)
from tests.kinds import non_negative
from tests.manifest_support import T1_LINE_10100_INPUT, inputs_without_form

D = Decimal
CODE = JurisdictionCode("CA-MB")
FORM_NAME = "ca-mb/mb479"
AMOUNT = "ca-mb/mb479_fertility_treatment_expenses_line_61"
BEFORE_MAXIMUM = "ca-mb/mb479_fertility_treatment_credit_before_maximum_line_61"
LINE_61 = "ca-mb/mb479_fertility_treatment_credit_line_61"
SALARY = "ca/employment_income"
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb479_line_61.yaml"

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
        - {LINE_61}
    capabilities: []
    """)


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real salary, input and line 61 parts, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    # The salary input belongs to the T1 employment income form, which this manifest does not
    # declare and no step here reads, so the salary joins the default form as the caller's own.
    (folder / "01_salary_input.yaml").write_text(
        inputs_without_form(T1_LINE_10100_INPUT), encoding="utf-8"
    )
    names = ["mb479_line_61_input.yaml", PART.name]
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


def _line_61(tmp_path: Path, salary: str, amount: str | None) -> Decimal:
    value = _sheet(tmp_path, salary, amount).get(manitoba_kinds().kind(LINE_61)).value
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
    # The amount is left out, read as 0 by the step's blank rule, so line 61 is 0.00 throughout.
    value = _line_61(tmp_path, salary, None)

    assert value == D("0.00")
    assert str(value) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # An amount of 1000.00: 40% of 1000.00 is 400.00.
        ("1000.00", "400.00"),
        # 0.03 x 40% = 0.012, rounded half-up to 0.01.
        ("0.03", "0.01"),
        # The printed "(maximum $16,000)" bounds the result: 50000.00 x 40% = 20000.00, capped.
        ("50000.00", "16000.00"),
        # 39999.97 x 40% = 15999.988, rounded half-up to 15999.99, under the maximum.
        ("39999.97", "15999.99"),
    ],
)
def test_line_61_is_40_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    value = _line_61(tmp_path, "70000", amount)

    assert value == D(expected)
    assert str(value) == expected


def test_a_negative_amount_raises() -> None:
    kind = manitoba_kinds().kind(AMOUNT)

    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


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


def test_the_part_is_an_apply_rate_step_then_a_capped_amount_step() -> None:
    assert _steps() == [
        {
            "name": "core/apply_rate",
            "title": "Fertility treatment credit before the maximum",
            "unit": "ca/cad",
            "params": {"rate": "ca-mb/fertility_treatment_credit_rate"},
            "consumes": {"base": AMOUNT},
            "blank": {"base": "0"},
            "produces": {"output": BEFORE_MAXIMUM},
        },
        {
            "name": "core/capped_amount",
            "title": "Fertility treatment tax credit",
            "reference": "61",
            "unit": "ca/cad",
            "params": {"cap": "ca-mb/fertility_treatment_credit_maximum"},
            "consumes": {"base": BEFORE_MAXIMUM},
            "produces": {"output": LINE_61},
        },
    ]


def test_the_step_keys_are_in_the_order_of_on428_a_line_5() -> None:
    rate, cap = _steps()

    assert list(rate) == ["name", "title", "unit", "params", "consumes", "blank", "produces"]
    assert list(cap) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]


def test_the_capping_step_is_titled_with_the_heading_the_form_prints_above_the_line() -> None:
    _, cap = _steps()

    assert cap["title"] == "Fertility treatment tax credit"


def test_the_intermediate_step_has_a_plain_words_title_and_no_reference() -> None:
    rate, _ = _steps()

    assert rate["title"] == "Fertility treatment credit before the maximum"
    assert "reference" not in rate


def test_the_before_maximum_kind_is_a_registered_non_negative_decimal_amount() -> None:
    constant = catalog.MB479_FERTILITY_TREATMENT_CREDIT_BEFORE_MAXIMUM_LINE_61
    kind = manitoba_kinds().kind(BEFORE_MAXIMUM)

    assert kind is constant
    assert isinstance(kind, AmountKind)
    assert kind.identifier == BEFORE_MAXIMUM
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))


def test_the_kind_is_a_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(LINE_61)

    assert kind is MB479_FERTILITY_TREATMENT_CREDIT_LINE_61
    assert isinstance(kind, AmountKind)
    assert kind.identifier == LINE_61
    assert kind.value_type is Decimal
    assert non_negative(kind)
    with pytest.raises(NegativeArtifactError):
        Artifact(kind, D("-0.01"))
