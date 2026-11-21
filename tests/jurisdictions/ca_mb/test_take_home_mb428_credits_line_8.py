"""MB428 (2025) line 8, the Manitoba tax on taxable income, real engine.

Form text (Form MB428, CRA 5007-C, read 2026-11-14,
https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5007-c/5007-c-25e.txt): "Line 8: Line 6
plus line 7 Manitoba tax on taxable income =". Line 6 is the tax on the excess over the column's
lower bound, rounded to the cent, and line 7 is the printed tax at the start of that column, so
line 8 is their sum. The sum is taken once, rounded half-up to the cent by `ca-mb/cent_rounding`,
which changes nothing here since both parts are already in cents. Lines 6 and 7 are never blank in
Manitoba (the last column has no upper boundary), so line 8 is never blank and the step has no
blank block.

Line 8 is one `core/sum` step over line 6 `ca-mb/mb428_tax_on_excess_line_6` and line 7
`ca-mb/mb428_bracket_tax_at_start_line_7`, output `ca-mb/mb428_tax_on_taxable_income_line_8`, in the
part `mb428_credits_line_8.yaml`.

The test composes the real parts: the Manitoba salary, the real Schedule 8, the T1 taxable-income
parts, and the real `mb428_credits_line_1.yaml`, `mb428_credits_line_3.yaml`,
`mb428_credits_line_4.yaml`, `mb428_credits_line_5.yaml`, `mb428_credits_line_6.yaml`,
`mb428_credits_line_7.yaml` and `mb428_credits_line_8.yaml`, and types in only the salary. The form
declaration is test-local, exporting lines 1, 3, 4, 5, 6, 7 and 8.

Figures (hand-computed in `_derived` below, not a CRA example): taxable income is the salary less
the enhanced CPP deduction, 9,935.00 / 198,926.00. Line 6 is 1,072.98 / 17,213.12 and line 7 is
0.00 / 11,833.50, so line 8 is 1,072.98 / 29,046.62. The boundary salaries are derived below as in
the line 6 and line 7 tests.
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
import tax_engine.jurisdictions.ca_mb.catalog as mb_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
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
from tests.manifest_support import T1_LINE_10100_INPUT

D = Decimal
CENT = D("0.01")
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = MB_PARTS / "mb428_credits_line_1.yaml"
LINE_3_PART = MB_PARTS / "mb428_credits_line_3.yaml"
LINE_4_PART = MB_PARTS / "mb428_credits_line_4.yaml"
LINE_5_PART = MB_PARTS / "mb428_credits_line_5.yaml"
LINE_6_PART = MB_PARTS / "mb428_credits_line_6.yaml"
LINE_7_PART = MB_PARTS / "mb428_credits_line_7.yaml"
LINE_8_PART = MB_PARTS / "mb428_credits_line_8.yaml"
FORM_NAME = "ca-mb/mb428_credits"
ROUNDING = "ca-mb/cent_rounding"
LINE_1 = "ca-mb/mb428_taxable_income_line_1"
LINE_3 = "ca-mb/mb428_bracket_lower_bound_line_3"
LINE_4 = "ca-mb/mb428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-mb/mb428_bracket_rate_line_5"
LINE_6 = "ca-mb/mb428_tax_on_excess_line_6"
LINE_7 = "ca-mb/mb428_bracket_tax_at_start_line_7"
LINE_8 = "ca-mb/mb428_tax_on_taxable_income_line_8"
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
# The MB428 declaration, test-local: lines 1, 3, 4, 5, 6, 7 and 8 are composed, so it exports those.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
        - {LINE_7}
        - {LINE_8}
    capabilities: []
    """)

# (salary, line 6, line 7, line 8): line 8 is line 6 plus line 7.
CASES = [
    ("10000", "1072.98", "0.00", "1072.98"),
    ("200000", "17213.12", "11833.50", "29046.62"),
]
# Salaries whose taxable income sits on a column's edge: line 1 is 47,000.00 or less in column 1,
# not more than 100,000.00 in column 2. One cent more is the next column.
EDGES = [
    ("47439.40", "0.00", "5076.00", "5076.00"),
    ("101074.00", "6757.50", "5076.00", "11833.50"),
]


def _part_files() -> Iterator[Path]:
    yield T1_LINE_10100_INPUT
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    yield LINE_1_PART
    yield LINE_3_PART
    yield LINE_4_PART
    yield LINE_5_PART
    yield LINE_6_PART
    yield LINE_7_PART
    yield LINE_8_PART


def _service(tmp_path: Path) -> TaxComputationService:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=2):
        (folder / f"{number:02d}_{part.name}").write_text(
            part.read_text(encoding="utf-8"),
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


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _taxable_income(salary: Decimal) -> Decimal:
    """The salary less the enhanced CPP deduction (2025): 1% of the earnings from $3,500 to
    $71,300, plus 4% of the earnings from $71,300 to $81,200."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    return salary - enhanced - second


def _column(line_1: Decimal) -> tuple[Decimal, Decimal]:
    """The lower bound (line 3) and the rate (line 5) of the column line 1 falls in."""
    if line_1 <= D("47000"):
        return D("0"), D("0.108")
    if line_1 <= D("100000"):
        return D("47000"), D("0.1275")
    return D("100000"), D("0.174")


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Line 6, line 7 and line 8 by the form's arithmetic, in Decimal."""
    line_1 = _taxable_income(salary)
    lower, rate = _column(line_1)
    line_6 = _cent(max(line_1 - lower, D(0)) * rate)
    line_7 = {D("0"): D("0.00"), D("47000"): D("5076.00"), D("100000"): D("11833.50")}[lower]
    return line_6, line_7, _cent(line_6 + line_7)


@pytest.mark.parametrize(("salary", "line_6", "line_7", "expected"), [*CASES, *EDGES])
def test_line_8_is_line_6_plus_line_7(
    tmp_path: Path, salary: str, line_6: str, line_7: str, expected: str
) -> None:
    # The table is the form's arithmetic in Decimal, checked before the engine is asked.
    assert _derived(D(salary)) == (D(line_6), D(line_7), D(expected))
    assert D(line_6) + D(line_7) == D(expected)
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_6)).value == D(line_6)
    assert sheet.get(_kind(LINE_7)).value == D(line_7)
    value = sheet.get(_kind(LINE_8)).value
    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize(("salary", "expected"), [("500000", "81246.62"), ("5000000", "864246.62")])
def test_line_8_has_no_blank_above_the_top_column(
    tmp_path: Path, salary: str, expected: str
) -> None:
    artifact = _sheet(tmp_path, salary).get(_kind(LINE_8))

    assert not artifact.is_blank
    assert artifact.value == D(expected)


def test_the_sum_is_traced_with_its_parts_in_the_order_they_are_wired(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    )
    assert [(kind, value) for kind, value in line.parts] == [
        (_kind(LINE_6), D("2847.71")),
        (_kind(LINE_7), D("5076.00")),
    ]
    assert line.total == D("7923.71")


def test_the_sum_reads_in_english_with_its_parts_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = (
        each for each in sheet.trace if isinstance(each, SumLine) and each.output is _kind(LINE_8)
    )
    text = EnglishTraceRenderer().render(line)

    assert "(2847.71) plus " in text
    assert "(5076.00)" in text
    assert text.endswith("gives 7923.71 (rounded to the nearest cent).")


def test_the_part_is_one_titled_sum_step_over_lines_6_and_7() -> None:
    part: Any = yaml.safe_load(LINE_8_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "params", "consumes", "produces"]
    assert step == {
        "name": "core/sum",
        "title": "Manitoba tax on taxable income",
        "reference": "8",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_6, LINE_7]},
        "produces": {"output": LINE_8},
    }


def test_line_8_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = manitoba_kinds()

    assert LINE_8 in kinds.identifiers()
    kind = kinds.kind(LINE_8)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is mb_catalog.MB428_TAX_ON_TAXABLE_INCOME_LINE_8
