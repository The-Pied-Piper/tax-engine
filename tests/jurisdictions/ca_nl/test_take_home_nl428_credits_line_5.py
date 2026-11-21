"""NL428 (2025) line 5, the rate of the column for lines 2 to 8, real engine.

Form text (Form NL428, CRA 5001-C, 5001-c-25e.txt): "Line 5: Rate 8.7%" in column 1, "Line 5: Rate
14.5%" in column 2, "Line 5: Rate 15.8%" in column 3 and "Line 5: Rate 17.8%" in column 4, under
"Column 1: Line 1 is $44,192 or less", "Column 2: Line 1 is more than $44,192 but not more than
$88,382", "Column 3: Line 1 is more than $88,382 but not more than $157,792" and "Column 4: Line 1
is more than $157,792 but not more than $220,910". Line 5 is the printed rate of the column that
line 1 falls in. Above 220,910 the table (`ca-nl/brackets_lines_2_to_8`, whose rates are the
printed ones) does not apply (lines 9 to 15 do), so line 5 is blank.

Line 5 is one `core/bracket_column_rate` step over line 1 with that schedule, output
`ca-nl/nl428_bracket_rate_line_5`, in the part `nl428_credits_line_5.yaml`. Line 1 is not this
ticket's: its part, `nl428_credits_line_1.yaml`, is composed as it is. The rate is a Decimal held
as printed, not rounded, and is not money, so the step has no unit.

The real parts composed: the real Schedule 8, the T1 taxable-income parts, line 1 and
`nl428_credits_line_5.yaml`. The header, the salary input and the form declaration are test-local
(Newfoundland and Labrador has no salary part), the form exporting lines 1 and 5.

Figures, computed from the engine's T1 taxable income (line 26000): salary 70,000 gives line 1 of
69,335.00 (14.5%) and 200,000 gives 198,926.00 (17.8%). Below the CPP and EI maxima the
deduction is the enhanced CPP, 1% of salary over 3,500 to the cent, so a salary of 44,603.03 gives
exactly 44,192.00. Hand figures, not a CRA example.
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
import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.registry import Namespace
from tax_engine.domain.trace import BracketColumnFigureLine, BracketOutsideRangeLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_nl.catalog import NL428_BRACKET_RATE_LINE_5
from tests.federal_forms import form_part_names, form_parts
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
CODE = JurisdictionCode("CA-NL")
FORM = "ca-nl/nl428_credits"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_5 = "ca-nl/nl428_bracket_rate_line_5"
NL_PARTS = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025"
FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"
LINE_PART = NL_PARTS / "nl428_credits_line_5.yaml"
T1_PARTS = form_part_names("t1_taxable_income", "t1_employment_income")

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
# The NL428 declaration, test-local: lines 1 and 5 are composed, so it exports those.
FORM_TEXT = dedent(f"""\
    form:
      name: {FORM}
      required: true
      exports:
        - {LINE_1}
        - {LINE_5}
    """)
LINE_1_PART = NL_PARTS / "nl428_credits_line_1.yaml"


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
            inputs_without_form(found)
            if name.endswith("_inputs.yaml")
            else found.read_text("utf-8"),
        )
    yield LINE_1_PART.name, LINE_1_PART.read_text(encoding="utf-8")
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


@pytest.mark.parametrize(
    ("salary", "expected"),
    [
        # Line 1 is 69,335.00, over 44,192 and not over 88,382: column 2.
        ("70000", "0.145"),
        # Line 1 of exactly 44,192.00 is still column 1.
        ("44603.03", "0.087"),
        # Line 1 is 88,382.01, over 88,382 and not over 157,792: column 3.
        ("89456.01", "0.158"),
    ],
)
def test_line_5_is_the_rate_of_the_column_line_1_falls_in(
    tmp_path: Path, salary: str, expected: str
) -> None:
    value = _sheet(tmp_path, salary).get(_kind(LINE_5)).value

    assert value == D(expected)
    assert isinstance(value, Decimal)


@pytest.mark.parametrize("salary", ["300000", "221984.01"])
def test_line_5_is_blank_when_line_1_is_above_220910(tmp_path: Path, salary: str) -> None:
    assert _sheet(tmp_path, salary).get(_kind(LINE_5)).is_blank


def test_the_blank_says_why_in_the_trace(tmp_path: Path) -> None:
    sheet = _sheet(tmp_path, "300000")
    line = BracketOutsideRangeLine(_kind(LINE_5), _kind(LINE_1), D("298926.00"))

    assert line in sheet.trace
    assert (
        EnglishTraceRenderer()
        .render(line)
        .endswith("(298926.00) is outside the range of the bracket table, so it is left blank.")
    )


@pytest.mark.parametrize(
    ("salary", "line_1", "expected", "percent"),
    [
        ("70000", "69335.00", "0.145", "14.5"),
        ("200000", "198926.00", "0.178", "17.8"),
    ],
)
def test_the_trace_names_the_rate_of_the_bracket_line_1_falls_in(
    tmp_path: Path, salary: str, line_1: str, expected: str, percent: str
) -> None:
    sheet = _sheet(tmp_path, salary)
    line = BracketColumnFigureLine(
        output=_kind(LINE_5),
        base=_kind(LINE_1),
        base_amount=D(line_1),
        name="rate",
        figure=D(expected),
    )

    assert line in sheet.trace
    rendered = EnglishTraceRenderer().render(line)
    assert rendered.endswith(f"falls in a bracket with the rate {percent}%.")


def test_the_part_is_one_titled_bracket_column_rate_step_over_line_1() -> None:
    part: Any = yaml.safe_load(LINE_PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    (step,) = part["capabilities"]
    assert list(step) == ["name", "title", "reference", "params", "consumes", "produces"]
    assert step == {
        "name": "core/bracket_column_rate",
        "title": "Rate",
        "reference": "5",
        "params": {"schedule": "ca-nl/brackets_lines_2_to_8"},
        "consumes": {"base": LINE_1},
        "produces": {"output": LINE_5},
    }


def test_line_5_is_a_registered_non_negative_decimal_amount_kind() -> None:
    kind = newfoundland_kinds().kind(LINE_5)

    assert kind is NL428_BRACKET_RATE_LINE_5
    assert isinstance(kind, AmountKind)
    assert kind.value_type is Decimal
    assert non_negative(kind)
