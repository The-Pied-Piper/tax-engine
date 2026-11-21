"""Schedule MB428-A (2025) line 12, line 10 minus line 11 (not below 0), from the salary alone.

Form text (Schedule MB428-A, CRA 5007-A): "Line 12: Line 10 minus line 11 (if negative, enter "0")
Enter this amount on line 61470 of your Form MB428. Family tax benefit = ^". The form names no
label for the line, so the step has no title. Line 12 is one core/subtract_not_below_zero step over
line 10 (`amount`) and line 11 (`less`), rounded half-up to the cent by `ca-mb/cent_rounding`. The
kind `ca-mb/mb428_a_family_tax_benefit_line_12` is the form's existing non-negative amount.

The test composes the real Manitoba salary part, the real federal parts the T1 taxable income form
needs (the same as the line 11 product test), the real `mb428_a_line_1.yaml`,
`mb428_a_line_10.yaml`, `mb428_a_line_11.yaml` and `mb428_a_line_11_product.yaml` parts and the new
`mb428_a_line_12.yaml`, and types in only the salary. The Schedule MB428-A form declaration is made
up here, exporting lines 10, 11 and 12.

The figures are hand-computed from the printed form (not a CRA example): line 10 is 2,065.00 at
every salary; line 11 is 894.15, 1,785.15, 6,240.15 and 17,903.34 at the four salaries, so line 12
is 1,170.85, 279.85, then the floor, 0.00, twice. The two salaries near the cut-off are this test's
own addition: net income is the salary less the enhanced CPP deduction, 1% of (salary - 3,500).
At 23,140 it is 22,943.60, line 11 is 2,064.92 and line 12 is 0.08; at 23,141 it is 22,944.59, line
11 is 2,065.01 and line 12 is the floor.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
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
from tests.manifest_support import inputs_without_form

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
PART = MB_PARTS / "mb428_a_line_12.yaml"
IDENTIFIER = "ca-mb/mb428_a_family_tax_benefit_line_12"
LINE_10 = "ca-mb/mb428_a_line_10"
LINE_11 = "ca-mb/mb428_a_line_11"
ROUNDING = "ca-mb/cent_rounding"
FORM_NAME = "ca-mb/mb428_a"
# The real Manitoba parts under line 12, in dependency order.
LINE_PARTS = (
    "mb428_a_line_1.yaml",
    "mb428_a_line_10.yaml",
    "mb428_a_line_11.yaml",
    "mb428_a_line_11_product.yaml",
)
# The real federal parts the T1 taxable-income form needs, beside the salary and line 11.
FEDERAL_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/mb428_a
      required: true
      exports:
        - ca-mb/mb428_a_line_10
        - ca-mb/mb428_a_line_11
        - ca-mb/mb428_a_family_tax_benefit_line_12
    capabilities: []
    """)

# salary, line 10, line 11, line 12. The first is the ticket's table; the second sits just inside
# the cut-off, where line 11 passes line 10 (2,065.00). The zero floor has its own test at 70000.
CASES = [
    ("10000", "2065.00", "894.15", "1170.85"),
    ("23140", "2065.00", "2064.92", "0.08"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from form_parts("schedule_8")
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in LINE_PARTS:
        yield MB_PARTS / name
    yield PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Manitoba manifest of a test header, a form declaration and the
    real part files, every other namespace being the Manitoba package list's own."""
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
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, manitoba_kinds(), manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )


def _sheet(tmp_path: Path, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-MB"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _value(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(identifier)).value)


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize(("salary", "line_10", "line_11", "expected"), CASES)
def test_line_12_is_line_10_minus_line_11_not_below_zero(
    tmp_path: Path, salary: str, line_10: str, line_11: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _value(sheet, LINE_10) == D(line_10)
    assert _value(sheet, LINE_11) == D(line_11)
    assert _value(sheet, IDENTIFIER) == D(expected)


def test_line_12_is_zero_at_70000_because_line_11_exceeds_line_10(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line_12 = _value(sheet, IDENTIFIER)
    assert _value(sheet, LINE_11) > _value(sheet, LINE_10)
    assert line_12 == D("0.00")
    # The floor is the cent zero of the rounding dataset: printed 0.00, never -0.00.
    assert str(line_12) == "0.00"
    assert line_12.as_tuple().exponent == -2
    assert not line_12.is_signed()


def test_the_part_is_one_untitled_subtract_not_below_zero_step() -> None:
    step = _step()

    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "12",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_10, "less": LINE_11},
        "produces": {"output": IDENTIFIER},
    }


def test_the_kind_is_the_registered_non_negative_decimal_amount() -> None:
    kind = manitoba_kinds().kind(IDENTIFIER)

    assert kind is mb_catalog.MB428_A_FAMILY_TAX_BENEFIT_LINE_12
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)


@pytest.mark.parametrize(("salary", "line_10", "line_11"), [("20000", "2065.00", "1785.15")])
def test_the_trace_has_a_row_for_line_12(
    tmp_path: Path, salary: str, line_10: str, line_11: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    (line,) = [
        t
        for t in sheet.trace
        if isinstance(t, SubtractedNotBelowZeroLine) and t.output == kinds.kind(IDENTIFIER)
    ]
    assert line.minuend == kinds.kind(LINE_10)
    assert line.minuend_amount == D(line_10)
    assert line.subtrahend == kinds.kind(LINE_11)
    assert line.subtrahend_amount == D(line_11)
    assert line.result == D("279.85")
