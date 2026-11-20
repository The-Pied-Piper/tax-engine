"""Worksheet MB428 (2025) line 6, line 4 divided by line 5, from the real parts.

Form text (Worksheet MB428, CRA 5007-D, 2025, from the ticket):
"Line 6: Line 4 divided by line 5 = ^".
The form names no label for the line, so the step has no title. Line 6 is one core/divide step over
line 4 (`dividend`) and line 5 (`divisor`), rounded by `ca-mb/exact_rounding` (`rounding: none`):
the form prints no rounding for the line and line 4 over 200,000.00 always terminates, so the ratio
is exact. The step has no unit, as the ratio is neither dollars nor a percent. The kind
`ca-mb/worksheet_mb428_line_6` is non-negative.

The test composes the real Manitoba salary part, the real federal parts the T1 taxable income form
needs, the real line 2, 3, 4 and 5 parts and the new `worksheet_mb428_line_6.yaml`, and types in
only the salary. The header and the Worksheet MB428 form declaration are made up here, because the
shared scaffold owns them.

Figures: line 4 is 0.00 at $10,000 and $200,000 (the line 4 test pins this), so
line 6 is 0 there. A salary of $251,074 gives net income 251,074 - 678.00 - 396.00 = 250,000.00,
the ticket's $250,000 net income, so line 4 is 50,000.00 and line 6 is 50,000.00 / 200,000.00 =
0.25. The $300,000 case is this test's own addition: net income 298,926.00, line 4 98,926.00 and
line 6 98,926.00 / 200,000.00 = 0.49463, more than two decimals, so it shows nothing is rounded to
the cent.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca
import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BlankPassedOnLine, QuotientLine
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
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
PART = MB_PARTS / "worksheet_mb428_line_6.yaml"
KIND = "ca-mb/worksheet_mb428_line_6"
LINE_2 = "ca-mb/worksheet_mb428_line_2"
LINE_3 = "ca-mb/worksheet_mb428_basic_personal_amount_line_3"
LINE_4 = "ca-mb/worksheet_mb428_line_4"
LINE_5 = "ca-mb/worksheet_mb428_basic_personal_amount_line_5"
ROUNDING = "ca-mb/exact_rounding"
FORM_NAME = "ca-mb/worksheet_mb428"
# The real federal parts the T1 taxable-income form needs, beside the salary and lines 2 to 5.
FEDERAL_PARTS = (
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_10100.yaml",
    "t1_taxable_income_line_10400.yaml",
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
    jurisdiction: CA-MB
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
FORM = dedent("""\
    form:
      name: ca-mb/worksheet_mb428
      required: true
      exports:
        - ca-mb/worksheet_mb428_line_2
        - ca-mb/worksheet_mb428_basic_personal_amount_line_3
        - ca-mb/worksheet_mb428_line_4
        - ca-mb/worksheet_mb428_basic_personal_amount_line_5
        - ca-mb/worksheet_mb428_line_6
    capabilities: []
    """)

# salary, line 4, line 5, line 6. The first four are the ticket's salaries: line 4 is the floor,
# 0.00, so line 6 is 0.
ZERO = [
    ("10000", "0.00", "200000.00", "0"),
    ("200000", "0.00", "200000.00", "0"),
]
# salary, net income (line 2), line 4, line 6: the ticket's $250,000 net income = ratio 0.25, and
# this test's own $300,000 addition (not in the ticket), whose ratio has five decimals.
POSITIVE = [
    ("251074", "250000.00", "50000.00", "0.25"),
    ("300000", "298926.00", "98926.00", "0.49463"),
]


def _part_files() -> Iterator[Path]:
    yield MB_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in FEDERAL_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield MB_PARTS / "worksheet_mb428_line_2.yaml"
    yield MB_PARTS / "worksheet_mb428_line_3.yaml"
    yield MB_PARTS / "worksheet_mb428_line_4.yaml"
    yield MB_PARTS / "worksheet_mb428_line_5.yaml"
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


def _rounding() -> Any:
    return YamlParameterSource(
        manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)


def _line_6(sheet: Worksheet) -> Decimal:
    return D(sheet.get(manitoba_kinds().kind(KIND)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _net_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _step() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert isinstance(step, dict)
    return step


@pytest.mark.parametrize(("salary", "line_4", "line_5", "expected"), ZERO)
def test_line_6_is_zero_while_line_4_is_zero_at_each_ticket_salary(
    tmp_path: Path, salary: str, line_4: str, line_5: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    assert sheet.get(kinds.kind(LINE_4)).value == D(line_4)
    assert sheet.get(kinds.kind(LINE_5)).value == D(line_5)
    assert _line_6(sheet) == D(expected)
    assert not _line_6(sheet).is_signed()


@pytest.mark.parametrize(("salary", "line_2", "line_4", "expected"), POSITIVE)
def test_line_6_is_line_4_over_line_5_exactly_above_the_threshold(
    tmp_path: Path, salary: str, line_2: str, line_4: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    kinds = manitoba_kinds()

    # Net income is recomputed from the salary; line 4 is it less 200,000.00.
    assert _net_income(D(salary)) == D(line_2)
    assert sheet.get(kinds.kind(LINE_2)).value == D(line_2)
    assert sheet.get(kinds.kind(LINE_4)).value == D(line_4)
    assert sheet.get(kinds.kind(LINE_5)).value == D("200000.00")
    assert _line_6(sheet) == D(expected)
    # The quotient is exact, as a Fraction would have it.
    assert _line_6(sheet) == D(line_4) / D("200000.00")


def test_line_6_is_not_rounded_to_the_cent(tmp_path: Path) -> None:
    value = _line_6(_sheet(tmp_path, "300000"))

    assert value == D("0.49463")
    assert value != _cent(value)
    exponent = value.as_tuple().exponent
    assert isinstance(exponent, int)
    assert exponent < -2


def test_line_6_is_never_blank_and_traces_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    assert not sheet.get(manitoba_kinds().kind(KIND)).is_blank
    assert not [t for t in sheet.trace if isinstance(t, BlankPassedOnLine)]


def test_the_step_traces_one_quotient_line_with_no_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")
    kinds = manitoba_kinds()

    assert _rounding().rounding == NO_ROUNDING
    (line,) = [t for t in sheet.trace if isinstance(t, QuotientLine)]
    assert line == QuotientLine(
        output=kinds.kind(KIND),
        dividend=kinds.kind(LINE_4),
        dividend_amount=D("98926.00"),
        divisor=kinds.kind(LINE_5),
        divisor_amount=D("200000.00"),
        rounding=NO_ROUNDING,
        result=D("0.49463"),
    )


def test_the_zero_row_traces_the_quotient_of_zero(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    kinds = manitoba_kinds()

    (line,) = [t for t in sheet.trace if isinstance(t, QuotientLine)]
    assert line == QuotientLine(
        output=kinds.kind(KIND),
        dividend=kinds.kind(LINE_4),
        dividend_amount=D("0.00"),
        divisor=kinds.kind(LINE_5),
        divisor_amount=D("200000.00"),
        rounding=NO_ROUNDING,
        result=D("0"),
    )


def test_the_quotient_row_reads_in_english_as_not_rounded(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")

    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    (row,) = [row for row in rows if " divided by " in row]
    assert "98926.00" in row
    assert "200000.00" in row
    assert "gives" in row
    assert "0.49463" in row
    assert row.endswith("(not rounded).")


def test_the_part_is_one_untitled_divide_step_with_no_unit() -> None:
    step = _step()

    assert list(step) == ["name", "reference", "params", "consumes", "produces"]
    assert "title" not in step
    assert "unit" not in step
    assert step == {
        "name": "core/divide",
        "reference": "6",
        "params": {"rounding": ROUNDING},
        "consumes": {"dividend": LINE_4, "divisor": LINE_5},
        "produces": {"output": KIND},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = manitoba_kinds().kind(KIND)

    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
