"""Worksheet NL428 (2025) line 7, line 1 minus line 6 (not below 0), from the real parts.

Form text (Worksheet NL428, CRA 5001-D, 2025, 5001-d-25e.txt): "Line 1: Maximum amount 7,064.00",
"Line 6: Line 4 multiplied by the percentage from line 5 = ^" and "Line 7: Line 1 minus line 6 (if
negative, enter \\"0\\") Enter this amount on line 58080of your Form NL428. = ^". The form names no
label for any of the lines, so no step has a title. Line 1 is a printed maximum, the
`ca-nl/age_maximum` dataset claimed whole (core/credit_amount), a step toward line 7 and so without
a reference, as line 3 is in the line 4 part. Line 7 is the part's final step, a
core/subtract_not_below_zero over line 1 (`amount`) and line 6 (`less`), rounded half-up to the cent
by `ca-nl/cent_rounding`, and carries the reference "7". Neither input is ever blank, so the
subtraction has no blank rule. Line 7 and its kind already exist on the form export; this part adds
line 1 and the step.

The test composes the real federal parts the T1 taxable income form needs, the real
`worksheet_nl428_line_4.yaml`, `worksheet_nl428_line_6.yaml` and `worksheet_nl428_line_7.yaml`, and
types in only the salary. The header and the Worksheet NL428 form declaration (exporting line 7) are
made up here, because the shared scaffold owns them. Newfoundland and Labrador is not yet listed in
the registrations, so the service is built over the package list of `support.py`.

Figures (hand-computed with Decimal, not a CRA example). Line 1 is 7,064.00; line 4 is the salary
less the enhanced CPP deduction (2025) less 38,712.00, not below 0.00; line 6 is 15% of line 4.
- 30,000: line 6 = 0.00, so line 7 = 7,064.00.
- 50,000: line 6 = 1,623.45, so line 7 = 5,440.55.
- 100,000: line 6 = 9,032.10, so line 7 = 0.00 (the floor bites). 200,000: line 6 = 24,032.10, so
  line 7 = 0.00.
- Above 81,200 the deduction is a flat 1,074.00 (678.00 + 396.00), so line 4 = salary - 39,786.00.
  86,879.26: line 4 = 47,093.26, line 6 = 7,063.99 (7,063.989), line 7 = 0.01. 86,879.33: line 4 =
  47,093.33, line 6 = 7,064.00 (7,063.9995 rounds half-up), line 7 = 0.00 exactly, the floor not
  biting. 86,879.34: line 6 = 7,064.00 (7,064.001), line 7 = 0.00. 86,879.40: line 4 = 47,093.40,
  line 6 = 7,064.01 (7,064.01 exactly), so 7,064.00 - 7,064.01 = -0.01 floors to 0.00.
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
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import (
    BlankPassedOnLine,
    CreditAmountLine,
    SubtractedNotBelowZeroLine,
)
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART_4 = NL_PARTS / "worksheet_nl428_line_4.yaml"
PART_6 = NL_PARTS / "worksheet_nl428_line_6.yaml"
PART = NL_PARTS / "worksheet_nl428_line_7.yaml"
MAXIMUM = "ca-nl/age_maximum"
LINE_1 = "ca-nl/worksheet_nl428_age_amount_maximum_line_1"
LINE_6 = "ca-nl/worksheet_nl428_age_amount_line_6"
LINE_7 = "ca-nl/worksheet_nl428_age_amount_line_7"
ROUNDING = "ca-nl/cent_rounding"
FORM_NAME = "ca-nl/nl428_worksheet"
# The real federal parts the T1 taxable-income form needs, beside the salary and the lines.
FEDERAL_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
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
        - {LINE_7}
    capabilities: []
    """)


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
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield PART_4
    yield PART_6
    yield PART


def _parameters() -> YamlParameterSource:
    return YamlParameterSource(
        newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
    )


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
        _parameters(),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-NL"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(newfoundland_kinds().kind(identifier)).value)


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def salary_net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _line_6(salary: str) -> Decimal:
    line_4 = max(salary_net_income(D(salary)) - D("38712.00"), D(0))
    return _cent(line_4 * D("0.15"))


def _expected(salary: str) -> Decimal:
    """Line 7 recomputed from the salary: 7,064.00 less line 6, not below 0.00."""
    return max(_cent(D("7064.00") - _line_6(salary)), D(0))


def _rounding() -> Any:
    return _parameters().get(ROUNDING, 2025, ROUNDING_ONLY)


# salary, line 6, line 7.
CASES = [
    ("30000", "0.00", "7064.00"),
    ("50000", "1623.45", "5440.55"),
    ("100000", "9032.10", "0.00"),
    ("200000", "24032.10", "0.00"),
    # Just under the maximum: 7,064.00 - 7,063.99.
    ("86879.26", "7063.99", "0.01"),
    # Line 6 equals line 1 exactly: 0.00 without the floor biting.
    ("86879.33", "7064.00", "0.00"),
    ("86879.34", "7064.00", "0.00"),
    # Line 6 one cent above line 1: the difference is -0.01 and the floor gives 0.00.
    ("86879.40", "7064.01", "0.00"),
]


@pytest.mark.parametrize(("salary", "line_6", "expected"), CASES)
def test_line_7_is_line_1_minus_line_6_not_below_zero(
    tmp_path: Path, salary: str, line_6: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line_6(salary) == D(line_6)
    assert _expected(salary) == D(expected)
    assert _value(sheet, LINE_6) == D(line_6)
    line_7 = _value(sheet, LINE_7)
    assert line_7 == D(expected)
    assert str(line_7) == expected


def test_line_1_is_the_printed_maximum_at_every_salary(tmp_path: Path) -> None:
    for salary in ("30000", "50000", "200000"):
        assert _value(_sheet(tmp_path / salary, salary), LINE_1) == D("7064.00")


def test_line_7_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")

    assert not sheet.get(newfoundland_kinds().kind(LINE_7)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not any("left blank, taken as" in row.lower() for row in rows)


def test_line_1_traces_the_dataset_amount_with_the_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")
    kinds = newfoundland_kinds()
    dataset = _parameters().get(MAXIMUM, 2025, CREDIT)

    (line,) = [
        t for t in sheet.trace if isinstance(t, CreditAmountLine) and t.output == kinds.kind(LINE_1)
    ]
    assert line == CreditAmountLine(
        output=kinds.kind(LINE_1),
        basis=dataset.values,
        rounding=dataset.rounding,
        value=D("7064.00"),
    )


def test_the_positive_row_traces_the_subtraction_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")
    kinds = newfoundland_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(LINE_7)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_7),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("7064.00"),
        subtrahend=kinds.kind(LINE_6),
        subtrahend_amount=D("1623.45"),
        rounding=_rounding().rounding,
        result=D("5440.55"),
    )


@pytest.mark.parametrize(("salary", "line_6"), [("100000", "9032.10"), ("86879.40", "7064.01")])
def test_the_floored_row_proves_the_floor_with_a_negative_difference(
    tmp_path: Path, salary: str, line_6: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = newfoundland_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(LINE_7)
    ]
    assert line == SubtractedNotBelowZeroLine(
        output=kinds.kind(LINE_7),
        minuend=kinds.kind(LINE_1),
        minuend_amount=D("7064.00"),
        subtrahend=kinds.kind(LINE_6),
        subtrahend_amount=D(line_6),
        rounding=_rounding().rounding,
        result=D("0.00"),
    )
    assert line.minuend_amount - line.subtrahend_amount < 0


def test_the_boundary_row_is_zero_without_the_floor_biting(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "86879.33")
    kinds = newfoundland_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(LINE_7)
    ]
    assert line.minuend_amount == line.subtrahend_amount == D("7064.00")
    assert line.result == D("0.00")


def test_the_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "50000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [row for row in rows if "not below 0" in row and "5440.55" in row]
    assert "7064.00" in row
    assert "1623.45" in row
    assert "gives CA$5440.55" in row
    assert "rounded to the nearest cent" in row


def test_the_part_is_two_untitled_steps_and_only_line_7_carries_a_reference() -> None:
    steps = _steps()

    assert [step["name"] for step in steps] == [
        "core/credit_amount",
        "core/subtract_not_below_zero",
    ]
    assert all("title" not in step for step in steps)
    assert [step.get("reference") for step in steps] == [None, "7"]


def test_line_1_is_the_age_maximum_claimed_whole_with_no_reference() -> None:
    step = _steps()[0]

    assert "reference" not in step
    assert list(step) == ["name", "unit", "params", "produces"]
    assert step == {
        "name": "core/credit_amount",
        "unit": "ca/cad",
        "params": {"amount": MAXIMUM},
        "produces": {"output": LINE_1},
    }


def test_line_7_is_a_subtract_not_below_zero_step_with_no_blank_rule() -> None:
    step = _steps()[1]

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "7",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_6},
        "produces": {"output": LINE_7},
    }


def test_line_1_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_1)

    assert kind is nl_catalog.WORKSHEET_NL428_AGE_AMOUNT_MAXIMUM_LINE_1
    assert LINE_1.startswith("ca-nl/")
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


def test_the_line_1_kind_rejects_a_negative_amount() -> None:
    with pytest.raises(NegativeArtifactError):
        Artifact(newfoundland_kinds().kind(LINE_1), D("-0.01"))


def test_the_line_1_docstring_quotes_the_form_text() -> None:
    doc = squashed(docstring_of(LINE_1))

    assert "Worksheet NL428" in doc
    assert 'line 1 "Line 1: Maximum amount 7,064.00"' in doc
