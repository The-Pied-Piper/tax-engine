"""SK428 (2025) line 62, line 60 plus line 61, from the salary alone, real parts.

Form text (Form SK428, CRA 5008-c-25e): "Line 62: Line 60 plus line 61 =". The form prints no
title for the line and no floor, so the step is untitled and is one core/sum over line 60 and the
line 61 input; the sum is signed, so a negative line 60 stays negative unless line 61 lifts it.
Line 61, "Line 61 and line 61510: Saskatchewan tax on split income (complete Form T1206)", is an
optional input, blank for a salary-only filer: the blank is read as 0 and the step prints its own
"left blank, taken as 0" row.

The test composes the real Saskatchewan salary part, the real Schedule 8, the T1 taxable income
parts, the real parts of lines 1, 3, 4, 5, 6, 7 and 8 of `ca-sk/sk428_credits`, the real
`sk428_line_58.yaml`, `sk428_line_59_input.yaml`, `sk428_line_60.yaml` and
`sk428_line_61_input.yaml`, and the new `sk428_line_62.yaml`, and types in only the salary (and,
in some tests, line 59 and line 61). The header and the two form declarations are made up here: the
credits form exports lines 1, 3, 4, 5, 6, 7 and 8, and `ca-sk/sk428` exports only line 62.

Figures: line 60 is line 58 (line 8 as the engine produces it) less line 59, re-derived here in
`_derived` with Decimal (not a CRA example); line 62 is that plus line 61 (0 when blank):
0.00 / 7,597.62 / 24,720.01 at salaries 0 / 70,000 / 200,000. The column edges belong to the line 8 and line 58 tests.
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
ZERO = D(0)
SK_PARTS = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = SK_PARTS / "sk428_line_62.yaml"
LINE_58_PART = SK_PARTS / "sk428_line_58.yaml"
LINE_59_PART = SK_PARTS / "sk428_line_59_input.yaml"
LINE_60_PART = SK_PARTS / "sk428_line_60.yaml"
LINE_61_PART = SK_PARTS / "sk428_line_61_input.yaml"
CREDITS_PARTS = tuple(f"sk428_credits_line_{n}.yaml" for n in (1, 3, 4, 5, 6, 7, 8))
FORM_NAME = "ca-sk/sk428"
CREDITS_FORM_NAME = "ca-sk/sk428_credits"
LINE_58 = "ca-sk/sk428_tax_on_taxable_income_line_58"
LINE_59 = "ca-sk/sk428_farm_capital_gains_credit_line_59"
LINE_60 = "ca-sk/sk428_tax_line_60"
LINE_61 = "ca-sk/sk428_tax_on_split_income_line_61"
IDENTIFIER = "ca-sk/sk428_tax_line_62"
ROUNDING = "ca-sk/cent_rounding"
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
        - ca-sk/sk428_tax_on_taxable_income_line_8
    capabilities: []
    """)
# The SK428 declaration, test-local: lines 58 to 62 are composed, so it exports only line 62.
FORM = dedent(f"""\
    form:
      name: {FORM_NAME}
      required: true
      exports:
        - {IDENTIFIER}
    capabilities: []
    """)

# salary, line 62: line 60 (line 8 less a blank line 59) plus a blank line 61, read as 0.
ALL = [
    ("0", "0.00"),
    ("70000", "7597.62"),
    ("200000", "24720.01"),
]


def _part_files() -> Iterator[Path]:
    yield SK_PARTS / "salary.yaml"
    yield from sorted(FEDERAL_FORMS.rglob("schedule_8*.yaml"))
    for name in T1_PARTS:
        yield next(FEDERAL_FORMS.rglob(name))
    for name in CREDITS_PARTS:
        yield SK_PARTS / name
    yield LINE_58_PART
    yield LINE_59_PART
    yield LINE_60_PART
    yield LINE_61_PART
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


def _sheet(
    tmp_path: Path,
    salary: str,
    line_59: str | None = None,
    line_61: str | None = None,
) -> Worksheet:
    given = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    if line_59 is not None:
        given.append(Artifact(sk_catalog.SK428_FARM_CAPITAL_GAINS_CREDIT_LINE_59, D(line_59)))
    if line_61 is not None:
        given.append(Artifact(sk_catalog.SK428_TAX_ON_SPLIT_INCOME_LINE_61, D(line_61)))
    worksheets = _service(tmp_path).compute(JurisdictionCode("CA-SK"), 2025, *given)
    (sheet,) = worksheets[FORM_NAME]
    return sheet


def _line(sheet: Worksheet, identifier: str) -> Decimal:
    return D(sheet.get(saskatchewan_kinds().kind(identifier)).value)


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _line_60(salary: Decimal, line_59: Decimal = ZERO) -> Decimal:
    """Line 60 by the form's arithmetic, in Decimal: line 8 (the tax on taxable income, where
    taxable income is the salary less the enhanced CPP deduction, 2025) less line 59."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    line_1 = salary - enhanced - second
    if line_1 <= D("53463"):
        lower, rate, line_7 = D("0"), D("0.105"), D("0.00")
    elif line_1 <= D("152750"):
        lower, rate, line_7 = D("53463"), D("0.125"), D("5613.62")
    else:
        lower, rate, line_7 = D("152750"), D("0.145"), D("18024.49")
    line_58 = _cent(max(line_1 - lower, D(0)) * rate) + line_7
    return _cent(line_58 - line_59)


def _derived(salary: Decimal, line_59: Decimal = ZERO, line_61: Decimal = ZERO) -> Decimal:
    """Line 62 by the form's arithmetic, in Decimal: line 60 plus line 61."""
    return _cent(_line_60(salary, line_59) + line_61)


@pytest.mark.parametrize(("salary", "expected"), ALL)
def test_the_expected_figures_are_line_60_plus_a_blank_line_61_derived_independently(
    salary: str, expected: str
) -> None:
    assert _derived(D(salary)) == D(expected)


@pytest.mark.parametrize(("salary", "expected"), ALL)
def test_line_62_is_line_60_when_line_61_is_blank(
    tmp_path: Path, salary: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert _line(sheet, IDENTIFIER) == _line(sheet, LINE_60) == D(expected)
    assert str(_line(sheet, IDENTIFIER)) == expected


@pytest.mark.parametrize(
    ("salary", "line_61", "expected"),
    [
        ("70000", "100.00", "7697.62"),
        ("70000", "0.00", "7597.62"),
    ],
)
def test_line_62_adds_a_given_line_61_to_line_60(
    tmp_path: Path, salary: str, line_61: str, expected: str
) -> None:
    sheet = _sheet(tmp_path, salary, line_61=line_61)

    assert _line(sheet, IDENTIFIER) == D(expected) == _derived(D(salary), line_61=D(line_61))


def test_a_given_line_59_flows_through_line_60_into_line_62(tmp_path: Path) -> None:
    # Line 58 at 70,000 is 7,597.62; line 59 of 100.00 gives line 60 of 7,497.62.
    sheet = _sheet(tmp_path, "70000", "100.00")

    assert _line(sheet, LINE_60) == D("7497.62")
    assert _line(sheet, IDENTIFIER) == D("7497.62") == _derived(D("70000"), D("100.00"))


def test_a_given_line_59_and_line_61_are_both_taken(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", "100.00", "50.00")

    assert _line(sheet, IDENTIFIER) == D("7547.62")


def test_a_negative_line_60_plus_line_61_sums_signed_with_no_floor(tmp_path: Path) -> None:
    # Line 60 at 20,000 less a line 59 of 5,000.00 is -2,917.32; line 61 of 1,000.00 leaves
    # -1,917.32, and a blank line 61 leaves -2,917.32.
    assert _line(_sheet(tmp_path, "20000", "5000.00", "1000.00"), IDENTIFIER) == D("-1917.32")
    other = tmp_path / "blank"
    other.mkdir()
    assert _line(_sheet(other, "20000", "5000.00"), IDENTIFIER) == D("-2917.32")


def test_the_step_traces_one_sum_line_with_the_cent_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_61="100.00")
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
            (kinds.kind(LINE_60), D("7597.62")),
            (kinds.kind(LINE_61), D("100.00")),
        ),
        rounding=rounding.rounding,
        total=D("7697.62"),
    )


def test_the_sum_row_reads_in_english_with_the_rounding_named(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000", line_61="100.00")

    rows = EnglishTraceRenderer().render_all(sheet.trace)

    assert [row for row in rows if "gives 7697.62" in row] == [
        "Sk428 tax line 60 (7597.62) plus sk428 tax on split income line 61 (100.00) gives"
        " 7697.62 (rounded to the nearest cent)."
    ]


def test_the_sheet_prints_no_title_and_the_reference_of_line_62(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")
    label = saskatchewan_kinds().kind(IDENTIFIER).label

    assert sheet.title(label) is None
    assert sheet.reference(label) == "62"


def _part() -> dict[str, Any]:
    part = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_part_names_the_form_and_has_one_untitled_sum_step_over_lines_60_and_61() -> None:
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
        "reference": "62",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"parts": [LINE_60, LINE_61]},
        "blank": {LINE_61: "0"},
        "produces": {"output": IDENTIFIER},
    }


def test_line_62_is_a_registered_signed_decimal_amount_kind() -> None:
    kinds = saskatchewan_kinds()

    assert IDENTIFIER in kinds.identifiers()
    kind = kinds.kind(IDENTIFIER)
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind) is False
    assert kind is sk_catalog.SK428_TAX_LINE_62
