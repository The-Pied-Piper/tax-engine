"""SK428 (2025) line 63, the Saskatchewan non-refundable tax credits from line 57, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 63: Saskatchewan non-refundable tax credits from line
57". Line 57 ("Line 57 and line 61500: Line 53 plus line 56 Enter this amount on line 63.") sits on
the other form `ca-sk/sk428_credits`, so line 63 is one `core/record_total` step over that form's
line 57 export, read as a record list (another form reads an export only as a record list). There
is one record, so there is no choice between two lines and no blank.

The test composes the real Saskatchewan salary part, the real Schedule 8 and T2204 parts, the real
line parts of `ca-sk/sk428_credits` that line 57 needs (lines 9, 20, 22, 24, 31, 32, 33 with
`sk428_line_33_inputs.yaml`, 35, 38, 42, 50 input, 51, 53, 56 input and 57) and the new
`sk428_line_63.yaml`, and types in only the salary. The two form declarations are made up here: the
credits form exports line 57 and `ca-sk/sk428` exports only line 63.

Figures: line 63 is line 57 as the engine produces it, re-derived here in `_derived` with Decimal
(not a CRA example): line 57 is line 53 (line 51 times 10.5%, half-up to the cent) plus the blank
line 56 read as 0.
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
LINE_PART = SK_PARTS / "sk428_line_63.yaml"
CREDITS_PARTS = (
    "sk428_credits_line_9.yaml",
    "sk428_credits_line_20.yaml",
    "sk428_credits_line_22.yaml",
    "sk428_credits_line_24.yaml",
    "sk428_line_33_inputs.yaml",
    "sk428_credits_line_31.yaml",
    "sk428_credits_line_32.yaml",
    "sk428_credits_line_33.yaml",
    "sk428_credits_line_35.yaml",
    "sk428_credits_line_38.yaml",
    "sk428_credits_line_42.yaml",
    "sk428_credits_line_50_input.yaml",
    "sk428_credits_line_51.yaml",
    "sk428_credits_line_53.yaml",
    "sk428_credits_line_56_input.yaml",
    "sk428_credits_line_57.yaml",
)
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_57 = "ca-sk/sk428_non_refundable_credits_line_57"
IDENTIFIER = "ca-sk/sk428_credits_from_line_57_line_63"
TITLE = "Saskatchewan non-refundable tax credits from line 57"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The credits form declaration, test-local: only line 57 is exported.
CREDITS_FORM = dedent(f"""\
    form:
      name: {CREDITS_FORM_NAME}
      required: true
      exports:
        - {LINE_57}
    capabilities: []
    """)
# The SK428 declaration, test-local: only line 63 is composed, so it exports only that.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 63: the same as line 57 (line 53, line 56 being blank).
CASES = [
    ("20000", "2166.75"),
    ("70000", "2505.32"),
]


def _cent(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def _derived(salary: Decimal) -> Decimal:
    """Line 57 by hand: line 53 plus line 56 (blank, 0). Line 53 is line 51 times 10.5%; line 51 is
    line 42, which is line 32 here (line 50 blank): the basic personal amount plus line 31, the
    CPP (4.95% above the $3,500 exemption, at most $3,356.10) and EI (1.64% to $65,700)."""
    cpp = min(_cent(max(salary - D("3500"), D(0)) * D("0.0495")), D("3356.10"))
    ei = min(salary, D("65700")) * D("0.0164")
    line_32 = BASIC_PERSONAL_AMOUNT + _cent(cpp + ei)
    line_53 = _cent(line_32 * D("0.105"))
    return line_53 + D(0)


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    yield from sorted(FEDERAL_FORMS.rglob("t2204*.yaml"))
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


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_expected_figures_are_line_57_derived_independently(salary: str, expected: str) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_63_is_line_57_read_across_the_forms(
    tmp_path: Path, salary: str, expected: str
) -> None:
    line_57 = _line(_sheet(tmp_path, CREDITS_FORM_NAME, salary), LINE_57)
    line_63 = _line(_sheet(tmp_path / "other", FORM_NAME, salary), IDENTIFIER)

    assert line_57 == line_63 == D(expected)
    assert str(line_63) == expected


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_trace_totals_the_one_line_57_record(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, salary)
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    assert line.amounts == (D(expected),)
    assert line.total == D(expected)


def test_the_trace_row_prints_line_57_and_the_total_and_no_blank_row(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    kind = saskatchewan_kinds().kind(IDENTIFIER)

    (line,) = [t for t in sheet.trace if isinstance(t, RecordTotalLine) and t.output == kind]
    row = EnglishTraceRenderer().render(line, sheet)
    assert row == "Line 57 (CA$2505.32) gives CA$2505.32."
    assert "left blank, taken as" not in row.lower()


def test_the_sheet_prints_the_title_and_the_reference_of_line_63(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, FORM_NAME, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) == TITLE
    assert sheet.reference(label) == "63"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_is_one_titled_record_total_over_the_credits_form_line_57_export() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "unit", "consumes", "produces"]
    assert step == {
        "name": "core/record_total",
        "title": TITLE,
        "reference": "63",
        "unit": "ca/cad",
        "consumes": {"records": "ca-sk/sk428_credits.sk428_non_refundable_credits_line_57"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_63_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is sk_catalog.SK428_CREDITS_FROM_LINE_57_LINE_63
