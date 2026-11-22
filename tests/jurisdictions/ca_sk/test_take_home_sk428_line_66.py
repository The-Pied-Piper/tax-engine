"""SK428 (2025) line 66, line 63 plus line 64 plus line 65, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 66: Add lines 63 to 65. =". The form prints no title
for the line, so the step is untitled and is one core/sum over line 63 (the credits from line 57,
`ca-sk/sk428_credits_from_line_57_line_63`), the line 64 input (the dividend tax credit, optional,
blank for a salary-only filer and read as 0 by the step's own blank rule, which prints its own
"left blank, taken as 0" row) and the line 65 product (the minimum tax carryover, always computed,
so it needs no blank row). The output is `ca-sk/sk428_credits_subtotal_line_66`.

The test composes the T1 employment income form, the real Schedule 8 and T2204 parts, the real
line parts of `ca-sk/sk428_credits` that line 57 needs, the real `sk428_line_63.yaml`,
`sk428_line_64_input.yaml`, `sk428_line_65_inputs.yaml` and `sk428_line_65.yaml`, and the new
`sk428_line_66.yaml`, and types in only the salary (and, in some tests, lines 64 and 65). The two
form declarations are made up here: the credits form exports line 57 and `ca-sk/sk428` exports only
line 66.

Figures: line 66 is line 63 (line 57 as the engine produces it) plus a blank line 64 (0) plus a
line 65 of 0.00, re-derived here in `_derived` with Decimal (not a CRA example).
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
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import SumLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import form_parts
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_capabilities,
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_parameter_parsers,
    saskatchewan_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
LINE_PART = SK_PARTS / "sk428_line_66.yaml"
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
    "sk428_credits_line_43.yaml",
    "sk428_credits_line_44.yaml",
    "sk428_credits_line_46.yaml",
    "sk428_credits_line_47.yaml",
    "sk428_credits_line_48.yaml",
    "sk428_credits_line_49.yaml",
    "sk428_credits_line_50.yaml",
    "sk428_credits_line_51.yaml",
    "sk428_credits_line_53.yaml",
    "sk428_credits_line_54_input.yaml",
    "sk428_credits_line_55_input.yaml",
    "sk428_credits_line_54.yaml",
    "sk428_credits_line_55.yaml",
    "sk428_credits_line_56.yaml",
    "sk428_credits_line_57.yaml",
)
SK_LINE_PARTS = (
    "sk428_line_63.yaml",
    "sk428_line_64_input.yaml",
    "sk428_line_65_inputs.yaml",
    "sk428_line_65.yaml",
)
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_57 = "ca-sk/sk428_non_refundable_credits_line_57"
LINE_63 = "ca-sk/sk428_credits_from_line_57_line_63"
LINE_64 = "ca-sk/sk428_dividend_tax_credit_line_64"
LINE_65_AMOUNT = "ca-sk/sk428_minimum_tax_carryover_amount_line_65"
LINE_65 = "ca-sk/sk428_minimum_tax_carryover_line_65"
IDENTIFIER = "ca-sk/sk428_credits_subtotal_line_66"
ROUNDING = "ca-sk/cent_rounding"
BASIC_PERSONAL_AMOUNT = D("19491")

HEADER = dedent("""\
    jurisdiction: CA-SK
    version: 1
    valid_from_tax_year: 2025
    outputs: []
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
# The SK428 declaration, test-local: lines 63 to 66 are composed, so it exports only line 66.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 66: line 63 plus a blank line 64 (0) plus a line 65 of 0.00.
CASES = [
    ("20000", "2166.75"),
    ("70000", "2505.32"),
]


def _cent(value: Decimal) -> Decimal:
    return value.quantize(CENT, ROUND_HALF_UP)


def _derived(salary: Decimal, line_64: Decimal = ZERO, line_65_amount: Decimal = ZERO) -> Decimal:
    """Line 66 by hand: line 63 plus line 64 plus line 65. Line 63 is line 57, which is line 53
    (line 51 times 10.5%) with line 56 blank; line 51 is line 32 here (line 50 blank): the basic
    personal amount plus line 31, the CPP (4.95% above the $3,500 exemption, at most $3,356.10) and
    EI (1.64% to $65,700). Line 65 is 50% of its amount, half-up to the cent."""
    cpp = min(_cent(max(salary - D("3500"), D(0)) * D("0.0495")), D("3356.10"))
    ei = min(salary, D("65700")) * D("0.0164")
    line_32 = BASIC_PERSONAL_AMOUNT + _cent(cpp + ei)
    line_63 = _cent(line_32 * D("0.105"))
    line_65 = _cent(line_65_amount * D("0.5"))
    return _cent(line_63 + line_64 + line_65)


def _part_files() -> Iterator[Path]:
    yield from form_parts("schedule_8")
    yield from form_parts("t2204")
    yield from form_parts("t1_taxable_income", "t1_employment_income", "t1_medical_expenses")
    for name in CREDITS_PARTS:
        yield SK_PARTS / name
    for name in SK_LINE_PARTS:
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
            part.read_text(encoding="utf-8"),
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


def _sheet(
    tmp_path: Path,
    salary: str,
    line_64: str | None = None,
    line_65_amount: str | None = None,
) -> Worksheet:
    kinds = saskatchewan_kinds()
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_64 is not None:
        given.append(Artifact(kinds.kind(LINE_64), D(line_64)))
    if line_65_amount is not None:
        given.append(Artifact(kinds.kind(LINE_65_AMOUNT), D(line_65_amount)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_the_expected_figures_are_lines_63_to_65_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), CASES)
def test_line_66_is_line_63_when_lines_64_and_65_are_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_63) == D(expected)
    assert _line(sheet, LINE_65) == ZERO
    assert str(_line(sheet, IDENTIFIER)) == expected


@pytest.mark.parametrize(
    ("salary", "line_64", "line_65_amount", "expected"),
    [
        # Line 63 at 70,000 is 2,505.32; 2,505.32 + 100.00 + 500.00 (50% of 1,000.00).
        ("70000", "100.00", "1000.00", "3105.32"),
        ("70000", "100.00", None, "2605.32"),
        ("70000", None, "1000.00", "3005.32"),
    ],
)
def test_line_66_adds_all_three_lines(
    tmp_path: Path,
    salary: str,
    line_64: str | None,
    line_65_amount: str | None,
    expected: str,
) -> None:
    sheet = _sheet(tmp_path, salary, line_64, line_65_amount)

    assert _line(sheet, IDENTIFIER) == D(expected)
    assert _line(sheet, IDENTIFIER) == _derived(
        D(salary), D(line_64 or "0"), D(line_65_amount or "0")
    )


def test_the_step_traces_one_sum_line_over_the_three_parts_with_the_cent_rounding(
    tmp_path: Path,
) -> None:
    sheet = _sheet(tmp_path, "70000", "100.00", "1000.00")
    kinds = saskatchewan_kinds()
    rounding = YamlParameterSource(
        saskatchewan_packages().roots(), saskatchewan_parameter_parsers(), saskatchewan_units()
    ).get(ROUNDING, 2025, ROUNDING_ONLY)

    (line,) = [
        t for t in sheet.trace if isinstance(t, SumLine) and t.output is kinds.kind(IDENTIFIER)
    ]
    assert line == SumLine(
        output=kinds.kind(IDENTIFIER),
        parts=(
            (kinds.kind(LINE_63), D("2505.32")),
            (kinds.kind(LINE_64), D("100.00")),
            (kinds.kind(LINE_65), D("500.00")),
        ),
        rounding=rounding.rounding,
        total=D("3105.32"),
    )


def test_the_sum_row_reads_in_english_with_the_total(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "100.00", "1000.00")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    (row,) = [row for row in rows if "gives 3105.32" in row]
    assert "2505.32" in row
    assert "100.00" in row
    assert "500.00" in row
    assert "rounded to the nearest cent" in row


def test_the_sheet_prints_no_title_and_the_reference_of_line_66(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "66"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_63_to_65() -> None:
    part = _part()

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM_NAME}
    (step,) = part["capabilities"]
    assert list(step) == [
        "name",
        "reference",
        "unit",
        "params",
        "consumes",
        "blank",
        "produces",
    ]
    assert step == {
        "name": "core/sum",
        "reference": "66",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_63, LINE_64, LINE_65]},
        "blank": {LINE_64: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_66_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
    assert kind is vars(sk_catalog)["SK428_CREDITS_SUBTOTAL_LINE_66"]
