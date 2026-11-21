"""Worksheet NL428 (2025) line 4, line 2 minus line 3 (not below 0), from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt): "Line 2: Amount from line 23600 of
your return", "Line 3: Income threshold 38,712.00" and "Line 4: Line 2 minus line 3 (if negative,
enter \\"0\\") = ^". The form names no label for any of the three lines, so no step has a title.

The part `worksheet_nl428_line_4.yaml` is three steps. Line 2 is a core/record_total over the T1
net income (`ca/t1_taxable_income.net_income`, line 23600 after its floor). Line 3 is a
core/credit_amount over the `ca-nl/age_income_threshold` dataset (38,712.00, claimed whole). Line 4
is a core/subtract_not_below_zero step over line 2 (`amount`) and line 3 (`less`), rounded half-up
to the cent by `ca-nl/cent_rounding`. Each step carries its line number as the reference ("2", "3",
"4"). The three kinds are non-negative. The "born in 1960 or earlier" condition is not read here:
line 4 is a plain subtraction.

The test composes the real federal parts the T1 taxable income form needs (Schedule 8 and the T1
lines 15000, 23300, 23400, 23600, 23600 signed and 26000 with their inputs) and the real
`worksheet_nl428_line_4.yaml`, and types in only the salary. The header (which declares the salary
input) and the Worksheet NL428 form declaration (exporting lines 2, 3 and 4) are made up here,
because the shared scaffold owns them. Newfoundland and Labrador is not yet listed in the
registrations, so the service is built over the package list of `support.py`.

Figures (hand-computed with Decimal, not a CRA example). Line 2 is the salary less the enhanced CPP
deduction (2025): 1% of the earnings from 3,500 to 71,300 plus 4% of the earnings from 71,300 to
81,200, each rounded half-up to the cent. Line 3 is 38,712.00.
- 30,000: deduction 265.00, line 2 = 29,735.00, below line 3, so line 4 = 0.00 (the floor).
- 50,000: deduction 465.00, line 2 = 49,535.00, line 4 = 49,535.00 - 38,712.00 = 10,823.00.
- The exact boundary: a salary of 39,067.68 has deduction 355.68 (1% of 35,567.68 is 355.6768),
  so line 2 = 38,712.00 = line 3 and line 4 = 0.00. One cent of salary more, 39,067.69, gives
  deduction 355.68 (355.6769), line 2 = 38,712.01 and line 4 = 0.01. One cent less, 39,067.67,
  gives deduction 355.68 (355.6767), line 2 = 38,711.99, below line 3, and line 4 = 0.00.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_nl
import tax_engine.jurisdictions.ca_nl.catalog as nl_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
PART = NL_PARTS / "worksheet_nl428_line_4.yaml"
LINE_2 = "ca-nl/worksheet_nl428_age_amount_net_income_line_2"
LINE_3 = "ca-nl/worksheet_nl428_age_amount_income_threshold_line_3"
LINE_4 = "ca-nl/worksheet_nl428_age_amount_line_4"
THRESHOLD = "ca-nl/age_income_threshold"
ROUNDING = "ca-nl/cent_rounding"
FORM_NAME = "ca-nl/nl428_worksheet"
# The real federal parts the T1 taxable-income form needs, beside the salary and the three lines.
FEDERAL_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    inputs:
      - name: ca/employment_income
        title: "Employment income"
        reference: "10100"
        unit: ca/cad
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_2}
        - {LINE_3}
        - {LINE_4}
    capabilities: []
    """)

# salary, line 2, line 3, line 4. Line 2 is below line 3: line 4 is the floor, 0.00.
FLOORED = [
    ("30000", "29735.00", "38712.00", "0.00"),
    ("39067.67", "38711.99", "38712.00", "0.00"),
]
# Line 2 equals line 3 exactly: the difference is 0.00 without the floor biting.
BOUNDARY = ("39067.68", "38712.00", "38712.00", "0.00")
# Line 2 above line 3.
POSITIVE = [
    ("39067.69", "38712.01", "38712.00", "0.01"),
    ("50000", "49535.00", "38712.00", "10823.00"),
]


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in the Newfoundland and
    Labrador catalog."""
    path = Path(nl_catalog.__file__)
    body = ast.parse(path.read_text(encoding="utf-8")).body
    for statement, following in zip(body, body[1:], strict=False):
        if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
            continue
        constants = [each.value for each in statement.value.args if isinstance(each, ast.Constant)]
        if (
            identifier.rpartition("/")[2] in constants
            and isinstance(following, ast.Expr)
            and isinstance(following.value, ast.Constant)
        ):
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Newfoundland and Labrador manifest of a test header, a form
    declaration and the real part files, every other namespace being the package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, found in enumerate(_part_files(), start=2):
        text = (
            inputs_without_form(found)
            if found.name.endswith("_inputs.yaml") and found.is_relative_to(FEDERAL_FORMS)
            else found.read_text(encoding="utf-8")
        )
        (folder / f"{number:02d}_{found.name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(),
            newfoundland_parameter_parsers(),
            newfoundland_units(),
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _rounding() -> Any:
    return YamlParameterSource(
        newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


@pytest.mark.parametrize(("salary", "line_2", "line_3", "expected"), FLOORED)
def test_line_4_is_zero_while_line_2_is_below_line_3(
    tmp_path: Path, salary: str, line_2: str, line_3: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    # Line 2 is recomputed from the salary, not only typed here.
    assert _net_income(D(salary)) == D(line_2)
    assert _value(sheet, LINE_2) == D(line_2)
    assert _value(sheet, LINE_3) == D(line_3)
    assert D(line_2) < D(line_3)
    line_4 = _value(sheet, LINE_4)
    assert line_4 == D(expected)
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_4) == "0.00"
    assert line_4.as_tuple().exponent == -2
    assert not line_4.is_signed()


def test_line_4_is_zero_when_line_2_equals_line_3_exactly(tmp_path: Path) -> None:
    salary, line_2, line_3, expected = BOUNDARY
    sheet = _sheet(tmp_path, salary)

    # 1% of (39,067.68 - 3,500) = 355.6768, rounded to 355.68; 39,067.68 - 355.68 = 38,712.00.
    assert _net_income(D(salary)) == D(line_2)
    assert D(line_2) == D(line_3)
    assert _value(sheet, LINE_2) == D(line_2)
    assert _value(sheet, LINE_3) == D(line_3)
    assert _value(sheet, LINE_4) == D(expected)
    assert str(_value(sheet, LINE_4)) == "0.00"


@pytest.mark.parametrize(("salary", "line_2", "line_3", "expected"), POSITIVE)
def test_line_4_is_line_2_minus_line_3_when_line_2_is_above_line_3(
    tmp_path: Path, salary: str, line_2: str, line_3: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _net_income(D(salary)) == D(line_2)
    assert _value(sheet, LINE_2) == D(line_2)
    assert _value(sheet, LINE_3) == D(line_3)
    assert D(line_2) - D(line_3) == D(expected)
    assert _value(sheet, LINE_4) == D(expected)
    assert str(_value(sheet, LINE_4)) == expected


def test_line_3_is_the_income_threshold_at_every_salary(tmp_path: Path) -> None:
    for salary in ("30000", "50000", "200000"):
        assert _value(_sheet(tmp_path / salary, salary), LINE_3) == D("38712.00")


def test_line_4_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")

    assert not sheet.get(newfoundland_kinds().kind(LINE_4)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not any("left blank, taken as" in row.lower() for row in rows)


def test_the_floored_row_traces_the_subtraction_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "30000")
    kinds = newfoundland_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_4),
        minuend=kinds.kind(LINE_2),
        minuend_amount=D("29735.00"),
        subtrahend=kinds.kind(LINE_3),
        subtrahend_amount=D("38712.00"),
        rounding=_rounding().rounding,
        result=D("0.00"),
    )


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")
    kinds = newfoundland_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_4),
        minuend=kinds.kind(LINE_2),
        minuend_amount=D("49535.00"),
        subtrahend=kinds.kind(LINE_3),
        subtrahend_amount=D("38712.00"),
        rounding=_rounding().rounding,
        result=D("10823.00"),
    )


def test_the_part_is_three_untitled_steps_each_carrying_its_line_number() -> None:
    steps = _steps()

    assert [step["name"] for step in steps] == [
        "core/record_total",
        "core/credit_amount",
        "core/subtract_not_below_zero",
    ]
    assert all("title" not in step for step in steps)
    assert [step.get("reference") for step in steps] == ["2", "3", "4"]


def test_line_2_is_a_record_total_over_the_t1_net_income() -> None:
    step = _steps()[0]

    assert list(step) == ["name", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "reference": "2",
        "unit": "ca/cad",
        "consumes": {"records": "ca/t1_taxable_income.net_income"},
        "produces": {"output": LINE_2},
    }


def test_line_3_is_the_age_income_threshold_claimed_whole() -> None:
    step = _steps()[1]

    assert list(step) == ["name", "reference", "unit", "params", "produces"]
    assert step == {
        "name": "core/credit_amount",
        "reference": "3",
        "unit": "ca/cad",
        "params": {"amount": THRESHOLD},
        "produces": {"output": LINE_3},
    }


def test_line_4_is_a_subtract_not_below_zero_step_with_no_blank_rule() -> None:
    step = _steps()[2]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_2, "less": LINE_3},
        "produces": {"output": LINE_4},
    }


@pytest.mark.parametrize("identifier", [LINE_2, LINE_3, LINE_4])
def test_each_kind_is_a_registered_non_negative_decimal_amount(identifier: str) -> None:
    kind = newfoundland_kinds().kind(identifier)

    assert identifier.startswith("ca-nl/")
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


@pytest.mark.parametrize("identifier", [LINE_2, LINE_3, LINE_4])
def test_each_kind_rejects_a_negative_amount(identifier: str) -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(newfoundland_kinds().kind(identifier), D("-0.01"))


@pytest.mark.parametrize(
    ("identifier", "quote"),
    [
        (LINE_2, 'line 2 "Line 2: Amount from line 23600 of your return"'),
        (LINE_3, 'line 3 "Line 3: Income threshold 38,712.00"'),
        (LINE_4, 'line 4 "Line 4: Line 2 minus line 3 (if negative, enter "0")'),
    ],
)
def test_each_docstring_quotes_the_form_text(identifier: str, quote: str) -> None:
    doc = squashed(docstring_of(identifier))

    assert "Worksheet NL428" in doc
    assert quote in doc
