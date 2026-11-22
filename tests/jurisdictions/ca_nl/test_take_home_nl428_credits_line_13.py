"""NL428 (2025) line 13, line 11 multiplied by the line 12 rate, from the real parts.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): each of the four columns of lines 9 to 15
prints "Line 13: Line 11 multiplied by the percentage from line 12 =". Line 13 is line 11 times the
printed rate of the column (19.8%, 20.8%, 21.3% or 21.8%), rounded half-up to the cent by
`ca-nl/cent_rounding`: the form states no rounding rule. Line 13 is one `core/multiply_by_rate`
step with base `ca-nl/nl428_taxable_income_over_lower_bound_line_11` and rate
`ca-nl/nl428_bracket_rate_line_12`, output `ca-nl/nl428_tax_on_excess_line_13`, as line 6 is. Lines
11 and 12 are blank at or below 220,910 (lines 2 to 8 apply), so line 13 is blank there.

Figures, re-derived in `_derived` below with Decimal (not a CRA example): taxable income is the
salary less the enhanced CPP deduction (1,074.00 from $71,300 up), line 11 is that less the
column's lower bound, and line 13 is line 11 times the rate: 250,000 gives line 1 of 248,926.00,
line 11 of 28,016.00 and line 13 of 5,547.17 (the other three columns are tested in line 12's
rate lookup). A salary of 250,001.50 makes the product 5,547.465, exactly half a cent, which goes
up.

The real parts composed: Schedule 8, the T1 taxable-income parts, lines 1, 10, 11, 12 and 13. The
header, the salary input and the form declaration are test-local.
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
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import NL428_TAX_ON_EXCESS_LINE_13
from tests.federal_forms import FEDERAL_FORMS, form_part_names, form_parts
from tests.jurisdictions.ca_nl.support import (
    newfoundland_capabilities,
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_parameter_parsers,
    newfoundland_units,
)
from tests.kinds import non_negative

D = Decimal
CENT = D("0.01")
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
ROUNDING = "ca-nl/cent_rounding"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_10 = "ca-nl/nl428_bracket_lower_bound_line_10"
LINE_11 = "ca-nl/nl428_taxable_income_over_lower_bound_line_11"
LINE_12 = "ca-nl/nl428_bracket_rate_line_12"
LINE_13 = "ca-nl/nl428_tax_on_excess_line_13"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
LINE_PART = NL_PARTS / "nl428_credits_line_13.yaml"
LINE_1_PART = NL_PARTS / "nl428_credits_line_1.yaml"
LINE_10_PART = NL_PARTS / "nl428_credits_line_10.yaml"
LINE_11_PART = NL_PARTS / "nl428_credits_line_11.yaml"
LINE_12_PART = NL_PARTS / "nl428_credits_line_12.yaml"
T1_PARTS = form_part_names(
    "t1_taxable_income", "t1_employment_income", "t1_lines_copied_by_provinces"
)

HEADER = dedent("""\
    jurisdiction: CA-NL
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
# The NL428 declaration, test-local: lines 1, 10, 11, 12 and 13 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_10}
        - {LINE_11}
        - {LINE_12}
        - {LINE_13}
    """)

# (salary, line 11, line 12 rate, line 13): one salary per column, then a product of exactly half a
# cent (28,017.50 x 19.8% = 5,547.465), which rounds up.
CASES = [
    ("250000", "28016.00", "0.198", "5547.17"),
    ("250001.50", "28017.50", "0.198", "5547.47"),
]


def _federal(name: str) -> Path:
    return next(FEDERAL_FORMS.rglob(name))


def _part_files() -> Iterator[tuple[str, str]]:
    """Each part's name and text, in composition order."""
    for found in form_parts("schedule_8"):
        yield found.name, found.read_text(encoding="utf-8")
    for name in T1_PARTS:
        found = _federal(name)
        yield (
            name,
            found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
    yield LINE_10_PART.name, LINE_10_PART.read_text(encoding="utf-8")
    yield LINE_11_PART.name, LINE_11_PART.read_text(encoding="utf-8")
    yield LINE_12_PART.name, LINE_12_PART.read_text(encoding="utf-8")
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


def _cent(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def _derived(salary: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Line 11, the line 12 rate and line 13 by the form's arithmetic, in Decimal."""
    enhanced = _cent(max(min(salary, D("71300")) - D("3500"), D(0)) * D("0.01"))
    second = _cent(max(min(salary, D("81200")) - D("71300"), D(0)) * D("0.04"))
    line_1 = salary - enhanced - second
    for lower, upper, rate in (
        (D("220910"), D("282214"), D("0.198")),
        (D("282214"), D("564429"), D("0.208")),
        (D("564429"), D("1128858"), D("0.213")),
        (D("1128858"), D("1e12"), D("0.218")),
    ):
        if lower < line_1 <= upper:
            return line_1 - lower, rate, _cent((line_1 - lower) * rate)
    raise AssertionError("line 1 is not above 220,910")


@pytest.mark.parametrize(("salary", "line_11", "rate", "expected"), CASES)
def test_line_13_is_line_11_times_the_line_12_rate_rounded_half_up_to_the_cent(
    tmp_path: Path, salary: str, line_11: str, rate: str, expected: str
) -> None:
    assert _derived(D(salary)) == (D(line_11), D(rate), D(expected))
    sheet = _sheet(tmp_path, salary)

    value = sheet.get(_kind(LINE_13)).value
    assert sheet.get(_kind(LINE_11)).value == D(line_11)
    assert sheet.get(_kind(LINE_12)).value == D(rate)
    assert value == D(expected)
    assert str(value) == expected


@pytest.mark.parametrize("salary", ["20000", "200000"])
def test_line_13_is_blank_when_lines_11_and_12_are_blank_up_to_220910(
    tmp_path: Path, salary: str
) -> None:
    sheet = _sheet(tmp_path, salary)

    assert sheet.get(_kind(LINE_11)).is_blank
    assert sheet.get(_kind(LINE_12)).is_blank
    assert sheet.get(_kind(LINE_13)).is_blank


def test_the_part_is_one_untitled_multiply_by_rate_step_over_lines_11_and_12() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "reference", "unit", "params", "consumes", "blank", "produces"]
    assert step == {
        "name": "core/multiply_by_rate",
        "reference": "13",
        "unit": "ca/cad",
        "params": {"rounding": ROUNDING},
        "consumes": {"base": LINE_11, "rate": LINE_12},
        "blank": {"base": "pass_on", "rate": "pass_on"},
        "produces": {"output": LINE_13},
    }


def test_line_13_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_13)

    assert kind is NL428_TAX_ON_EXCESS_LINE_13
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
