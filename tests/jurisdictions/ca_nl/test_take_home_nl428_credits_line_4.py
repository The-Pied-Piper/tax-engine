"""NL428 (2025) line 4, line 2 minus line 3 (cannot be negative), real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): each of the four columns of lines 2 to 8 prints
"Line 2: Amount from line 1" and "Line 4: Line 2 minus line 3 (cannot be negative) =". Line 2 is a
copy of line 1 (the T1 taxable income) and has no step; line 3 is the printed lower bound of the
column line 1 falls in (0.00, 44,192.00, 88,382.00 or 157,792.00), blank above 220,910, where lines
9 to 15 apply. The form prints no label for line 4, so the step has no title.

Line 4 is one `core/subtract_not_below_zero` step with `amount` = line 1 and `less` = line 3,
rounded by `ca-nl/cent_rounding`, output `ca-nl/nl428_taxable_income_over_lower_bound_line_4`, in
the part `nl428_credits_line_4.yaml`. A blank line 3 is passed on, so line 4 is blank above 220,910.

The real parts composed: the real Schedule 8, the T1 taxable-income parts, lines 1 and 3 and
`nl428_credits_line_4.yaml`. The header, the salary input and the form declaration are test-local
(Newfoundland and Labrador has no salary part), the form exporting lines 1, 3 and 4.

Figures, hand computed (not a CRA example): taxable income is the salary less the enhanced CPP
deduction, 19,835.00 / 69,335.00 / 198,926.00 for salaries of 20,000 / 70,000 / 200,000, line 3 is
0.00 / 44,192.00 / 157,792.00, so line 4 is 19,835.00 / 25,143.00 / 41,134.00. The boundary salaries
are those of the line 3 test: one cent either side of each column's lower bound.
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
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import NL428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
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
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_3 = "ca-nl/nl428_bracket_lower_bound_line_3"
LINE_4 = "ca-nl/nl428_taxable_income_over_lower_bound_line_4"
ROUNDING = "ca-nl/cent_rounding"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_3_PART = NL_PARTS / "nl428_credits_line_3.yaml"
LINE_PART = NL_PARTS / "nl428_credits_line_4.yaml"
T1_PARTS = (
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
        required: true
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The NL428 declaration, test-local: lines 1, 3 and 4 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
    """)
LINE_1_PART = NL_PARTS / "nl428_credits_line_1.yaml"


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml")):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_3_PART.name, LINE_3_PART.read_text(encoding="utf-8")
    yield LINE_PART.name, LINE_PART.read_text(encoding="utf-8")


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM_TEXT, encoding="utf-8")
    for number, (name, text) in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{name}").write_text(text, encoding="utf-8")
    roots = {**newfoundland_packages().roots(), Namespace("ca-nl"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, newfoundland_kinds(), newfoundland_units()),
        YamlParameterSource(
            newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
        ),
        newfoundland_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(CODE, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))
    (sheet,) = worksheets[FORM]
    return sheet


def _kind(identifier: str) -> AmountKind:
    kind = newfoundland_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        newfoundland_packages().roots(), newfoundland_parameter_parsers(), newfoundland_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


# (salary, line 1, line 3, line 4)
CASES = [
    ("20000", "19835.00", "0.00", "19835.00"),
    ("70000", "69335.00", "44192.00", "25143.00"),
    ("200000", "198926.00", "157792.00", "41134.00"),
]
EDGES = [
    ("44603.03", "44192.00", "0.00", "44192.00"),
    ("44603.04", "44192.01", "44192.00", "0.01"),
    ("89456.00", "88382.00", "44192.00", "44190.00"),
    ("89456.01", "88382.01", "88382.00", "0.01"),
    ("158866.00", "157792.00", "88382.00", "69410.00"),
    ("158866.01", "157792.01", "157792.00", "0.01"),
    ("221984.00", "220910.00", "157792.00", "63118.00"),
]


@pytest.mark.parametrize(("salary", "line_1", "line_3", "expected"), [*CASES, *EDGES])
def test_line_4_is_line_1_less_line_3_for_the_salary(
    tmp_path: Path, salary: str, line_1: str, line_3: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", ["221984.01", "300000"])
def test_line_4_is_blank_when_line_3_is_blank_above_220910(tmp_path: Path, salary: str) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_3)).is_blank
    assert sheet.get(_kind(LINE_4)).is_blank


def test_the_trace_records_the_subtraction_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=_kind(LINE_4),
        minuend=_kind(LINE_1),
        minuend_amount=D("69335.00"),
        subtrahend=_kind(LINE_3),
        subtrahend_amount=D("44192.00"),
        rounding=_rounding().rounding,
        result=D("25143.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_over_lines_1_and_3() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_3},
        "blank": {"less": "pass_on"},
        "produces": {"output": LINE_4},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_4)

    assert kind is NL428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
