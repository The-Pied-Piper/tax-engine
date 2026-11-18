"""SK428 (2025) line 58, the Saskatchewan tax on taxable income from line 8, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 58: Saskatchewan tax on taxable income from line 8 ^"
and "Enter the amount from line 8 on line 58 and continue at line 9." Line 58 is a copy of line 8,
which sits on the other form `ca-sk/sk428_credits`, so its one step is a `core/record_total` over
that form's line 8 export, read as a record list (another form reads an export only as a record
list). There is one table, so there is no choice between two lines and no blank.

The test composes the real Saskatchewan salary part, the real Schedule 8, the T1 taxable income
parts, the real parts of lines 1, 3, 4, 5, 6, 7 and 8 of `ca-sk/sk428_credits`, and the new
`sk428_line_58.yaml`, and types in only the salary. The header and the two form declarations are
made up here: the credits form exports lines 1, 3, 4, 5, 6, 7 and 8, and `ca-sk/sk428` exports only
line 58.

Figures: line 58 is line 8 as the engine produces it, re-derived here in `_derived` with Decimal
(not a CRA example): 0.00 / 1,043.18 / 2,082.68 / 7,597.62 / 24,720.01 at salaries 0 / 10,000 /
20,000 / 70,000 / 200,000, and the column-edge figures of the line 8 test.
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
import tax_engine.jurisdictions.ca_sk
import tax_engine.jurisdictions.ca_sk.catalog as sk_catalog
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import RecordTotalLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative
from tests.manifest_support import inputs_without_form

D = Decimal
CENT = D("0.01")
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = SK_PARTS / "sk428_line_58.yaml"
CREDITS_PARTS = tuple(f"sk428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_8 = "ca-sk/sk428_tax_on_taxable_income_line_8"
IDENTIFIER = "ca-sk/sk428_tax_on_taxable_income_line_58"
TITLE = "Saskatchewan tax on taxable income from line 8"
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
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The credits form declaration, test-local: lines 1, 3, 4, 5, 6, 7 and 8 are composed.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - ca-sk/sk428_taxable_income_line_1
        - ca-sk/sk428_bracket_lower_bound_line_3
        - ca-sk/sk428_taxable_income_over_lower_bound_line_4
        - ca-sk/sk428_bracket_rate_line_5
        - ca-sk/sk428_tax_on_excess_line_6
        - ca-sk/sk428_bracket_tax_at_start_line_7
        - {LINE_8}
    capabilities: []
    """)
# The SK428 declaration, test-local: only line 58 is composed, so it exports only that.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 58: the same as line 8.
CASES = [
    ("0", "0.00"),
    ("10000", "1043.18"),
    ("20000", "2082.68"),
    ("70000", "7597.62"),
    ("200000", "24720.01"),
]
# Salaries whose taxable income sits on a column's edge (53,463.00 and 152,750.00), as in the
# line 8 test.
EDGES = [
    ("53967.67", "5613.61"),
    ("53967.68", "5613.62"),
    ("53967.69", "5613.62"),
    ("153823.99", "18024.49"),
    ("153824.00", "18024.50"),
    ("153824.01", "18024.49"),
]
ALL = [*CASES, *EDGES]


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in CREDITS_PARTS:
        yield SK_PARTS / name
    yield LINE_PART


def _service(tmp_path: Path) -> TaxComputationService:
    """The engine over a temporary Saskatchewan manifest of a test header, form declarations and
    the real part files, every other namespace being the Saskatchewan package list's own."""
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_credits_form.yaml").write_text(CREDITS_FORM, encoding="utf-8")
    (folder / "02_form.yaml").write_text(FORM, encoding="utf-8")
    for number, part in enumerate(_part_files(), start=3):
        (folder / f"{number:02d}_{part.name}").write_text(
            inputs_without_form(part)
            if part.name.endswith("_inputs.yaml") and part.is_relative_to(FEDERAL_FORMS)
            else part.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    roots = {**saskatchewan_packages().roots(), Namespace("ca-sk"): tmp_path}
    return TaxComputationService(
        YamlJurisdictionSource(roots, saskatchewan_kinds(), saskatchewan_units()),
        YamlParameterSource(
            saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
        ),
        saskatchewan_capabilities(),
    )


def _sheet(tmp_path: Path, form: str, salary: str) -> Worksheet:
    worksheets = _service(tmp_path).compute(
        JurisdictionCode("CA-SK"), 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )
    (sheet,) = worksheets[form]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _derived(salary: Decimal) -> Decimal:
    """Line 8 by the form's arithmetic, in Decimal: the tax on taxable income, where taxable
    income is the salary less the enhanced CPP deduction (2025)."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    line_1 = salary - enhanced - second
    if line_1 <= D("53463"):
        lower, rate, line_7 = D("0"), D("0.105"), D("0.00")
    elif line_1 <= D("152750"):
        lower, rate, line_7 = D("53463"), D("0.125"), D("5613.62")
    else:
        lower, rate, line_7 = D("152750"), D("0.145"), D("18024.49")
    return _cent(max(line_1 - lower, D(0)) * rate) + line_7


@pytest.mark.parametrize(("salary", "expected"), ALL)
def test_the_expected_figures_are_line_8_derived_independently(salary: str, expected: str) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), ALL)
def test_line_58_is_line_8_read_across_the_forms(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_8 = _line(_sheet(tmp_path, CREDITS_FORM_NAME, salary), LINE_8)
    line_58 = _line(_sheet(tmp_path / "other", FORM_NAME, salary), IDENTIFIER)

    assert line_8 == line_58 == D(expected)
    assert str(line_58) == expected


@pytest.mark.parametrize(("salary", "expected"), ALL)
def test_the_trace_totals_the_one_line_8_record(tmp_path: Path, salary: str, expected: str) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, salary)
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    assert line.amounts == (D(expected),)
    assert line.total == D(expected)


def test_the_trace_row_prints_line_8_and_the_total_and_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    row = EnglishTraceRenderer().render(line, sheet)
    assert row == "Line 8 (CA$7597.62) gives CA$7597.62."
    rows = EnglishTraceRenderer().render_all(sheet.trace, sheet)
    assert not any("left blank, taken as" in each.lower() for each in rows)


def test_the_sheet_prints_the_title_and_the_reference_of_line_58(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) == TITLE
    assert sheet.reference(label) == "58"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_titled_record_total_over_the_credits_form_line_8_export() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "title": TITLE,
        "reference": "58",
        "unit": "ca/cad",
        "consumes": {"records": "ca-sk/sk428_credits.sk428_tax_on_taxable_income_line_8"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_58_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_TAX_ON_TAXABLE_INCOME_LINE_58
