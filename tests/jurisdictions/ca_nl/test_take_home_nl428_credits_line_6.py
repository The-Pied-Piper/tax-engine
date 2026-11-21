"""NL428 (2025) line 6, line 4 multiplied by the line 5 rate, real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): each of the four columns of lines 2 to 8 prints
"Line 6: Line 4 multiplied by the percentage from line 5 =". Line 6 is line 4 times the printed
rate of the column (8.7%, 14.5%, 15.8% or 17.8%), rounded half-up to the cent by
`ca-nl/cent_rounding`: the form states no rounding rule. The form prints no label for line 6, so
the step has no title. Above 220,910 lines 4 and 5 are blank (lines 9 to 15 apply), so line 6 is
blank too.

Line 6 is one `core/multiply_by_rate` step with base `ca-nl/nl428_taxable_income_over_lower_bound_
line_4` and rate `ca-nl/nl428_bracket_rate_line_5`, output `ca-nl/nl428_tax_on_excess_line_6`, in
the part `nl428_credits_line_6.yaml`; a blank base or rate is passed on.

The real parts composed: the real Schedule 8, the T1 taxable-income parts, lines 1, 3, 4, 5 and 6.
The header, the salary input and the form declaration are test-local (Newfoundland and Labrador has
no salary part), the form exporting lines 1, 3, 4, 5 and 6.

Figures, re-derived in `_derived` below with Decimal (not a CRA example): taxable income is the
salary less the enhanced CPP deduction, 69,335.00 for a salary of 70,000; line 4 is that less the
column's lower bound (44,192.00), so 25,143.00; line 6 is line 4 at 14.5%: 3,645.74. The rounding
salary (44,603.06) is one of the line 4 and line 5 tests.
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
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import MultipliedByRateLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import NL428_TAX_ON_EXCESS_LINE_6
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
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
ROUNDING = "ca-nl/cent_rounding"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_3 = "ca-nl/nl428_bracket_lower_bound_line_3"
LINE_4 = "ca-nl/nl428_taxable_income_over_lower_bound_line_4"
LINE_5 = "ca-nl/nl428_bracket_rate_line_5"
LINE_6 = "ca-nl/nl428_tax_on_excess_line_6"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_1_PART = NL_PARTS / "nl428_credits_line_1.yaml"
LINE_3_PART = NL_PARTS / "nl428_credits_line_3.yaml"
LINE_4_PART = NL_PARTS / "nl428_credits_line_4.yaml"
LINE_5_PART = NL_PARTS / "nl428_credits_line_5.yaml"
LINE_PART = NL_PARTS / "nl428_credits_line_6.yaml"
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
    "t1_taxable_income_line_11700_inputs.yaml",
    "t1_taxable_income_line_11700.yaml",
    "t1_taxable_income_line_12500_inputs.yaml",
    "t1_taxable_income_line_12500.yaml",
    "t1_taxable_income_line_21300_inputs.yaml",
    "t1_taxable_income_line_21300.yaml",
    "t1_taxable_income_line_23200_inputs.yaml",
    "t1_taxable_income_line_23200.yaml",
    "t1_taxable_income_line_25700.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_employment_income_line_10400_inputs.yaml",
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
# The NL428 declaration, test-local: lines 1, 3, 4, 5 and 6 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_3}
        - {LINE_4}
        - {LINE_5}
        - {LINE_6}
    """)

# (salary, line 1, line 4, line 5 rate, line 6): line 4 is line 1 less the lower bound of its
# column, and line 6 is line 4 times the rate, rounded half-up to the cent.
CASES = [
    ("70000", "69335.00", "25143.00", "0.145", "3645.74"),
    # Column 3 (15.8%) and column 4 (17.8%): the last figure of column 3, and 200,000.
    ("158866.00", "157792.00", "69410.00", "0.158", "10966.78"),
    ("200000", "198926.00", "41134.00", "0.178", "7321.85"),
]
# Rounding, half-up to the cent: 25,143.00 x 14.5% = 3,645.735 is exactly half a cent and goes up
# (above, in CASES); line 4 of 0.03 at 14.5% is 0.00435 and goes down to 0.00.
ROUNDING_CASES = [
    ("44603.06", "44192.03", "0.03", "0.145", "0.00"),
]
ALL_CASES = [*CASES, *ROUNDING_CASES]


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
    yield LINE_4_PART.name, LINE_4_PART.read_text(encoding="utf-8")
    yield LINE_5_PART.name, LINE_5_PART.read_text(encoding="utf-8")
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
    if line_1 <= D("44192"):
        return D("0"), D("0.087")
    if line_1 <= D("88382"):
        return D("44192"), D("0.145")
    if line_1 <= D("157792"):
        return D("88382"), D("0.158")
    return D("157792"), D("0.178")


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Line 1, line 4, the line 5 rate and line 6 by the form's arithmetic, in Decimal."""
    line_1 = _taxable_income(salary)
    lower, rate = _column(line_1)
    line_4 = max(line_1 - lower, D(0))
    return line_1, line_4, rate, _cent(line_4 * rate)


@pytest.mark.parametrize(("salary", "line_1", "line_4", "rate", "expected"), ALL_CASES)
def test_line_6_is_line_4_times_the_line_5_rate_rounded_half_up_to_the_cent(
    tmp_path: Path, salary: str, line_1: str, line_4: str, rate: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_6)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)
    assert str(value) == expected


@pytest.mark.parametrize("salary", ["221984.01", "300000"])
def test_line_6_is_blank_when_lines_4_and_5_are_blank_above_220910(
    tmp_path: Path, salary: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_4)).is_blank
    assert sheet.get(_kind(LINE_5)).is_blank
    assert sheet.get(_kind(LINE_6)).is_blank


def test_the_trace_names_line_4_times_the_line_5_rate_at_70000(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    line = MultipliedByRateLine(
        output=_kind(LINE_6),
        base_kind=_kind(LINE_4),
        base_value=D("25143.00"),
        rate_kind=_kind(LINE_5),
        rate_value=D("0.145"),
        rounding=_rounding().rounding,
        result=D("3645.74"),
    )
    assert line in sheet.trace


def test_the_product_reads_in_english_with_its_rate_base_and_rounding(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "70000")

    (line,) = [
        each
        for each in sheet.trace
        if isinstance(each, MultipliedByRateLine) and each.output is _kind(LINE_6)
    ]
    text = EnglishTraceRenderer().render(line)

    assert "(14.5%)" in text
    assert "(25143.00)" in text
    assert text.endswith("gives 3645.74 (rounded to the nearest cent).")


def test_the_part_is_one_untitled_multiply_by_rate_step_over_lines_4_and_5() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert "title" not in step
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "6",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"base": LINE_4, "rate": LINE_5},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_6},
    }


def test_line_6_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_6)

    assert kind is NL428_TAX_ON_EXCESS_LINE_6
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
