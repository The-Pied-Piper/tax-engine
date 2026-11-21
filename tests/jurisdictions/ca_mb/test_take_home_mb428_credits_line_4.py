"""MB428 (2025) line 4, the taxable income over the column's lower bound, real engine.

Form text (Form MB428, CRA 5007-C, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt): "Line 4:
Line 2 minus line 3 (can not be negative) = ^". Line 2 is a copy of line 1 ("Amount from line 1")
and has no step of its own. Line 3 is the printed lower bound of the column that line 1 falls in.
Line 4 is therefore line 1 less line 3, floored at zero, rounded to the cent.

Manitoba line 3 is never blank (one set of three columns, the last with no upper boundary), so
line 4 is never blank either: there is no blank case to test here.

Line 1 is `ca-mb/mb428_taxable_income_line_1`, its part `mb428_credits_line_1.yaml`, and line 3 is
`ca-mb/mb428_bracket_lower_bound_line_3`, its part `mb428_credits_line_3.yaml`; both are composed as
they are. Line 4 is `core/subtract_not_below_zero` with `amount` = line 1 and `less` = line 3,
output `ca-mb/mb428_taxable_income_over_lower_bound_line_4`, rounded by `ca-mb/cent_rounding`, in
the part `mb428_credits_line_4.yaml`.

The real parts composed: the Manitoba salary, the real Schedule 8, the T1 taxable-income parts,
lines 1, 3 and 4. The form declaration is test-local, exporting lines 1, 3 and 4.

Figures, hand-computed here from the salary less the enhanced CPP deduction (not a CRA example):
salary 10,000 gives line 1 of 9,935.00 and line 3 of 0.00, so line 4 is 9,935.00; 70,000 gives
69,335.00 less 47,000.00, so 22,335.00; 200,000 gives 198,926.00 less 100,000.00, so 98,926.00.
The edges sit exactly on the column bounds of line 3: a salary of 47,439.40 gives line 1 of
47,000.01 (line 4 0.01) and 101,074.00 gives 100,000.00 (line 4 53,000.00).
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SubtractedNotBelowZeroLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
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
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = MB_PARTS / "mb428_credits_line_1.yaml"
LINE_3_PART = MB_PARTS / "mb428_credits_line_3.yaml"
LINE_4_PART = MB_PARTS / "mb428_credits_line_4.yaml"
FORM_NAME = "ca-mb/mb428_credits"
LINE_1 = "ca-mb/mb428_taxable_income_line_1"
LINE_3 = "ca-mb/mb428_bracket_lower_bound_line_3"
LINE_4 = "ca-mb/mb428_taxable_income_over_lower_bound_line_4"
ROUNDING = "ca-mb/cent_rounding"
# The real federal parts the T1 taxable-income form needs, beside the salary and line 1.
T1_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_employment_income.yaml",
    "t1_employment_income_line_10100.yaml",
    "t1_employment_income_line_10400.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The MB428 declaration, test-local: lines 1, 3 and 4 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
    capabilities: []
    """)

CASES = [
    ("10000", "9935.00", "0.00", "9935.00"),
    ("200000", "198926.00", "100000.00", "98926.00"),
]
# Salaries whose taxable income sits on a column's edge (line 3 is 47,000.00 or 100,000.00 at
# the bounds). One cent more is the next column, and line 4 is one cent or the full column.
EDGES = [
    ("47439.40", "47000.01", "47000.00", "0.01"),
    ("101074.00", "100000.00", "47000.00", "53000.00"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_1_PART
    yield LINE_3_PART
    yield LINE_4_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
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


def _kind(identifier: str) -> AmountKind:
    kind = manitoba_kinds().kind(identifier)
    assert isinstance(kind, AmountKind)
    return kind


def _rounding() -> Any:
    return YamlParameterSource(
        manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


@pytest.mark.parametrize(("salary", "line_1", "line_3", "expected"), CASES)
def test_line_4_is_line_1_less_line_3_for_the_salary(
    tmp_path: Path, salary: str, line_1: str, line_3: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "line_1", "line_3", "expected"), EDGES)
def test_line_4_is_line_1_less_line_3_at_the_column_edges(
    tmp_path: Path, salary: str, line_1: str, line_3: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_4)).value

    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 3 is the top column's 100,000.00 and is never blank, so line 4 is not either.
        ("200000", "98926.00"),
        ("500000", "398926.00"),
    ],
)
def test_line_4_is_not_blank_above_the_top_column(
    tmp_path: Path, salary: str, expected: str
) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_4))

    assert not artifact.is_blank
    assert artifact.value == D(expected)


def test_the_trace_records_the_subtraction_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [t for t in sheet.trace if isinstance(t, SubtractedNotBelowZeroLine)]
    assert line == SubtractedNotBelowZeroLine(
        output=_kind(LINE_4),
        minuend=_kind(LINE_1),
        minuend_amount=D("69335.00"),
        subtrahend=_kind(LINE_3),
        subtrahend_amount=D("47000.00"),
        rounding=_rounding().rounding,
        result=D("22335.00"),
    )


def test_the_part_is_one_untitled_subtract_not_below_zero_step_over_lines_1_and_3() -> None:
    part: Any = yaml.safe_load(LINE_4_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/subtract_not_below_zero",
        "reference": "4",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"amount": LINE_1, "less": LINE_3},
        "produces": {"output": LINE_4},
    }


def test_line_4_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert LINE_4 in kinds.identifiers()
    kind = kinds.kind(LINE_4)
    assert kind is mb_catalog.MB428_TAXABLE_INCOME_OVER_LOWER_BOUND_LINE_4
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
